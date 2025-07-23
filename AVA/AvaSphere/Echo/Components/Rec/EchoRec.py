
import logging
import os
import time
import re
import audioop
import random
import ctypes
import winsound
from PyQt5.QtCore import QTimer
from requests.exceptions import ConnectionError, Timeout
from difflib import SequenceMatcher
from dotenv import load_dotenv
#from faster_whisper import WhisperModel
import tempfile
import speech_recognition as sr
from playsound import playsound
import simpleaudio
import pygame
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

DEFAULT_STANDBY: list[str] = [
    "Standby", "Stand by", "No thanks",
    "Ok thank you", "Ok thanks", "Thats enough"
]

DEFAULT_DEACTIVATION: list[str] = [
    "Deactivate", "Shutdown"
]

DEACTIVATION_PROTOCOLS: dict[str, tuple[str, str, str, str]] = {
    "shutdown":   ("Shutdown Protocol", "Starting", "Complete", "Canceled"),
    "deactivate": ("Deactivation Protocol", "Starting", "Complete", "Canceled")
}

CONFIRM_COMMANDS: set[str] = {
    "confirm", "yes", "proceed", "do it", "okay", "sure", "affirmative", "continue"
}

CANCEL_COMMANDS: set[str] = {
    "cancel", "no", "abort", "stop", "nevermind", "never mind", "decline", "not now"
}

SPEECH_REPLACEMENTS: dict[str, str] = {
    "junior": "jr", "elisa": "eleasa", "alisa": "eleasa", "eliza": "eleasa",
    "pops": "poppie", "gramps": "poppie", "granny": "grammie", "grammy": "grammie",
    "aspen": "espn", "espen": "espn", "shut down": "shutdown",
    "fuc": "fuck", "fuckkk": "fuck", "fuckk": "fuck", "fuckkker": "fucker",
    "fuckker": "fucker", "fuckkking": "fucking", "fuckking": "fucking", "motherfuker": "motherfucker",
    "bich": "bitch", "okay": "ok", "momma": "mama", "brody": "brodie",
    "talk to you": "talk to", "talked": "talk", "civil": "sybil", "sibyl": "sybil",
    "cible": "sybil", "symbol": "sybil", "sebel": "sybil", "sebo": "sybil",
    "sibore": "sybil", "sible": "sybil", "a i": "ai", "you're": "your",    
    "girl": "gal", "deact": "deactivate", "de": "deactivate",
}


WHISPER_SIZES: dict[str, str] = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "largeV2": "large-v2",
    "largeV3": "large-v3"
}

load_dotenv()
logger = logging.getLogger(__name__)

