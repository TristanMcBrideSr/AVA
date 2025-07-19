
import sys
import threading
import time
import random
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QObject, QTimer
from AvaSphere.Matrix.Interface.UIS.MCWindow import MCWindow

class Interface(QObject):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Interface, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(self, 'initialized'):
            self._initComponents()
            self.initialized = True

    def _initComponents(self):
        self.mcWindow = MCWindow()
        self.mcWindow.show()
        self.showingBrain = False
        self.playing = False
        self.getPosition = None
        self.standingby = False
        self.inactivityTimer = QTimer()
        self.inactivityTimer.setInterval(180000)  # 3 minutes
        self.inactivityTimer.timeout.connect(self.standby)

    def startTimer(self):
        self.standingby = False
        self.inactivityTimer.start()

    def stopTimer(self):
        self.standingby = True
        self.inactivityTimer.stop()

    def restartTimer(self):
        self.standingby = False
        self.inactivityTimer.start()

    @property
    def printing(self):
        return self.mcWindow.tcWindow.printing

    def standby(self):
        if self.standingby:
            return
        self.stopTimer()
        self.disappear()

    def activation(self):
        time.sleep(1)
        self.mcWindow.connectUpdateState("activate", speed=80, fadeDirection="in")
        # time.sleep(3)
        # self.mcWindow.connectUpdateState("activate", speed=80) #, soundEffect="online")
        # time.sleep(9)

    def deactivation(self):
        # normal speed = 150
        self.mcWindow.connectUpdateState("deactivate", speed=80) #, soundEffect="offline")
        time.sleep(9)
        self.mcWindow.connectUpdateState("offline", fadeDirection="out")

    def synthesize(self):
        state = "brain" if self.showingBrain else "synthesize"
        self.mcWindow.connectUpdateState(state, speed=250 if self.showingBrain else 150)

    def processing(self):
        state = "brain" if self.showingBrain else "processing"
        self.mcWindow.connectUpdateState(state, speed=500 if self.showingBrain else 250)

    def recognize(self):
        state = "brain" if self.showingBrain else "recognize"
        self.mcWindow.connectUpdateState(state, speed=80 if self.showingBrain else 80)

    def appear(self):
        self.mcWindow.appear()

    def disappear(self):
        self.mcWindow.disappear()

    def hideBrain(self):
        if self.playing:
            return
        self.showingBrain = False
        self.mcWindow.connectUpdateState("hide-brain", speed=100)
        time.sleep(3)
        self.mcWindow.connectUpdateState("recognize", speed=100)
        time.sleep(1)

    def showBrain(self):
        if self.playing:
            return
        self.showingBrain = True
        self.mcWindow.connectUpdateState("show-brain", speed=100)
        time.sleep(3)
        self.mcWindow.connectUpdateState("brain", speed=40)
        time.sleep(1)

    def getInterfaceSequence(self, sequence):
        sequence = sequence.lower()
        sequenceMap = {
            "activation": self.activation, "deactivation": self.deactivation,
            "hidebrain": self.hideBrain, "showbrain": self.showBrain,
            "synthesize": self.synthesize, "processing": self.processing, "recognize": self.recognize,
            "appear": self.appear, "disappear": self.disappear,
             
            "show-input-output": self.mcWindow.showTCWindow,
            "hide-input-output": self.mcWindow.hideTCWindow,

            "input-output": lambda: self.mcWindow.toggleWindow("top-center"),
            "settings": lambda: self.mcWindow.toggleWindow("bottom-center"),
            
            # "start-hide/seek": self.startHideAndSeek,
            # "stop-hide/seek": self.stopHideAndSeek,
            # "current-position": self.mcWindow.getCurrentPosition,

            # "quotes": lambda: self.mcWindow.toggleWindow("top-left"),
            # "thought-process": lambda: self.mcWindow.toggleWindow("top-right"),

            # "user-profiles": lambda: self.mcWindow.toggleWindow("center-left"),
            # "self-profile": lambda: self.mcWindow.toggleWindow("center-right"),

            # "info-1": lambda: self.mcWindow.toggleWindow("bottom-left"),
            # "info-2": lambda: self.mcWindow.toggleWindow("bottom-right"),
        }
        return sequenceMap.get(sequence, lambda: None)()

    def directlyMoveTo(self, direction: str):
        self.mcWindow.directlyMoveTo(direction)

    def animatedMoveTo(self, direction: str):
        self.mcWindow.animatedMoveTo(direction)

    def connectKeyboard(self):
        return self.mcWindow.connectKeyboard()

    def connectVoice(self, content):
        self.mcWindow.connectVoice(content)

    def connectOutput(self, content):
        self.mcWindow.connectOutput(content)

    def connectDisplay(self, content):
        return self.mcWindow.connectDisplay(content)

    def connectSwitch(self, mode):
        self.mcWindow.connectSwitch(mode)

    def connectRegion(self, region):
        self.mcWindow.connectRegion(region)

    def setIOMode(self, mode):
        self.mcWindow.setTCMode(mode)

    def showIOWindow(self):
        self.mcWindow.showTCWindow()

    def hideIOWindow(self):
        self.mcWindow.hideTCWindow()

    def connectCenterClicks(self, callback):
        self.mcWindow.regionTouched.connect(callback)

    def handleCenterClicks(self, region):
        self.mcWindow.handleCenterClicks(region)
