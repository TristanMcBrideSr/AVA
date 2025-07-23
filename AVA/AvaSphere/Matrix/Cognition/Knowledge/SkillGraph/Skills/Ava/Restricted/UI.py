
import inspect
import os
import time
import threading
import logging
from dotenv import load_dotenv

from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Utils.EnvUptater.EnvUpdater import EnvUpdater
from AvaSphere.Matrix.Interface.Interface import Interface


from SkillLink import SkillLink, ArgumentParser
from AvaSphere.Matrix.Cognition.Database.Database import Database

logger = logging.getLogger(__name__)

load_dotenv()


class Appearance:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Appearance, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.argParser    = ArgumentParser()
        self.skillLink = SkillLink()
        self.interface  = Interface()
        self.envUpdater = EnvUpdater()
        self.actionMap = {
            # Appearance Actions
            "appear":     self._appear,
            "disappear":  self._disappear,
            "show-brain": self._showBrain,
            "hide-brain": self._hideBrain,

            # Heart Monitor Actions
            # "show-heart": self._showHeartMonitor,
            # "hide-heart": self._hideHeartMonitor,

            # Window Actions
            "show-input-output":  self._showIOWindow,
            "hide-input-output":  self._hideIOWindow,
            "show-settings-menu": self._showSettingsWindow,
            "hide-settings-menu": self._hideSettingsWindow,
            # "show-self-profile":  self._showSProfileWindow,
            # "hide-self-profile":  self._hideSProfileWindow,
            # "show-user-profile":  self._showUProfilesWindow,
            # "hide-user-profile":  self._hideUProfilesWindow,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Manage my appearance and user interface windows."
        }

    def appearanceSkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)


    # ────────────────────── Appearance Functions ──────────────────────
    def _appear(self) -> str:
        return self._toggleAppearance("Appear", "showing yourself")

    def _disappear(self) -> str:
        return self._toggleAppearance("Disappear", "hiding yourself")

    def _showBrain(self) -> str:
        return self._toggleAppearance("ShowBrain", "showing your brain")

    def _hideBrain(self) -> str:
        return self._toggleAppearance("HideBrain", "hiding your brain")

    def _toggleAppearance(self, sequence: str, message: str) -> str:
        self.interface.getInterfaceSequence(sequence)
        return f"You are {message}"


    # ────────────────────── Heart Monitor Functions ──────────────────────
    # def _showHeartMonitor(self) -> str:
    #     return self._toggleHeartMonitor(True)

    # def _hideHeartMonitor(self) -> str:
    #     return self._toggleHeartMonitor(False)

    # def _toggleHeartMonitor(self, shouldShow: bool) -> str:
    #     currentStatus = self._currentStatus()
    #     if currentStatus == shouldShow:
    #         return f"Heart monitor is already {'showing' if shouldShow else 'hidden'}"
    #     self._updateEnvValue("True" if shouldShow else "False")
    #     return "Heart monitor is visible" if shouldShow else "Heart monitor hidden"

    # def _currentStatus(self) -> bool:
    #     load_dotenv()
    #     return os.getenv("ACTIVATE_HEART", 'False') == 'True'

    # def _updateEnvValue(self, status: str) -> None:
    #     self.envUpdater.updateEnvValue("ACTIVATE_HEART", status)


    # ────────────────────── Window Functions ──────────────────────
    def _showIOWindow(self) -> str:
        return self._toggleWindow("Input-Output", True)

    def _hideIOWindow(self) -> str:
        return self._toggleWindow("Input-Output", False)

    def _showSettingsWindow(self) -> str:
        return self._toggleWindow("Settings", True)

    def _hideSettingsWindow(self) -> str:
        return self._toggleWindow("Settings", False)

    # def _showSProfileWindow(self) -> str:
    #     return self._toggleWindow("Self-Profile", True)

    # def _hideSProfileWindow(self) -> str:
    #     return self._toggleWindow("Self-Profile", False)

    # def _showUProfilesWindow(self) -> str:
    #     return self._toggleWindow("User-Profiles", True)

    # def _hideUProfilesWindow(self) -> str:
    #     return self._toggleWindow("User-Profiles", False)

    def _toggleWindow(self, view: str, isShow: bool) -> str:
        self.interface.getInterfaceSequence(view)
        verb = "opened" if isShow else "closed"
        label = view.replace("-", " ")
        return f"{label} window {verb}"