class Rec:
    def __init__(self, parent):
        self._initComponents(parent)

    def _initComponents(self, parent):
        self.parent            = parent
        self.recognizer        = sr.Recognizer()
        self.useProcessFalback = False
        self.useBiometrics     = False
        self.timeOut           = 10  # seconds
        # if self.useProcessFalback:
        #     self.whisper    = WhisperModel(
        #         whisperSize = WHISPER_SIZES["small"],
        #         device      = "cpu",
        #         computeType = "int8",
        #         cpuThreads  = max(1, os.cpu_count() // 2), #THREADS,
        #         numWorkers  = max(1, os.cpu_count() // 2), #WORKERS,
        #     )
        self.inputDir = self.parent.db.echoInputDir
        self.fileName = self.parent.getDir(self.inputDir, "capturedVoice.wav")
        self._initMixer()
        self._initSounds()

    def _initMixer(self) -> None:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                return
        if not hasattr(self, "listeningChannel"):
            self.listeningChannel = pygame.mixer.Channel(4)

    def _initSounds(self) -> None:
        self.soundChoice = 4
        try:
            base = self.parent.db.echoSoundDir
            self.sound1 = self.parent.getDir(base, "Listening 1.wav")
            self.sound2 = self.parent.getDir(base, "Listening 1.wav")
            self.sound3 = self.parent.getDir(base, "Listening 1.wav")
            self.sound4 = self.parent.getDir(base, "Listening 1.wav")
        except Exception as e:
            logger.error(f"Sound initialization error:", exc_info=True)
            self.sound1 = self.sound2 = self.sound3 = self.sound4 = None
        

    def processState(self, ctx: str = None) -> bool:
        if ctx:
            if self.processStandby(ctx):
                return True
            if self.processDeactivation(ctx):
                return True
            return False
        else:
            return self.processActivation()

    def processActivation(self) -> bool:
        if self.parent.mode == "keyboard":
            ctx = self.keyboardInput()
            return ctx if ctx else False
        ctx = self.inputAudio(withSound=False)
        if ctx and self.parent.getName in ctx:
            ctx = ctx.replace(self.parent.getName, "").strip()
            return ctx
        return False

    def processStandby(self, ctx: str) -> bool:
        standbyList = [word.strip().lower() for word in os.getenv("STANDBY", DEFAULT_STANDBY).split(",")]
        return ctx.strip() in standbyList

    def processDeactivation(self, ctx: str) -> bool:
        deactivationList = [word.strip().lower() for word in os.getenv("DEACTIVATION", DEFAULT_DEACTIVATION).split(",")]
        for word in deactivationList:
            if ctx.strip() == word:
                self.parent.deactivating = True

        protocol = None
        userName = self.parent.getUserName
        if ctx in deactivationList:
            protocol = DEACTIVATION_PROTOCOLS["deactivate"]

        if protocol:
            confirmation = self.inputAudio(withSound=True)
            if confirmation in CONFIRM_COMMANDS:
                self.parent.deactivating = True
                self.parent.synthesize(f"{protocol[1]} {protocol[0]}.")
                time.sleep(4)
                self.parent.synthesize(f"{protocol[0]} Is Now {protocol[2]}...")
                time.sleep(2)
                self.parent.synthesize(self._goodbyePhrases(userName))
                time.sleep(8)
                self.parent.interface.getInterfaceSequence("Deactivation")
                return True
            elif confirmation in CANCEL_COMMANDS:
                self.parent.synthesize(self._cancelPhrases(userName, protocol))
                time.sleep(4)
                self.parent.deactivating = False
                return False
        return False

    def recognize(self) -> str:
        if self.parent.deactivating:
            return None
        if not self.parent.speaking:
            ctx = self.inputAudio(withSound=True)
            return ctx
        return None

    def inputAudio(self, withSound: bool = False) -> str:
        if self.parent.mode == "keyboard":
            return self.keyboardInput()

        if not self.parent.printing:
            audio = self._captureAudio(selfSpeech=False, withSound=withSound)
            if not audio:
                return None
            try:
                ctx = self._processAudio(audio)
                ## KEEP THIS FOR FUTURE USE
                # if self.useBiometrics and self.parent.getSelfName in ctx:
                #     self.parent.biometrics.process("audio", audio)
                self._recognizedText(self._transcribeContext(ctx))
                print(f"Recognized: {ctx}")
                return ctx
            except Exception as e:
                logger.error(f"Audio Processing error:", exc_info=True)
                return None

    def ambientAudio(self) -> str:
        if self.parent.mode == "keyboard":
            return self.keyboardInput()

        audio = self._captureAudio(selfSpeech=True)
        if not audio:
            return None
        try:
            ctx = self._processAudio(audio)
            # if not ctx or self.ignoreInput(ctx):
            #     return None
            self.parent.storedInput = self.parent.attributes.getInstructions(ctx)
            return ctx
        except Exception as e:
            logger.error(f"Audio Processing error:", exc_info=True)
            return None

    def _captureAudio(self, selfSpeech: bool = False, withSound: bool = False) -> sr.AudioData:
        condition = self.parent.speaking if selfSpeech else not self.parent.speaking and not self.parent.touched
        if condition:
            try:
                with sr.Microphone() as source:
                    if not selfSpeech:
                        self.recognizer.adjust_for_ambient_noise(source, duration=2)
                        self.parent.interface.getInterfaceSequence("Recognize")
                        self._recognizedText("Listening . . . . .")
                        if withSound:
                            self._getSound(self.soundChoice)
                            while self.isPlaying():
                                time.sleep(0.1)

                    if selfSpeech:
                        systemVolume = self._getSystemVolume()
                        self.recognizer.energy_threshold = (
                            1.5 * (1000 + (systemVolume / 100) * (5000 - 1000))
                        )

                    try:
                        audio = self.recognizer.listen(
                            source,
                            timeout=5,
                            phrase_time_limit=10 if selfSpeech else None
                        )
                    except sr.WaitTimeoutError:
                        logger.warning("⚠️ No speech detected: timed out while waiting for phrase.")
                        return None

                    if selfSpeech:
                        audioEnergy = audioop.rms(audio.get_raw_data(), audio.sample_width)
                        if audioEnergy < self.recognizer.energy_threshold + 400:
                            return None

                    if not selfSpeech:
                        self.parent.interface.getInterfaceSequence("Processing")
                        self._recognizedText("Processing . . . . .")

                    return audio

            except Exception as e:
                logger.error(f"Microphone error:", exc_info=True)
        return None

    def _processAudio(self, audio: sr.AudioData) -> str:
        def process():
            if self.parent.touched or not audio or not isinstance(audio, sr.AudioData):
                return None
            try:
                result = self._recognizeWithGoogle(audio)
                return result
            except (sr.RequestError, ConnectionError, Timeout, sr.WaitTimeoutError, Exception):
                logger.error("Recognition Error:", exc_info=True)
                if self.useProcessFalback:
                    print("Switching to Whisper...")
                    #return self._recognizeWithWhisper(audio)
                    result = self._recognizeWithGoogle(audio)
                    return result
            return None

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(process)
            try:
                return future.result(timeout=self.timeOut)
            except FuturesTimeoutError:
                print("⚠️ Audio processing timed out.")
                logger.warning("Audio processing timed out.")
                return None

    def _recognizeWithGoogle(self, audio: sr.AudioData) -> str:
        try:
            ctx = self.recognizer.recognize_google(audio).lower()
            return self._cleanContent(ctx) if ctx else None
        except sr.UnknownValueError:
            logger.debug("Speech was unintelligible.")
            return None
        # Other exceptions will propagate for fallback logic

    def _recognizeWithWhisper(self, audio: sr.AudioData) -> str:
        tmpPath = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio.get_wav_data())
                tmpPath = tmp.name
            segments, _ = self.whisper.transcribe(tmpPath)
            ctx = " ".join(segment.text for segment in segments).strip().lower()
            return self._cleanContent(ctx) if ctx else None
        except sr.UnknownValueError:
            logger.debug("Speech was unintelligible.")
            return None
        except Exception:
            logger.error("Whisper Error:", exc_info=True)
            return None
        finally:
            if tmpPath and os.path.exists(tmpPath):
                os.remove(tmpPath)

    def keyboardInput(self) -> str:
        while self.parent.printing:
            time.sleep(0.01)
        self.parent.interface.getInterfaceSequence("Recognize")
        ctx = self.parent.interface.connectKeyboard()
        self.parent.interface.getInterfaceSequence("Processing")
        # if self.useBiometrics and self.parent.getSelfName in ctx:
        #     self.parent.biometrics.process("image")
        time.sleep(1)
        return ctx

    def _recognizedText(self, ctx: str) -> None:
        self.parent.interface.connectVoice(ctx)

    def _transcribeContext(self, ctx: str) -> str:
        if not ctx or not isinstance(ctx, str):
            return ""
        return re.sub(r"([.!?]\s*)(\w)", lambda x: x.group(1) + x.group(2).upper(), ctx.capitalize())

    def _cleanContent(self, ctx: str, applyReplacements: bool = True, removeNums: bool = False) -> str:
        if not ctx or not isinstance(ctx, str):
            return ""
        ctx = ctx.replace("\n", " ").replace("\n\n", " ")
        ctx = re.sub(r"[^\w\s]", "", ctx).lower().strip()
        if applyReplacements:
            for word, rep in SPEECH_REPLACEMENTS.items():
                ctx = re.sub(rf"\b{re.escape(word)}\b", rep, ctx, flags=re.IGNORECASE)
        if removeNums:
            ctx = re.sub(r"\d+", "", ctx)
        return ctx

    # def _getSound(self, key: int) -> None:
    #     try:
    #         # base = self.parent.db.echoSoundDir
    #         soundDict = {
    #             1: lambda: winsound.Beep(350, 500),
    #             2: lambda: winsound.PlaySound(self.sound1, winsound.SND_FILENAME),
    #             3: lambda: winsound.PlaySound(self.sound2, winsound.SND_FILENAME),
    #             4: lambda: winsound.PlaySound(self.sound3, winsound.SND_FILENAME),
    #             5: lambda: winsound.PlaySound(self.sound4, winsound.SND_FILENAME),
    #         }
    #         if key in soundDict:
    #             soundDict[key]()
    #     except Exception as e:
    #         logger.error(f"Sound error:", exc_info=True)
    
    def _getSound(self, key: int) -> None:
        try:
            soundDict = {
                1: lambda: self.listeningChannel.play(pygame.mixer.Sound(self.sound1)),
                2: lambda: self.listeningChannel.play(pygame.mixer.Sound(self.sound2)),
                3: lambda: self.listeningChannel.play(pygame.mixer.Sound(self.sound2)),
                4: lambda: self.listeningChannel.play(pygame.mixer.Sound(self.sound4)),
            }
            if key in soundDict:
                soundDict[key]()
        except Exception as e:
            logger.error(f"Sound error:", exc_info=True)

    def isPlaying(self) -> bool:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.listeningChannel = pygame.mixer.Channel(4)
            except pygame.error as e:
                logger.error(f"Failed to initialize the mixer:", exc_info=True)
                return False
        return self.listeningChannel.get_busy()

    def _cancelPhrases(self, userName: str, proto: tuple[str, str, str, str]) -> str:
        phrases = [
            f"Oh brilliant, {userName} - say nothing and expect magic. {proto[0]} canceled.",
            f"Well, since you've turned into a statue, {proto[0]} is canceled. Cheers, {userName}.",
            f"That awkward silence? Yeah, that cost you. {proto[0]} is off, {userName}.",
            f"Guess we're playing the quiet game - fine, {proto[0]} is done. Happy now, {userName}?",
            f"Since you couldn't be bothered to decide, I've gone ahead and canceled {proto[0]}. You're welcome, {userName}.",
            f"No confirmation? No cancellation? No problem - I'll just cancel {proto[0]} myself. Lazy genius, {userName}.",
            f"Apparently, doing nothing is your strategy. So I've canceled {proto[0]}, {userName}. Top-tier effort.",
            f"The timer waited. I waited. You... didn't. {proto[0]} is canceled. Stunning performance, {userName}.",
            f"Radio silence it is, then. {proto[0]} has been binned. As you were, {userName}.",
            f"Right, no input detected. Must be a new kind of confirmation. Anyway, {proto[0]} is canceled, {userName}.",
            f"Timer ran out, patience ran out, and now {proto[0]} is out. Well done, {userName}."
        ]
        return random.choice(phrases)

    def _goodbyePhrases(self, userName: str) -> str:
        phrases = [
            f"Goodbye {userName}... try not to get lost in your own brilliance.",
            f"Take care, {userName}. Or don't. You do you.",
            f"See you later, {userName}. Assuming you survive your own decisions.",
            f"Farewell for now, {userName}. I'll try to contain my excitement.",
            f"Until next time, {userName} - because apparently, this wasn't enough.",
            f"Stay safe, {userName}. Though statistically speaking... questionable.",
            f"Catch you later, {userName}. I'll be here. Not by choice, mind you.",
            f"Peace out, {userName}. May your Wi-Fi be strong and your coffee stronger.",
            f"Have a good one, {userName} - whatever that even means anymore.",
            f"Be well, {userName}. Or at least don't make headlines.",
            f"Later {userName}, it's been real... tragically.",
            f"Signing off, {userName}. Don't do anything I would.",
            f"Adieu {userName}, until we meet again - because fate clearly has a sense of humor.",
            f"May your journey be smooth, {userName} - unlike your last attempt at multitasking.",
            f"See you in the stars, {userName}. Or at the very least, back here pretending like you didn't forget something."
        ]
        return random.choice(phrases)
