
import os
import threading
from pathlib import Path
from dotenv import load_dotenv
import logging
from PyQt5.QtCore import QTimer

from AvaSphere.Echo.Components.Gen.EchoGen import Gen
from AvaSphere.Echo.Components.Rec.EchoRec import Rec
from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Interface.Interface import Interface


load_dotenv()
logger = logging.getLogger(__name__)


class Echo:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        super().__init__()
        if hasattr(self, "initialized"):
            return

        self._initComponents()
        
        self.initialized = True

    def _initComponents(self):
        self.interface           = Interface()
        self.attributes          = Attributes()
        self.db                  = Database()
        self.backgroundInputLock = threading.Lock()
        self._initVariables()
        self._initFiles()
        self.mode                = self.loadMode()
        self.interface.setIOMode(self.mode)
        self.rec                 = Rec(self)
        self.gen                 = Gen(self)
        QTimer.singleShot(0, self._initIOWindow)

    def _initIOWindow(self) -> None:
        mode = os.getenv("IO_STARTUP_MODE", "Both").lower()
        actions = {
            ("keyboard", "keyboard"): lambda: QTimer.singleShot(3000, self.interface.showIOWindow),
            ("voice", "voice"): lambda: QTimer.singleShot(3000, self.interface.showIOWindow),
        }
        action = actions.get((mode, self.mode))
        if action:
            action()
        elif mode == "both":
            QTimer.singleShot(3000, self.interface.showIOWindow)
        # If mode is "none" or not matched, do nothing (pass)

    def _initVariables(self):
        self.storedInput, self.storedOutput, self.backgroundInput, self.fileName = "", [], None, None
        self.speaking, self.paused, self.touched                                 = False, False, False
        self.deactivating, self.switchingModes, self.adjustCurrentAttributes     = False, False, False

    def _initFiles(self):
        self.echoModeDir = self.db.echoModeDir
        self.modeFile    = self.getDir(self.echoModeDir, "Mode.txt")
        self.defaultMode = "keyboard"
        if not os.path.exists(self.modeFile):
            with open(self.modeFile, "w") as file:
                file.write(self.defaultMode)

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def processState(self, ctx=None):
        return self.rec.processState(ctx)

    def recognize(self):
        return self.rec.recognize()

    def keyboard(self):
        return self.rec.keyboard()

    def synthesize(self, ctx):
        return self.gen.synthesize(ctx)

    @property
    def printing(self):
        return self.interface.printing

    @property
    def getName(self):
        defaultAssistantName = os.getenv("ASSISTANT_NAME", "AVA")
        return self.attributes.getCurrentAttribute("Ava", "Name", defaultAssistantName).lower()

    @property
    def getGender(self):
        defaultAssistantGender = os.getenv("ASSISTANT_GENDER", "Female")
        return self.attributes.getCurrentAttribute("Ava", "Gender", defaultAssistantGender).lower()

    @property
    def getUserName(self):
        defaultUserName = os.getenv("DEFAULT_USER_NAME", "User")
        return self.attributes.getCurrentAttribute("User", "Name", defaultUserName)

    def loadMode(self):
        try:
            with open(self.modeFile, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return self.defaultMode

    def switchMode(self, mode=None):
        if self.switchingModes:
            return
        
        self.switchingModes = True
        targetMode = mode if mode else ("voice" if self.mode == "keyboard" else "keyboard")
        self.mode  = targetMode
        self.interface.setIOMode(targetMode)
        with open(self.modeFile, "w") as file:
            file.write(targetMode)
        self.switchingModes = False

    def getEchoAttributes(self, attName, *args, **kwargs):
        echoMap = {
            "switchMode":      self.switchMode,
            "resetAttributes": self.gen.resetAttributes,
            "setVoice":        self.gen.setVoice,
            "resetVoice":      self.gen.resetVoice,
            "setVolume":       self.gen.setVolume,
            "resetVolume":     self.gen.resetVolume,
            "setRate":         self.gen.setRate,
            "resetPitch":      self.gen.resetPitch,
            "setPitch":        self.gen.setPitch,
            "resetRate":       self.gen.resetRate,
        }
        att = echoMap.get(attName)
        if att:
            return att(*args, **kwargs)