class Move:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Move, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.argParser    = ArgumentParser()
        self.skillLink = SkillLink()
        self.interface = Interface()
        self.actionMap = {
            "current-screen-position": self._currentScreenPosition,
            "move-center":             self._moveCenter,
            "move-left":               self._moveLeft,
            "move-right":              self._moveRight,
            "move-up":                 self._moveUp,
            "move-down":               self._moveDown,
            "move-back":               self._moveBack,
            "move-top-left":           self._moveTopLeft,
            "move-top-right":          self._moveTopRight,
            "move-bottom-left":        self._moveBottomLeft,
            "move-bottom-right":       self._moveBottomRight,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Manage my movement."
        }

    def moveSkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)


    # ─────────────────────── Movement Functions ──────────────────────
    def _currentScreenPosition(self) -> str:
        return self.interface.getInterfaceSequence("Current-Location")

    def _moveCenter(self) -> str:
        return self._moveToPosition("center", "center of the screen")

    def _moveLeft(self) -> str:
        return self._moveToPosition("left", "left of the screen")

    def _moveRight(self) -> str:
        return self._moveToPosition("right", "right of the screen")

    def _moveUp(self) -> str:
        return self._moveToPosition("up", "top of the screen")

    def _moveDown(self) -> str:
        return self._moveToPosition("down", "bottom of the screen")

    def _moveBack(self) -> str:
        return self._moveToPosition("previous", "previous position")

    def _moveTopLeft(self) -> str:
        return self._moveToPosition("top-left", "top left of the screen")

    def _moveTopRight(self) -> str:
        return self._moveToPosition("top-right", "top right of the screen")

    def _moveBottomLeft(self) -> str:
        return self._moveToPosition("bottom-left", "bottom left of the screen")

    def _moveBottomRight(self) -> str:
        return self._moveToPosition("bottom-right", "bottom right of the screen")

    def _moveToPosition(self, position: str, label: str) -> str:
        self.interface.animatedMoveTo(position)
        return f"Moved to the {label}"


# class Play:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:
#                 if not cls._instance:
#                     cls._instance = super(Play, cls).__new__(cls, *args, **kwargs)
#         return cls._instance

#     def __init__(self):
#         if hasattr(self, "initialized"):
#             return
#         self._initComponents()
#         self.initialized = True

#     def _initComponents(self):
#         self.argParser    = ArgumentParser()
#         self.skillLink = SkillLink()
#         self.interface = Interface()
#         self.actionMap = {
#             "start-playing-hide/seek": self._startHideAndSeek,
#             "play-hide/seek-again":    self._playHideAndSeekAgain,
#             "stop-playing-hide/seek":  self._stopHideAndSeek,
#         }

#     def _metaData(self):
#         return {
#             "className": self.__class__.__name__,
#             "description": "Manage my play activities."
#         }

#     def playSkill(self, action: str, *args):
#         self.skillLink.argParser.printArgs(self, locals())
#         name = inspect.currentframe().f_code.co_name
#         return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)


#     # ────────────────────── Play Functions ──────────────────────
#     def _startHideAndSeek(self) -> str:
#         return self._playHideAndSeek("Playing hide and seek with the user")

#     def _playHideAndSeekAgain(self) -> str:
#         return self._playHideAndSeek("Playing hide and seek with the user again")

#     def _stopHideAndSeek(self) -> str:
#         self.interface.getInterfaceSequence("Stop-Hide/Seek")
#         return "Done playing hide and seek with the user"

#     def _playHideAndSeek(self, context: str) -> str:
#         self.interface.getInterfaceSequence("Start-Hide/Seek")
#         position = self.interface.getPosition
#         print(position)
#         return f"{context} and you are hiding at {position}, DO NOT TELL THEM YOUR POSITION, LET THEM GUESS WHERE YOU ARE AT!"
