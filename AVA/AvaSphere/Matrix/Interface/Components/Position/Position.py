import math
from PyQt5.QtCore import QObject, QPoint, QPropertyAnimation
from PyQt5.QtGui import QGuiApplication

class PositionManager(QObject):
    """
    Encapsulates all logic for computing, animating, and executing direct moves,
    including a 'previous' move, of a top-level QWidget on the primary screen.
    """
    _POSITION_FACTORIES = {
        "top-left":      lambda sw,sh,ww,wh: (0, 0),
        "top-center":    lambda sw,sh,ww,wh: ((sw-ww)//2, 0),
        "top-right":     lambda sw,sh,ww,wh: (sw-ww, 0),
        "center-left":   lambda sw,sh,ww,wh: (0, (sh-wh)//2),
        "left-center":   lambda sw,sh,ww,wh: (0, (sh-wh)//2),
        "center":        lambda sw,sh,ww,wh: ((sw-ww)//2, (sh-wh)//2),
        "center-right":  lambda sw,sh,ww,wh: (sw-ww, (sh-wh)//2),
        "right-center":  lambda sw,sh,ww,wh: (sw-ww, (sh-wh)//2),
        "bottom-left":   lambda sw,sh,ww,wh: (0, sh-wh),
        "bottom-center": lambda sw,sh,ww,wh: ((sw-ww)//2, sh-wh),
        "bottom-right":  lambda sw,sh,ww,wh: (sw-ww, sh-wh),
        "left":          lambda sw,sh,ww,wh: (0, (sh-wh)//2),
        "right":         lambda sw,sh,ww,wh: (sw-ww, (sh-wh)//2),
        "up":            lambda sw,sh,ww,wh: ((sw-ww)//2, 0),
        "down":          lambda sw,sh,ww,wh: ((sw-ww)//2, sh-wh),
    }

    def __init__(self, window):
        super().__init__(window)
        self.win      = window
        self.prevPos  = window.pos()
        self._anims   = []

    def screenAndWindow(self):
        """
        Returns (screen_width, screen_height, window_width, window_height)
        based on availableGeometry() so that edges line up with where
        you initially positioned the window.
        """
        screen = QGuiApplication.primaryScreen()
        geom   = screen.availableGeometry()    # <-- use availableGeometry here
        sw, sh = geom.width(), geom.height()
        ww, wh = self.win.width(), self.win.height()
        return sw, sh, ww, wh

    def storeCurrent(self):
        """Snapshot current pos for 'previous'."""
        self.prevPos = self.win.pos()

    def animateMove(self, direction, duration=2000):
        key = direction.lower()
        if key == "previous":
            return self.movePrevious(animated=True)

        self.storeCurrent()
        sw, sh, ww, wh = self.screenAndWindow()
        factory = self._POSITION_FACTORIES.get(key)
        if not factory:
            raise ValueError(f"Unknown direction: {direction!r}")

        x, y = factory(sw, sh, ww, wh)
        anim = QPropertyAnimation(self.win, b"pos", self)
        anim.setDuration(duration)
        anim.setStartValue(self.win.pos())
        anim.setEndValue(QPoint(x, y))
        anim.start()
        self._anims.append(anim)
        anim.finished.connect(lambda a=anim: self._anims.remove(a))

    def directMove(self, direction):
        key = direction.lower()
        if key == "previous":
            return self.movePrevious(animated=False)

        self.storeCurrent()
        sw, sh, ww, wh = self.screenAndWindow()
        factory = self._POSITION_FACTORIES.get(key)
        if not factory:
            raise ValueError(f"Unknown direction: {direction!r}")

        x, y = factory(sw, sh, ww, wh)
        self.win.move(x, y)

    def movePrevious(self, animated=False):
        if animated:
            anim = QPropertyAnimation(self.win, b"pos", self)
            anim.setDuration(2000)
            anim.setStartValue(self.win.pos())
            anim.setEndValue(self.prevPos)
            anim.start()
            self._anims.append(anim)
            anim.finished.connect(lambda a=anim: self._anims.remove(a))
        else:
            self.win.move(self.prevPos)

    def getCurrentPosition(self):
        x,y=self.pos().x(),self.pos().y()
        sw,sh,ww,wh=self.screenAndWindow()
        horiz=("left" if x<=sw*0.25 else "right" if x+ww>=sw*0.75 else "center")
        vert =("top" if y<=sh*0.25 else "bottom" if y+wh>=sh*0.75 else "center")
        name="center" if (horiz,vert)==("center","center") else f"{vert}-{horiz}"
        return f"{name} (x:{x}, y:{y})"

    # def getCurrentPosition(self):
    #     # 1) grab the window's own pos() (already in screen coords for a top-level)
    #     x, y = self.pos().x(), self.pos().y()

    #     # 2) figure out screen size
    #     geom = QGuiApplication.primaryScreen().availableGeometry()
    #     sw, sh = geom.width(), geom.height()
    #     ww, wh = self.width(), self.height()

    #     # 3) bucket into left/center/right
    #     if   x <= sw * 0.25:        horizontal = "left"
    #     elif x + ww >= sw * 0.75:   horizontal = "right"
    #     else:                       horizontal = "center"

    #     # 4) bucket into top/center/bottom
    #     if   y <= sh * 0.25:        vertical = "top"
    #     elif y + wh >= sh * 0.75:   vertical = "bottom"
    #     else:                       vertical = "center"

    #     # 5) build the name
    #     name = "center" if (horizontal, vertical) == ("center","center") else f"{vertical}-{horizontal}"

    #     print(f"Current location: {name} (x:{x}, y:{y})")
    #     return f"{name} (x:{x}, y:{y})"
