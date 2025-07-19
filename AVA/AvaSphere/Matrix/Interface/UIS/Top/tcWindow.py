import os
import threading
import logging
from collections import deque
from dotenv import load_dotenv

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QHBoxLayout
)
from PyQt5.QtCore import (
    Qt, QTimer, QRectF, QMetaObject, pyqtSignal
)
from PyQt5.QtGui import QTextCursor, QRegion, QPainterPath

from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Interface.Components.Alignment.Alignment import Alignment
from AvaSphere.Matrix.Interface.Components.Constants.Constants import (
    FLASH_INTERVAL, FADE_IN_MS, FADE_OUT_MS, FONT_SIZE, FONT_MIN, FONT_MAX, FONT_STEP,
    TCWINDOW_POSITION, TCWINDOW_WIDTH, TCWINDOW_HEIGHT, BORDER_RADIUS,
)
from AvaSphere.Matrix.Interface.Components.Fade.Fade import Fade
from AvaSphere.Matrix.Interface.Components.Flash.Flash import Flash
from AvaSphere.Matrix.Interface.Components.Style.Style import (
    windowStyle, titleLabelStyle, titleButtonStyle, textEditStyle
)

load_dotenv()
logger = logging.getLogger(__name__)

class TCWindow(Fade, QWidget):
    keyboardTextSubmitted  = pyqtSignal(str)
    voiceTextSubmitted     = pyqtSignal(str)
    visibilityChanged      = pyqtSignal(bool)
    outputTextSubmitted    = pyqtSignal(str)
    killSwitchSignal       = pyqtSignal()

    _instance = None
    _lock     = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        if hasattr(self, 'initialized'):
            return

        self.enableFlash      = True
        self._initComponents()
        self.initialized      = True

    def _initComponents(self):
        self.attributes        = Attributes()
        self.fontSize          = FONT_SIZE
        self.fadeInDuration    = FADE_IN_MS
        self.fadeOutDuration   = FADE_OUT_MS

        # core animation state
        self.printQueue        = deque()
        self.outputBuffer      = ""
        self.outputIndex       = 0
        self.printing          = False
        self.outputPaused      = False
        self.printingToContent = False  # True=voice→content, False=output→outputText

        self.outputTimer = QTimer()
        self.outputTimer.setSingleShot(True)

        self._initWindow()
        self._initFadeEffect()
        self._initFlashEffect()

        # wire signals
        self.voiceTextSubmitted.connect(self.connectVoice)
        self.outputTextSubmitted.connect(self.connectOutput)
        self.killSwitchSignal.connect(self.killSwitch, Qt.QueuedConnection)

    @property
    def getSelfName(self):
        return self.attributes.getCurrentAttribute("Ava", "Name",os.getenv("ASSISTANT_NAME", "AVA")).upper()

    def _initWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(TCWINDOW_WIDTH, TCWINDOW_HEIGHT)
        self.setStyleSheet(windowStyle())
        self._alignWindow(TCWINDOW_POSITION)

        # rounded corners
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), BORDER_RADIUS, BORDER_RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

        # title bar
        self.titleLabel = QLabel(f" ⪡⪢⪡⪢  {self.getSelfName}  ⪡⪢⪡⪢ ")
        self.titleLabel.setFixedHeight(50)
        self.titleLabel.setStyleSheet(titleLabelStyle())
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.minimizeButton = QPushButton("-")
        self.maximizeButton = QPushButton("+")
        self.closeButton    = QPushButton("X")
        for btn in (self.minimizeButton, self.maximizeButton, self.closeButton):
            btn.setFixedSize(50, 30)
            btn.setStyleSheet(titleButtonStyle())

        self.minimizeButton.clicked.connect(self._decreaseFontSize)
        self.maximizeButton.clicked.connect(self._increaseFontSize)
        self.closeButton.clicked.connect(self._fadeOutAndHide)

        titleLayout = QHBoxLayout()
        titleLayout.addWidget(self.titleLabel, 1)
        titleLayout.addWidget(self.minimizeButton)
        titleLayout.addWidget(self.maximizeButton)
        titleLayout.addWidget(self.closeButton)

        # input & output
        self.content = QTextEdit()
        self.content.setStyleSheet(textEditStyle(10))
        self.content.keyPressEvent = self._customKeyPressEvent

        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)
        self._updateFontSize()

        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(titleLayout)
        mainLayout.addWidget(self.content)
        mainLayout.addWidget(self.outputText)
        mainLayout.setStretch(1, 2)
        mainLayout.setStretch(2, 5)

    def _initFlashEffect(self):
        self.flash = Flash(self.titleLabel, interval=FLASH_INTERVAL)
        self.flash.toggle(self.enableFlash)

    def _customKeyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            text = self.content.toPlainText().strip()
            if text:
                self.keyboardTextSubmitted.emit(text)
                self.content.clear()
        else:
            QTextEdit.keyPressEvent(self.content, event)

    def _increaseFontSize(self):
        if self.fontSize < FONT_MAX:
            self.fontSize += FONT_STEP
            self._updateFontSize()

    def _decreaseFontSize(self):
        if self.fontSize > FONT_MIN:
            self.fontSize -= FONT_STEP
            self._updateFontSize()

    def _updateFontSize(self):
        style = textEditStyle(self.fontSize)
        self.content.setStyleSheet(style)
        self.outputText.setStyleSheet(style)
        self.maximizeButton.setEnabled(self.fontSize < FONT_MAX)
        self.minimizeButton.setEnabled(self.fontSize > FONT_MIN)

    def _alignWindow(self, position):
        Alignment(self).align(position)

    # ─── connectKeyboard (unchanged) ─────────────────────────────────────
    def connectKeyboard(self):
        """
        Blocks until user presses Enter in the input box, then returns the text.
        """
        self.inputText = None
        self.content.setFocus()

        def _onInput(text):
            self.inputText = text

        def _onKill():
            self.inputText = ""

        self.keyboardTextSubmitted.connect(_onInput)
        self.killSwitchSignal.connect(_onKill)

        while self.inputText is None:
            QApplication.processEvents()

        try:    self.keyboardTextSubmitted.disconnect(_onInput)
        except: pass
        try:    self.killSwitchSignal.disconnect(_onKill)
        except: pass

        return self.inputText.strip().lower()

    # ─── connectVoice (with fix) ────────────────────────────────────────
    def connectVoice(self, content):
        def enqueue_or_print():
            if self.printing:
                self.printQueue.append(("voice", content))
            else:
                self.content.clear()
                self.outputBuffer      = content
                self.outputIndex       = 0
                self.printingToContent = True
                self.printing          = True
                self._printNextChar()
        if threading.current_thread() is threading.main_thread():
            enqueue_or_print()
        else:
            QMetaObject.invokeMethod(self, enqueue_or_print, Qt.QueuedConnection)
        #self.connectOutput(content)  # Reuse connectOutput for voice content

    # ─── connectOutput (with fix) ───────────────────────────────────────
    def connectOutput(self, content):
        def enqueue_or_print():
            if self.printing:
                self.printQueue.append(("output", content))
            else:
                self.outputText.clear()
                self.outputBuffer      = content
                self.outputIndex       = 0
                self.printingToContent = False
                self.printing          = True
                self._printNextChar()
        if threading.current_thread() is threading.main_thread():
            enqueue_or_print()
        else:
            QMetaObject.invokeMethod(self, enqueue_or_print, Qt.QueuedConnection)

    # ─── Text animation (with Fix #2) ───────────────────────────────────
    def _printNextChar(self):
        if self.outputPaused:
            return

        targetWidget = self.content if self.printingToContent else self.outputText

        if self.outputIndex >= len(self.outputBuffer):
            self.printing = False

            if self.printQueue:
                target, nxt = self.printQueue.popleft()
                self.outputBuffer      = nxt
                self.outputIndex       = 0
                self.printingToContent = (target == "voice")
                # always clear the next target
                (self.content if self.printingToContent else self.outputText).clear()

                self.printing = True
                self._printNextChar()
            return

        ch = self.outputBuffer[self.outputIndex]
        targetWidget.insertPlainText(ch)
        targetWidget.moveCursor(QTextCursor.End)
        self.outputIndex += 1

        delay = {".":450,"!":450,"?":450,",":300,"\n":100," ":53}.get(ch,33)
        self.outputTimer.singleShot(delay, self._printNextChar)

    def pauseOutput(self):
        if threading.current_thread() is threading.main_thread():
            self.outputPaused = True
        else:
            QTimer.singleShot(0, self.pauseOutput)

    def resumeOutput(self):
        if threading.current_thread() is threading.main_thread() and self.printing:
            self.outputPaused = False
            self._printNextChar()
        else:
            QTimer.singleShot(0, self.resumeOutput)

    def stopOutput(self):
        if threading.current_thread() is threading.main_thread():
            self.outputPaused = False
            self.printing     = False
            self.printQueue.clear()
            self.outputBuffer = ""
            self.outputIndex  = 0
            self.outputText.clear()
        else:
            QTimer.singleShot(0, self.stopOutput)

    def setMode(self, mode: str):
        if mode.lower() == "keyboard":
            self.content.show()
            self.content.setEnabled(True)
        else:
            self.content.show()
            #self.content.hide()
            self.content.setEnabled(False)
        self.update()

    def killSwitch(self):
        try:
            if hasattr(self, 'flashTimer'):   self.flashTimer.stop()
            if hasattr(self, 'fadeInAnim'):   self.fadeInAnim.stop()
            if hasattr(self, 'fadeOutAnim'):  self.fadeOutAnim.stop()
        except Exception:
            logger.error("KillSwitch error", exc_info=True)
        for btn in (self.minimizeButton, self.maximizeButton, self.closeButton):
            btn.setEnabled(False)
        self.stopOutput()
        self.setWindowOpacity(0)
        super().hide()

    def refreshStyles(self):
        self.setStyleSheet(windowStyle())
        self.titleLabel.setStyleSheet(titleLabelStyle())
        btnStyle = titleButtonStyle()
        for btn in (self.minimizeButton, self.maximizeButton, self.closeButton):
            btn.setStyleSheet(btnStyle)
        textStyle = textEditStyle(self.fontSize)
        self.content.setStyleSheet(textStyle)
        self.outputText.setStyleSheet(textStyle)
