from PyQt5.QtWidgets import QApplication

TOP_PAD = 25
BOTTOM_PAD = 0

class Alignment:
    def __init__(self, widget, topPad=TOP_PAD, bottomPad=BOTTOM_PAD):
        self.widget = widget
        self.topPad = topPad
        self.bottomPad = bottomPad

    def align(self, position):
        screen = QApplication.primaryScreen().availableGeometry()
        sw, sh = screen.width(), screen.height()
        ww, wh = self.widget.width(), self.widget.height()

        positions = {
            'top-left': (0, self.topPad),
            'top-center': ((sw - ww) // 2, self.topPad),
            'top-right': (sw - ww, self.topPad),
            'bottom-left': (0, sh - wh - self.bottomPad),
            'bottom-center': ((sw - ww) // 2, sh - wh - self.bottomPad),
            'bottom-right': (sw - ww, sh - wh - self.bottomPad),
            'center-screen': ((sw - ww) // 2, (sh - wh) // 2),
            'left-center': (0, (sh - wh) // 2),
            'right-center': (sw - ww, (sh - wh) // 2),
            'center-left': (0, (sh - wh) // 2),
            'center-right': (sw - ww, (sh - wh) // 2),
        }

        if position not in positions:
            raise ValueError(f"Invalid position '{position}'. Valid positions are: {', '.join(positions)}")

        self.widget.move(*positions[position])
