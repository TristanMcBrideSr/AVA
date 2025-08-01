
import inspect
import logging
import os
import threading
from dotenv import load_dotenv
from HoloAI import HoloLink

from AvaSphere.Echo.Echo import Echo

logger = logging.getLogger(__name__)


class Mode:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Mode, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.holoLink = HoloLink()
        self.echo          = Echo()
        self.actionMap = {
            "set-voice-mode":    self._setVoiceMode,
            "set-keyboard-mode": self._setKeyboardMode,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Manage modes."
        }

    def modeSkill(self, action: str, *args):
        self.holoLink.calledActions(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.holoLink.executeSkill('system', name, self.actionMap, action, *args)

    def _setVoiceMode(self) -> str:
        self.echo.getEchoAttributes("switchMode", "voice")
        return "Now using voice mode."

    def _setKeyboardMode(self) -> str:
        self.echo.getEchoAttributes("switchMode", "keyboard")
        return "Now using keyboard mode."