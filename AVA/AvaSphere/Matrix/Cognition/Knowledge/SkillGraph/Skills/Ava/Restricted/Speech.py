
import threading
import os
import logging
import inspect
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from dotenv import load_dotenv
from AvaSphere.Echo.Echo import Echo

from HoloAI import HoloLink

logger = logging.getLogger(__name__)


class Speech:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Speech, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.holoLink = HoloLink()
        self.echo          = Echo()
        self.devices       = AudioUtilities.GetSpeakers()
        self.audioControl  = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume        = cast(self.audioControl, POINTER(IAudioEndpointVolume))
        self.actionMap = {
            # "increase-speaking-volume": self._increaseSpeechVolume,
            # "decrease-speaking-volume": self._decreaseSpeechVolume,
            # "toggle-mute":              self._toggleSpeechVolume,
            # "get-speaking-volume":      self._getSpeechVolume,
            # "set-speaking-volume":      self._setSpeechVolume,

            # "increase-speaking-rate":   self._increaseSpeakingRate,
            # "decrease-speaking-rate":   self._decreaseSpeakingRate,
            # "normal-speaking-rate":     self._resetSpeakingRate,
            "use-male-voice":           self._useMaleVoice,
            "use-female-voice":         self._useFemaleVoice,
            "reset-voice":              self._resetVoice,
            "reset-attributes":         self._resetAtts,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Manage speech."
        }

    def speechSkill(self, action: str, *args):
        self.holoLink.calledActions(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.holoLink.executeSkill('system', name, self.actionMap, action, *args)

    # ────────────────────── Volume Functions ──────────────────────
    def _increaseSpeechVolume(self) -> str:
        return self._adjustSpeechVolume(delta=0.1, direction="Increased")

    def _decreaseSpeechVolume(self) -> str:
        return self._adjustSpeechVolume(delta=-0.1, direction="Decreased")

    def _adjustSpeechVolume(self, delta: float, direction: str) -> str:
        current = self.volume.GetMasterVolumeLevelScalar()
        new = max(0.0, min(current + delta, 1.0))
        self.volume.SetMasterVolumeLevelScalar(new, None)
        return f"{direction} my speech volume to {new * 100:.0f}%."

    def _toggleSpeechVolume(self) -> str:
        isMuted = self.volume.GetMute()
        self.volume.SetMute(not isMuted, None)
        return "Unmuted voice." if isMuted else "Muted voice."

    def _getSpeechVolume(self) -> str:
        current = self.volume.GetMasterVolumeLevelScalar()
        return f"Current speech volume is at {current * 100:.0f}%."

    def _setSpeechVolume(self, volume: int) -> str:
        try:
            if isinstance(volume, float):
                volume = int(volume)
            if not isinstance(volume, int) or not (0 <= volume <= 100):
                raise ValueError(f"Volume must be an integer between 0 and 100. You provided: {volume}")
            self.volume.SetMasterVolumeLevelScalar(volume / 100.0, None)
            return f"Speech volume is now set to {volume}%."
        except Exception as e:
            logger.error(f"Error setting speech volume: {e}", exc_info=True)
            return f"An error occurred while trying to set my speech volume: {e}"

    # ────────────────────── Speaking Rate Functions ──────────────────────
    def _increaseSpeakingRate(self, rate: int) -> str:
        return self._adjustSpeakingRate("increaseRate", rate, "Increased")

    def _decreaseSpeakingRate(self, rate: int) -> str:
        return self._adjustSpeakingRate("decreaseRate", rate, "Decreased")

    def _adjustSpeakingRate(self, action: str, rate: int, label: str) -> str:
        updatedRate = self.echo.getEchoAttributes(action, rate)
        return f"{label} speaking rate to {int((updatedRate / 12) * 100)}%."

    def _resetSpeakingRate(self) -> str:
        self.echo.getEchoAttributes("resetRate")
        return "Reset speaking rate."

    # ────────────────────── Voice Functions ──────────────────────
    def _useMaleVoice(self) -> str:
        self.echo.getEchoAttributes("setVoice", "Male")
        return "Using a male voice."

    def _useFemaleVoice(self) -> str:
        self.echo.getEchoAttributes("setVoice", "Female")
        return "Using a female voice."

    def _resetVoice(self) -> str:
        self.echo.getEchoAttributes("resetVoice")
        return "Voice is reset."

    def _resetAtts(self) -> str:
        self.echo.getEchoAttributes("resetAttributes")
        return "All voice attributes reset."
