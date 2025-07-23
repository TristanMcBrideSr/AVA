import os
import threading
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QScrollArea, QToolButton, QMenu,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QRectF
)
from PyQt5.QtGui import QPainterPath, QRegion
from dotenv import load_dotenv

from AvaSphere.Matrix.Utils.EnvUptater.EnvUpdater import EnvUpdater
from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Interface.Components.Constants.Constants import (
    FLASH_INTERVAL, FADE_IN_MS, FADE_OUT_MS, FONT_SIZE, FONT_MIN, FONT_MAX, FONT_STEP,
    BCWINDOW_POSITION, BCWINDOW_WIDTH, BCWINDOW_HEIGHT, BORDER_RADIUS,
)
from AvaSphere.Matrix.Interface.Components.Alignment.Alignment import Alignment
from AvaSphere.Matrix.Interface.Components.Fade.Fade import Fade
from AvaSphere.Matrix.Interface.Components.Flash.Flash import Flash
from AvaSphere.Matrix.Interface.Components.Style.Style import (
    windowStyle, titleLabelStyle, titleButtonStyle, textEditStyle, lineEditStyle, actionButtonStyle, toolButtonStyle, menuStyle,
    toggleNormalStyle, toggleSelectedStyle,
)
from AvaSphere.Matrix.Interface.Components.Selections.Selections import BCSECTION_FIELDS

load_dotenv()
logger = logging.getLogger(__name__)

SECTION_FIELDS = BCSECTION_FIELDS

evu = EnvUpdater()

def updateEnvValue(key, newValue, filename=".env"):
    # if not os.path.exists(filename):
    #     return
    # with open(filename, "r", encoding="utf-8") as file:
    #     lines = file.readlines()
    # updated = False
    # for i, line in enumerate(lines):
    #     if line.strip().startswith(f"{key}="):
    #         lines[i] = f"{key}={newValue}\n"
    #         updated = True
    #         break
    # if not updated:
    #     lines.append(f"{key}={newValue}\n")
    # with open(filename, "w", encoding="utf-8") as file:
    #     file.writelines(lines)
    # load_dotenv(filename, override=True)
    evu.updateEnvValue(key, newValue, filename)

def getDir(*paths):
    return str(Path(*paths).resolve())

def getAssetsPath(*paths):
    return str(Path(getDir(Database().startDir, "X UI ASSETS X"), *paths).resolve())

def buildPagesHierarchy(directory):
    hierarchy = {'subDirs': {}, 'pages': {}}
    if not os.path.exists(directory):
        return hierarchy
    for item in sorted(os.listdir(directory)):
        fullPath = getDir(directory, item)
        if os.path.isdir(fullPath):
            hierarchy['subDirs'][item] = buildPagesHierarchy(fullPath)
        elif item.lower().endswith(".txt"):
            hierarchy['pages'][Path(item).stem] = fullPath
    return hierarchy

def loadInitialMessage():
    try:
        with open(getAssetsPath("Pages", "welcome.txt"), "r", encoding="cp1252") as file:
            return file.read()
    except Exception as e:
        return f"Error loading welcome message: {e}"

