from PyQt5.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
)

class Fade:
    """Mixin to add fade-in/fade-out to any QWidget subclass."""

    def _initFadeEffect(self):
        # assumes self.fadeInDuration, self.fadeOutDuration, self.visibilityChanged
        self.isFading  = False
        self.isShowing = False

        self.setWindowOpacity(0)

        self.fadeInAnim = QPropertyAnimation(self, b"windowOpacity")
        self.fadeInAnim.setDuration(self.fadeInDuration)
        self.fadeInAnim.setStartValue(0)
        self.fadeInAnim.setEndValue(1)
        self.fadeInAnim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fadeInAnim.finished.connect(self._onFadeInFinished)

        self.fadeOutAnim = QPropertyAnimation(self, b"windowOpacity")
        self.fadeOutAnim.setDuration(self.fadeOutDuration)
        self.fadeOutAnim.setStartValue(1)
        self.fadeOutAnim.setEndValue(0)
        self.fadeOutAnim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fadeOutAnim.finished.connect(self._onFadeOutFinished)

    def show(self):
        if not super().isVisible() and not self.isFading:
            self.isFading = True
            self.fadeOutAnim.stop()
            super().show()
            self.fadeInAnim.start()

    def hide(self):
        if super().isVisible() and not self.isFading:
            self.isFading = True
            self.fadeInAnim.stop()
            self.fadeOutAnim.start()

    def _fadeOutAndHide(self):
        if not self.isFading and self.windowOpacity() > 0:
            self.isFading = True
            self.fadeInAnim.stop()
            self.fadeOutAnim.start()

    def _onFadeInFinished(self):
        self.setWindowOpacity(1)
        # emit your window's visibilityChanged signal if it exists
        if hasattr(self, 'visibilityChanged'):
            self.visibilityChanged.emit(True)
        self.isFading  = False
        self.isShowing = True

    def _onFadeOutFinished(self):
        self.setWindowOpacity(0)
        super().hide()
        if hasattr(self, 'visibilityChanged'):
            self.visibilityChanged.emit(False)
        self.isFading  = False
        self.isShowing = False
