import logging
import time
import os
import warnings
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API.")
import pygame
import math
import threading
from dotenv import load_dotenv

from PyQt5.QtGui import QRegion
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsColorizeEffect

from PyQt5.QtWidgets import (
    QWidget, QLabel, QApplication, QGraphicsOpacityEffect, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QSize, QRect, pyqtSignal, QTimer, QPoint, QEvent, QPropertyAnimation
)
from PyQt5.QtGui import QMovie, QGuiApplication

from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Interface.Components.Assets.Assets import AssetManager
from AvaSphere.Matrix.Interface.Components.Position.Position import PositionManager
from AvaSphere.Matrix.Interface.Components.Tints.Tints import TintManager
from AvaSphere.Matrix.Interface.UIS.Top.tcWindow import TCWindow
from AvaSphere.Matrix.Interface.UIS.Bottom.bcWindow import BCWindow

load_dotenv()
ACTIVATE_DEMO = os.getenv("ACTIVATE_DEMO_MODE", 'False') == 'True'

GIF_STATES = {"activate", "deactivate", "offline", "recognize", "synthesize", "processing", "show-brain", "brain", "hide-brain"}

logger = logging.getLogger(__name__)

class MCWindow(QWidget):
    stateSignal          = pyqtSignal(str, int, str, str)
    animateMoveSignal    = pyqtSignal(str, int)
    directMoveSignal     = pyqtSignal(str)
    regionTouched        = pyqtSignal(int)
    buttonClicked        = pyqtSignal(int)
    fadeInSignal         = pyqtSignal()
    fadeOutSignal        = pyqtSignal()
    toggleModeSignal     = pyqtSignal()
    hideAllWindowsSignal = pyqtSignal()
    killSwitchSignal     = pyqtSignal()

    DRAG_THRESHOLD = 10
    _instance      = None
    _lock          = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MCWindow, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        super().__init__()
        if hasattr(self, "initialized"):
            return

        self.emotionOverride = True
        self.emotion = "Blue" # States can be: Ecstatic, Excited, Happy, Pissed Off, Angry, Frustrated, Annoyed, Neutral, Lonely 

        self._initComponents()

        self.initialized = True

    def _initComponents(self):
        self.demoModeActivated = ACTIVATE_DEMO
        self.attributes        = Attributes()
        self.tintManager       = TintManager()

        self._initWindow()

        self._initSubWindows()
        self._initSubWindowTimer()

        self._initSignals()
        self._initMixer()

        # prepare audio
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        self.channels   = [pygame.mixer.Channel(i) for i in range(pygame.mixer.get_num_channels())]
        self.touchTimes = {k:0 for k in AssetManager.getRegionKeys()}

        # click state
        self.clickCounter = 0
        self.soundEffect  = False
        self.isDragging   = False
        self.oldPos       = QPoint()

        # reset-multi-click timer
        self.resetTimer = QTimer(self)
        self.resetTimer.setInterval(30000)
        self.resetTimer.timeout.connect(self.resetClickCounter)
        self.currentState   = None
        self.currentEmotion = None
        self.lastStyledUser = None
        self._setupEmotionUpdater()

    def _initSubWindowTimer(self):
        self.refreshTimer = QTimer(self)
        self.refreshTimer.setInterval(1000)
        self.refreshTimer.timeout.connect(self.checkAndRefreshStyles)
        self.refreshTimer.start()

    def _initSubWindows(self):
        # Only keep tcWindow and bcWindow
        self.tcWindow = TCWindow()
        self.bcWindow = BCWindow()

    def _getAllSubWindows(self):
        return [
            self.tcWindow, self.bcWindow
        ]

    def getEmotionalState(self):
        if self.emotionOverride:
            return self.emotion
        return "Neutral" #self.attributes.getEmotions()

    def _setupEmotionUpdater(self):
        self.emotionTimer = QTimer(self)
        self.emotionTimer.setInterval(300)
        self.emotionTimer.timeout.connect(self._refreshEmotionTint)
        self.emotionTimer.start()

    def _refreshEmotionTint(self):
        if self.currentState in GIF_STATES:
            emo = self.getEmotionalState()
            if emo != self.currentEmotion:
                self.currentEmotion = emo
                self._applyTintEffect(emo)

    def _initWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self._setupTintEffect()
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.installEventFilter(self)
        self.label.setScaledContents(True)
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        if self.demoModeActivated:
            self.label.setGeometry(QRect(0,0,800,800))
            self.setFixedSize(QSize(800,800))
        else:
            self.label.setGeometry(QRect(0,0,600,600))
            self.setFixedSize(QSize(600,600))

        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x   = (geo.width()-self.width())//2
            y   = (geo.height()-self.height())//2
            self.move(x, y)

    def _setupTintEffect(self):
        self.tintEffect = QWidget(self.label)
        self.tintEffect.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.tintEffect.hide()

    def _initSignals(self):
        self.stateSignal.connect(self.updateState, Qt.QueuedConnection)
        self.postionManager = PositionManager(self)
        self.animateMoveSignal.connect(self.postionManager.animateMove, Qt.QueuedConnection)
        self.directMoveSignal .connect(self.postionManager.directMove,  Qt.QueuedConnection)
        self.buttonClicked.connect(self.handleButtonClicks, Qt.QueuedConnection)
        self.fadeInSignal.connect(self.fadeIn, Qt.QueuedConnection)
        self.fadeOutSignal.connect(self.fadeOut, Qt.QueuedConnection)
        self.hideAllWindowsSignal.connect(self.hideAllWindows, Qt.QueuedConnection)
        self.killSwitchSignal.connect(self.killSwitch, Qt.QueuedConnection)

    def _initMixer(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=4, buffer=512)
            except pygame.error as e:
                logger.error(f"Mixer init failed: {e}", exc_info=True)
        self.gifChannel    = pygame.mixer.Channel(0)
        self.buttonChannel = pygame.mixer.Channel(1)
        self.regionChannel = self.buttonChannel
        if not hasattr(self, 'preloadedSounds'):
            self.preloadedSounds = {}
            for key in ['online','offline','shutdown','hide','show','exit']:
                path = AssetManager.getSound(key)
                if path and os.path.exists(path):
                    try:
                        self.preloadedSounds[key] = pygame.mixer.Sound(path)
                    except Exception as e:
                        logger.error(f"Preload sound '{key}' error:", exc_info=True)

    def resetClickCounter(self):
        self.clickCounter = 0

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.label.setGeometry(0, 0, self.width(), self.height())
        if m := self.label.movie():
            m.setScaledSize(self.label.size())

        tintMaskScale = 0.88  # Pick once; always fits proportionally

        w = self.label.width()
        h = self.label.height()
        size = int(min(w, h) * tintMaskScale)
        x = (w - size) // 2
        y = (h - size) // 2
        circleRect = QRect(x, y, size, size)
        self.tintEffect.setGeometry(self.label.geometry())
        self.tintEffect.setMask(QRegion(circleRect, QRegion.Ellipse))




    def updateState(self, state, speed=100, soundEffect=None, fadeDirection=None):
        self.currentState = state
        gif = AssetManager.getGif(state)
        if gif and os.path.exists(gif):
            movie = QMovie(gif)
            movie.setSpeed(speed)
            self.label.setMovie(movie)
            movie.setScaledSize(self.label.size())
            movie.start()
            self.currentMovie = movie

            if fadeDirection == "in":
                self.fadeIn()
            elif fadeDirection == "out":
                self.fadeOut()
            if soundEffect:
                self.playSoundEffect("Gifs", soundEffect)
        else:
            logger.warning(f"GIF missing for state '{state}'")

        if state == "offline":
            time.sleep(6)
            self.killSwitch(True)

        self.show()
        if state in GIF_STATES:
            emo = self.getEmotionalState()
            self._applyTintEffect(emo)
        else:
            self.tintEffect.hide()

    def _applyTintEffect(self, emo: str):
        tint = self.tintManager.getTint(emo)
        self._targetColor = tint if isinstance(tint, tuple) else None
        self._startTintAnimation()

    def _startTintAnimation(self):
        if not hasattr(self, "_currentAlpha"):
            self._currentAlpha = 0
        self._alphaStep = 3
        if not hasattr(self, "_tintTimer"):
            self._tintTimer = QTimer(self)
            self._tintTimer.setInterval(16)
            self._tintTimer.timeout.connect(self._updateTintFrame)
        self._tintTimer.start()

    def _updateTintFrame(self):
        if self._targetColor is None:
            self._currentAlpha = max(0, self._currentAlpha - self._alphaStep)
            if self._currentAlpha <= 0:
                self._tintTimer.stop()
                self.tintEffect.hide()
                return
            rgba = f"rgba(0,0,0,{self._currentAlpha})"
        else:
            r, g, b, targetAlpha = self._targetColor
            if self._currentAlpha < targetAlpha:
                self._currentAlpha = min(self._currentAlpha + self._alphaStep, targetAlpha)
            elif self._currentAlpha > targetAlpha:
                self._currentAlpha = max(self._currentAlpha - self._alphaStep, targetAlpha)
            else:
                self._tintTimer.stop()
            rgba = f"rgba({r},{g},{b},{self._currentAlpha})"
        self.tintEffect.setStyleSheet(f"background-color: {rgba};")
        self.tintEffect.show()
        self.tintEffect.raise_()

    def fadeEffect(self, dur, start, end):
        QTimer.singleShot(0, lambda: self.performFadeEffect(dur, start, end))

    def performFadeEffect(self, dur, start, end):
        eff = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(dur)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.start()

    def fadeIn(self):  self.fadeEffect(3000, 0.0, 1.0)
    def fadeOut(self): self.fadeEffect(3000, 1.0, 0.0)

    def eventFilter(self, source, event):
        if source is self.label and event.type() in (
            QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseMove
        ):
            return False
        return super().eventFilter(source, event)

    def mousePressEvent(self, event):
        self.postionManager.storeCurrent()
        self.isDragging = False
        self.oldPos     = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        if abs(delta.x())>self.DRAG_THRESHOLD or abs(delta.y())>self.DRAG_THRESHOLD:
            self.isDragging = True
            self.move(self.x()+delta.x(), self.y()+delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if self.isDragging:
            self.isDragging = False
        else:
            self.handleTouch(event)

    def activateKillSwitch(self):
        return os.getenv("ACTIVATE_KILL_SWITCH", 'False') =='True'

    def handleTouch(self, event):
        cx, cy = self.label.width()/2, self.label.height()/2
        x, y   = event.pos().x(), event.pos().y()
        dist   = math.hypot(x-cx, y-cy)
        r = min(cx, cy)
        th = {1:0.3*r, 2:0.5*r, 3:0.7*r}
        if self.activateKillSwitch() and dist<=th[3]:
            self.handleCenterClicks(3)
            return
        for idx, rad in th.items():
            if dist<=rad:
                self.regionTouched.emit(idx)
                return
        angle = (math.degrees(math.atan2(y-cy, x-cx))+360)%360
        btn   = self._getButtonForAngle(angle)
        self.handleButtonClicks(btn)

    def _getButtonForAngle(self, angle):
        m = [
            ((202.5,247.5),"top-left"),((247.5,292.5),"top-center"),
            ((292.5,337.5),"top-right"),((22.5,67.5),"bottom-right"),
            ((67.5,112.5),"bottom-center"),((112.5,157.5),"bottom-left"),
            ((157.5,202.5),"center-left"),((337.5,22.5),"center-right"),
        ]
        for (low,hi),key in m:
            if low<=hi:
                if low<=angle<hi: return key
            else:
                if angle>=low or angle<hi: return key
        return "Invalid"

    def handleButtonClicks(self, button):
        self.toggleWindow(button.lower())

    def handleCenterClicks(self, region):
        if self.activateKillSwitch():
            self.playSoundEffect("Button","exit")
            self.clickCounter+=1
            if self.clickCounter==2: self.resetTimer.start()
            if self.clickCounter>=3:
                self.resetTimer.stop()
                self.killSwitch(True ,3000)
        else:
            self.playSoundEffect("region", None, region)

    def toggleWindow(self, key):
        wmap = {
            'top-center':   self.tcWindow,
            'bottom-center':self.bcWindow,
        }
        targ = wmap.get(key)
        if not targ: return
        show = not targ.isVisible()
        self.playSoundEffect("Button","show" if show else "hide")
        show and targ.show() or targ.hide()

    def appear(self):      self.fadeInSignal.emit()
    def disappear(self):   self.fadeOutSignal.emit()

    def animatedMoveTo(self, direction):
        self.animateMoveSignal.emit(direction, 2000)

    def directlyMoveTo(self, direction):
        self.directMoveSignal.emit(direction)

    def previousMove(self, animated=False):
        self.postionManager.movePrevious(animated=animated)

    def getCurrentPosition(self):
        return self.postionManager.getCurrentPosition()

    def playSoundEffect(self, component, soundEffect=None, region=None):
        path = AssetManager.getSound(soundEffect)
        if not path:
            logger.warning(f"Sound effect missing: {soundEffect}")
            return

        snd = pygame.mixer.Sound(path)
        if component == "Gifs":
            self.gifChannel.play(snd)
        elif component == "region":
            self.regionChannel.play(snd)
        elif component == "Button":
            snd.set_volume(0.5)
            self.buttonChannel.play(snd)
        else:
            snd.set_volume(0.5)
            self.buttonChannel.play(snd)

    def effectFinished(self):
        self.soundEffect = False

    def setTCMode(self, mode):
        self.tcWindow.setMode(mode)

    def showTCWindow(self):
        self.tcWindow.show()

    def hideTCWindow(self):
        self.tcWindow.hide()

    def connectKeyboard(self):
        return self.tcWindow.connectKeyboard()

    def connectVoice(self, content):
        self.tcWindow.voiceTextSubmitted.emit(content)

    def connectOutput(self, content):
        self.tcWindow.outputTextSubmitted.emit(content)

    def connectDisplay(self, content):
        # For compatibility, stub or map to tcWindow if needed, else pass
        pass

    def connectUpdateState(self, state, speed=100, soundEffect=None, fadeDirection=None):
        self.stateSignal.emit(state, speed, soundEffect, fadeDirection)

    def connectRegion(self, callback):
        self.regionTouched.connect(callback)

    def connectSwitch(self, mode):
        self.toggleModeSignal.connect(mode, Qt.QueuedConnection)

    def connectHideAllWindows(self):
        self.hideAllWindowsSignal.emit()

    def connectKillSwitch(self):
        self.killSwitchSignal.emit()

    def hideAllWindows(self):
        for w in self._getAllSubWindows():
            if w.isVisible():
                try: w.hide()
                except Exception as e: 
                    logger.error(f"Error hiding {w}", exc_info=True)

    def killSwitch(self, killMCWindow=False, time=3000):
        for w in self._getAllSubWindows():
            if w.isVisible():
                action = getattr(w, 'killSwitch', w.hide)
                action()
        if killMCWindow:
            self.resetTimer.stop()
            if hasattr(self, 'currentMovie'):
                self.currentMovie.stop()
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                for ch in self.channels:
                    ch.stop()
            self.setWindowOpacity(0)
            super().hide()
            QTimer.singleShot(time, QApplication.quit)

    def checkAndRefreshStyles(self):
        from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Profile.UserProfile import UserProfile
        up = UserProfile()
        try:
            currentUser = up.identity.loadCurrentUserName()
        except Exception as e:
            logger.error("Failed to load current user", exc_info=True)
            return
        if currentUser != self.lastStyledUser:
            self.lastStyledUser = currentUser
            QTimer.singleShot(0, self._refreshSubWindowStyles)

    def _refreshSubWindowStyles(self):
        for w in self._getAllSubWindows():
            if hasattr(w, "refreshStyles"):
                w.refreshStyles()