class BCWindow(Fade, QWidget):
    inputTextSubmitted     = pyqtSignal(str)
    visibilityChanged      = pyqtSignal(bool)
    outputTextSubmitted    = pyqtSignal(str)
    killSwitchSignal       = pyqtSignal()

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(BCWindow, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        if hasattr(self, "initialized"):
            return

        self.enableFlash = False
        self._lastDevToggles = self._activateDevToggles()
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.attributes = Attributes()
        self.textFields = {}
        self.toggleButtons = {}
        self.normalStyle   = toggleNormalStyle()
        self.selectedStyle = toggleSelectedStyle()

        self.fontSize        = FONT_SIZE
        self.fadeInDuration  = FADE_IN_MS
        self.fadeOutDuration = FADE_OUT_MS
        self.isFading        = False
        self.isShowing       = False

        pagesDir            = getAssetsPath("Pages")
        self.pagesHierarchy = buildPagesHierarchy(pagesDir)
        self.subMenuOrder   = ["Welcome", "About", "Information", "Defaults", "Actions"]

        self._initWindow()
        self._initFadeEffect()
        self._initFlashEffect()

        self.envUpdateTimer = QTimer(self)
        self.envUpdateTimer.timeout.connect(self._updateAllFields)
        self.envUpdateTimer.start(1000)
        self.killSwitchSignal.connect(self.killSwitch, Qt.QueuedConnection)

    @property
    def getSelfName(self):
        defaultSelfName = os.getenv("ASSISTANT_NAME", "AVA")
        return self.attributes.getCurrentAttribute("Ava", "Name", defaultSelfName).upper()

    def _initWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(windowStyle())
        self.setFixedSize(BCWINDOW_WIDTH, BCWINDOW_HEIGHT)
        self._alignWindow(BCWINDOW_POSITION)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), BORDER_RADIUS, BORDER_RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(10)

        # --- TITLE BAR ---
        titleLayout = QHBoxLayout()
        self.titleLabel = QLabel(" ⪡⪢⪡⪢⪡⪢ SETTINGS ⪡⪢⪡⪢⪡⪢ ")
        self.titleLabel.setFixedHeight(50)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet(titleLabelStyle())

        self.minimizeButton = QPushButton("-")
        self.maximizeButton = QPushButton("+")
        self.closeButton    = QPushButton("X")
        for btn in (self.minimizeButton, self.maximizeButton, self.closeButton):
            btn.setFixedSize(50, 30)
            btn.setStyleSheet(titleButtonStyle())
        self.minimizeButton.clicked.connect(self._decreaseFontSize)
        self.maximizeButton.clicked.connect(self._increaseFontSize)
        self.closeButton.clicked.connect(self._fadeOutAndHide)
        self.minimizeButton.setEnabled(self.fontSize > FONT_MIN)
        self.maximizeButton.setEnabled(self.fontSize < FONT_MAX)

        titleLayout.addWidget(self.titleLabel, stretch=1)
        titleLayout.addWidget(self.minimizeButton)
        titleLayout.addWidget(self.maximizeButton)
        titleLayout.addWidget(self.closeButton)
        mainLayout.addLayout(titleLayout)

        # --- SCROLL AREA for CONTENT ---
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { border: none; }")
        mainLayout.addWidget(self.scrollArea)

        self.contentWidget = QWidget()
        self.scrollArea.setWidget(self.contentWidget)
        contentLayout = QVBoxLayout(self.contentWidget)
        contentLayout.setContentsMargins(5, 5, 5, 5)
        contentLayout.setSpacing(10)

        # INFO SECTION
        infoLayout = QVBoxLayout()
        self.pagesMenuButton = QToolButton()
        self.pagesMenuButton.setText("Welcome")
        self.pagesMenuButton.setPopupMode(QToolButton.InstantPopup)
        self.pagesMenuButton.setFixedWidth(1945)
        self.pagesMenuButton.setStyleSheet(toolButtonStyle())

        self.pagesMenu = QMenu(self)
        self.pagesMenu.setStyleSheet(menuStyle())
        self._populateMenu(self.pagesMenu, self.pagesHierarchy, self.subMenuOrder)
        self.pagesMenuButton.setMenu(self.pagesMenu)

        self.infoPanel = QTextEdit()
        self.infoPanel.setReadOnly(True)
        self.infoPanel.setFixedHeight(350)
        self.infoPanel.setStyleSheet(textEditStyle(self.fontSize))
        self.infoPanel.setPlainText(loadInitialMessage())

        infoLayout.addWidget(self.pagesMenuButton)
        infoLayout.addWidget(self.infoPanel)
        contentLayout.addLayout(infoLayout)

        # BOTTOM SECTION: TEXT INPUTS + TOGGLES
        bottomLayout = QHBoxLayout()

        # TEXT INPUTS
        textLayout = QVBoxLayout()
        for label, key in self._getProductionInputs():
            textLayout.addWidget(self._createTextRow(label, key))

        # TOGGLES (prod + dev toggles)
        self.togglesLayout = QVBoxLayout()
        self.togglesLayout.setSpacing(8)
        self.togglesLayout.setContentsMargins(0, 0, 0, 0)

        for label, key, *mode in self._getProductionToggles():
            self.togglesLayout.addWidget(self._createOnOffRow(label, key, *mode))

        self.devToggleWidgets = []
        self.devSpacerItem = None
        self._populateDevToggles()

        self.toggleBottomSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.togglesLayout.addItem(self.toggleBottomSpacer)

        bottomLayout.addLayout(textLayout, stretch=3)
        bottomLayout.addLayout(self.togglesLayout, stretch=2)
        contentLayout.addLayout(bottomLayout)
        contentLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum))

    def _activateDevToggles(self):
        load_dotenv(override=True)
        return os.getenv("DEV_TOGGLES", "False") == "True"

    def _populateMenu(self, parentMenu, hierarchy, subMenuOrder=None):
        if subMenuOrder is None:
            subMenuOrder = []
        for pageName, filePath in sorted(hierarchy.get('pages', {}).items()):
            action = parentMenu.addAction(pageName)
            action.triggered.connect(lambda _, fp=filePath: self._loadPageContent(fp))
        subDirs = list(hierarchy.get('subDirs', {}).keys())
        for desiredDir in subMenuOrder:
            if desiredDir in subDirs:
                subDirs.remove(desiredDir)
                subDirHierarchy = hierarchy['subDirs'][desiredDir]
                subMenu = QMenu(desiredDir, parentMenu)
                subMenu.setStyleSheet(parentMenu.styleSheet())
                parentMenu.addMenu(subMenu)
                self._populateMenu(subMenu, subDirHierarchy, subMenuOrder)
        for subDirName in sorted(subDirs):
            subDirHierarchy = hierarchy['subDirs'][subDirName]
            subMenu = QMenu(subDirName, parentMenu)
            subMenu.setStyleSheet(parentMenu.styleSheet())
            parentMenu.addMenu(subMenu)
            self._populateMenu(subMenu, subDirHierarchy, subMenuOrder)

    def _loadPageContent(self, filePath):
        if not self.isVisible():
            return
        try:
            with open(filePath, "r", encoding="cp1252") as f:
                data = f.read()
            self.infoPanel.setPlainText(data)
        except UnicodeDecodeError as e:
            self.infoPanel.setPlainText(f"Error reading {filePath}: {e}")
        except Exception as ex:
            self.infoPanel.setPlainText(f"Error: {ex}")

    def _createTextRow(self, labelText, envKey):
        rowWidget = QWidget()
        rowWidget.setMinimumHeight(40)
        rowWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rowLayout = QHBoxLayout(rowWidget)
        rowLayout.setSpacing(10)
        rowLayout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(labelText)
        label.setStyleSheet("color: white; font-size: 9pt;")
        label.setFixedWidth(370)

        lineEdit = QLineEdit()
        lineEdit.setFixedWidth(775)
        lineEdit.setStyleSheet(lineEditStyle(self.fontSize))
        lineEdit.setText(os.getenv(envKey, ""))
        self.textFields[envKey] = lineEdit

        saveButton = QPushButton("Save")
        saveButton.setFixedSize(90, 40)
        saveButton.setStyleSheet(actionButtonStyle(self.fontSize))
        saveButton.clicked.connect(lambda: self._setEnvValue(envKey, lineEdit.text()))

        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedSize(100, 40)
        cancelButton.setStyleSheet(actionButtonStyle(self.fontSize))
        cancelButton.clicked.connect(lambda: lineEdit.setText(os.getenv(envKey, "")))

        rowLayout.addWidget(label)
        rowLayout.addWidget(lineEdit)
        rowLayout.addWidget(saveButton)
        rowLayout.addWidget(cancelButton)
        rowLayout.addStretch()
        return rowWidget

    def _createOnOffRow(self, labelText, envKey, onValue="True", offValue="False"):
        rowWidget = QWidget()
        rowWidget.setMinimumHeight(40)
        rowWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rowLayout = QHBoxLayout(rowWidget)
        rowLayout.setSpacing(10)
        rowLayout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(labelText)
        label.setStyleSheet("color: white; font-size: 10pt;")
        label.setFixedWidth(400)
        label.setMinimumHeight(32)

        onButton = QPushButton("On")
        offButton = QPushButton("Off")
        onButton.setFixedSize(75, 40)
        offButton.setFixedSize(75, 40)
        onButton.setStyleSheet(self.normalStyle)
        offButton.setStyleSheet(self.normalStyle)
        onButton.setMinimumHeight(32)
        offButton.setMinimumHeight(32)

        def onClicked():
            self._setEnvValue(envKey, onValue)
            self._updateAllFields()
        def offClicked():
            self._setEnvValue(envKey, offValue)
            self._updateAllFields()

        onButton.clicked.connect(onClicked)
        offButton.clicked.connect(offClicked)

        self.toggleButtons[envKey] = (onButton, offButton, onValue, offValue)

        currentValue = os.getenv(envKey, offValue)
        if currentValue == onValue:
            onButton.setStyleSheet(self.selectedStyle)
        else:
            offButton.setStyleSheet(self.selectedStyle)

        rowLayout.addWidget(label)
        rowLayout.addWidget(onButton)
        rowLayout.addWidget(offButton)
        return rowWidget

    def _setEnvValue(self, key, value):
        updateEnvValue(key, value)

    def _updateAllFields(self):
        if not self.isVisible():
            return

        # Dynamically refresh dev toggles if needed
        currentDevToggles = self._activateDevToggles()
        if getattr(self, '_lastDevToggles', None) != currentDevToggles:
            self._lastDevToggles = currentDevToggles
            self._populateDevToggles()

        for key, widget in self.textFields.items():
            currentValue = os.getenv(key, "")
            if widget.text() != currentValue:
                widget.setText(currentValue)
        for key, (onB, offB, onV, offV) in list(self.toggleButtons.items()):
            if not (onB and offB):
                continue
            cv = os.getenv(key, offV)
            if cv == onV:
                onB.setStyleSheet(self.selectedStyle)
                offB.setStyleSheet(self.normalStyle)
            else:
                onB.setStyleSheet(self.normalStyle)
                offB.setStyleSheet(self.selectedStyle)

    def _populateDevToggles(self):
        for widget in getattr(self, "devToggleWidgets", []):
            self.togglesLayout.removeWidget(widget)
            widget.deleteLater()
        self.devToggleWidgets = []

        for label, key, *mode in self._getDevSettings():
            self.toggleButtons.pop(key, None)

        if getattr(self, "devSpacerItem", None):
            self.togglesLayout.removeItem(self.devSpacerItem)
            self.devSpacerItem = None

        if self._activateDevToggles():
            for label, key, *mode in self._getDevSettings():
                row = self._createOnOffRow(label, key, *mode)
                self.togglesLayout.insertWidget(self.togglesLayout.count()-1, row)
                self.devToggleWidgets.append(row)
        else:
            self.devSpacerItem = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.togglesLayout.insertItem(self.togglesLayout.count()-1, self.devSpacerItem)

    def _initFlashEffect(self):
        self.flash = Flash(self.titleLabel, interval=FLASH_INTERVAL)
        self.flash.toggle(self.enableFlash)

    def _increaseFontSize(self):
        if self.fontSize < FONT_MAX:
            self.fontSize += FONT_STEP
            self.maximizeButton.setEnabled(self.fontSize < FONT_MAX)
            self.minimizeButton.setEnabled(self.fontSize > FONT_MIN)
            self._updateInfoPanelFontSize()

    def _decreaseFontSize(self):
        if self.fontSize > FONT_MIN:
            self.fontSize -= FONT_STEP
            self.maximizeButton.setEnabled(self.fontSize < FONT_MAX)
            self.minimizeButton.setEnabled(self.fontSize > FONT_MIN)
            self._updateInfoPanelFontSize()

    def _updateInfoPanelFontSize(self):
        self.infoPanel.setStyleSheet(textEditStyle(self.fontSize))

    def _alignWindow(self, position):
        Alignment(self).align(position)

    def _getProductionInputs(self):
        return SECTION_FIELDS["Production-Inputs"]

    def _getProductionToggles(self):
        return SECTION_FIELDS["Production-Toggles"]

    def _getDevSettings(self):
        return SECTION_FIELDS["Dev-Toggles"]

    def connectKillSwitch(self):
        self.killSwitchSignal.emit()

    def killSwitch(self):
        try:
            if hasattr(self, 'flashTimer'):
                self.flashTimer.stop()
            if hasattr(self, 'envUpdateTimer'):
                self.envUpdateTimer.stop()
            if hasattr(self, 'fadeInAnim'):
                self.fadeInAnim.stop()
            if hasattr(self, 'fadeOutAnim'):
                self.fadeOutAnim.stop()
        except Exception as e:
            print(f"KillSwitch error in BCWindow: {e}")
            logger.error("BCWindow killSwitch error", exc_info=True)

        for btn in (self.minimizeButton, self.maximizeButton, self.closeButton, self.pagesMenuButton):
            btn.setEnabled(False)
        for field in self.textFields.values():
            field.setText("")
            field.setEnabled(False)
        for onB, offB, *_ in self.toggleButtons.values():
            onB.setEnabled(False)
            offB.setEnabled(False)
        self.infoPanel.clear()
        self.infoPanel.setReadOnly(True)
        self.titleLabel.setText("")
        self.setWindowOpacity(0)
        super().hide()

    def refreshStyles(self):
        self.setStyleSheet(windowStyle())
        self.titleLabel.setStyleSheet(titleLabelStyle())
        self.pagesMenuButton.setStyleSheet(toolButtonStyle())
        self.pagesMenu.setStyleSheet(menuStyle())
        self.infoPanel.setStyleSheet(textEditStyle(self.fontSize))

        btnStyle = titleButtonStyle()
        for btn in (self.minimizeButton, self.maximizeButton, self.closeButton):
            btn.setStyleSheet(btnStyle)
        for field in self.textFields.values():
            field.setStyleSheet(lineEditStyle(self.fontSize))
        btnStyle = actionButtonStyle(self.fontSize)
        for row in self.findChildren(QHBoxLayout):
            for i in range(row.count()):
                widget = row.itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.text() in {"Save", "Cancel"}:
                    widget.setStyleSheet(btnStyle)
        self.normalStyle   = toggleNormalStyle()
        self.selectedStyle = toggleSelectedStyle()
        for key, (onB, offB, onV, offV) in self.toggleButtons.items():
            current = os.getenv(key, offV)
            if current == onV:
                onB.setStyleSheet(self.selectedStyle)
                offB.setStyleSheet(self.normalStyle)
            else:
                onB.setStyleSheet(self.normalStyle)
                offB.setStyleSheet(self.selectedStyle)
