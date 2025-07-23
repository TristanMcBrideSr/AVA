
import os
import pyttsx4
import shutil
import textwrap
import re
import pygame
import tempfile
import time
import threading
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Gen:
    def __init__(self, parent):
        self._initComponents(parent)

    def _initComponents(self, parent):
        self.parent = parent
        self.engine = pyttsx4.init()
        self._initMixer()
        self.gender = self.parent.getGender
        self.voice  = None
        self.setVoice(self.parent.getGender)
        self.setRate()
        self.setPitch()
        self.setVolume()
               
    def _initMixer(self) -> None:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                return
        if not hasattr(self, "speechChannel"):
            self.speechChannel = pygame.mixer.Channel(2)

    @staticmethod
    def cleanText(text):
        return re.sub(r'[\*\[\]\(\)\{\}\<\>]', '', text)

    @staticmethod
    def normalizeText(text):
        replacements = {
            '“': '"', '”': '"', '‘': "'", '’': "'",
            '—': '-', '–': '-', '−': '-', '‐': '-',
            '…': '...',
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    def setVoice(self, gender=None):
        if gender is None:
            gender = self.parent.getGender
        gender = gender.lower()
        self.voice = 0 if gender == "male" else 1
        voices = self.engine.getProperty('voices')
        if len(voices) > self.voice:
            self.engine.setProperty('voice', voices[self.voice].id)
        else:
            print(f"Warning: No voice available for {self.parent.getName}")

    def setRate(self, rate=None):
        if rate is not None:
            rate = int(rate)
        else:
            rate = int(self._getSettings("RATE", 200))
        return self.engine.setProperty('rate', rate)

    def setVolume(self, volume=None):
        if volume is not None:
            volume = float(volume)
        else:
            volume = float(self._getSettings("VOLUME", 1.0))
        if volume < 0.0 or volume > 1.0:
            print(f"Warning: Volume {volume} out of range, setting to default 1.0")
            volume = 1.0
        return self.engine.setProperty('volume', volume)

    def setPitch(self, pitch=None):
        try:
            if pitch is not None:
                pitch = int(pitch)
            else:
                pitch = int(self._getSettings("PITCH", 100))
            return self.engine.setProperty('pitch', pitch)
        except Exception:
            pass

    def resetVoice(self):
        return self.setVoice()

    def resetRate(self):
        return self.setRate()

    def resetVolume(self):
        return self.setVolume()

    def resetPitch(self):
        return self.setPitch()

    def resetAttributes(self) -> None:
        self.resetPitch()
        self.resetRate()
        self.resetVoice()

    def synthesize(self, text):
        if self.parent.mode == "keyboard":
            return self.synthesizedText(text)
        self.parent.speaking = True
        self._createFile(".wav")
        cleaned = self.cleanText(text)
        self.synthesizedText(text)
        gender = self.parent.getGender
        if gender != self.gender:
            self.setVoice(gender)
        self.engine.save_to_file(cleaned, self.parent.fileName)
        self.engine.runAndWait()
        self.engine.stop()
        while not os.path.exists(self.parent.fileName):
            time.sleep(0.1)
        self.play()
        self.resetAttributes()

    def synthesizedText(self, text):
        if not self.parent.speaking:
            self.parent.interface.getInterfaceSequence("Synthesize")
        self.parent.interface.connectOutput(text)

    def play(self) -> None:
        self.parent.interface.getInterfaceSequence("Synthesize")
        pygame.mixer.music.load(self.parent.fileName)
        self.speechChannel.play(pygame.mixer.Sound(self.parent.fileName))
        while self.isPlaying():
            time.sleep(0.1)
        self.parent.speaking = False

    def isPlaying(self) -> bool:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.speechChannel = pygame.mixer.Channel(2)
            except pygame.error as e:
                logger.error(f"Failed to initialize the mixer:", exc_info=True)
                return False
        return self.speechChannel.get_busy()

    def _createFile(self, media: str) -> None:
        # changed delete=False to True to ensure the file is deleted after use
        with tempfile.NamedTemporaryFile(delete=False, suffix=media) as temp_file:
            self.parent.fileName = temp_file.name

    def _getSettings(self, key, default):
        load_dotenv(override=True)
        envVar  = f"SPEAKING_{key.upper()}"
        envSet  = os.getenv(envVar)
        return envSet or default if envSet is not None else default

