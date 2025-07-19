# from PyQt5.QtCore import QTimer
# from AvaSphere.Matrix.Interface.Components.Style.Style import flashStyle, FLASH_COLOR1, FLASH_COLOR2
# FLASH_INTERVAL = 500

# class Flash:
#     def __init__(self, label, interval=FLASH_INTERVAL, colorA=FLASH_COLOR1, colorB=FLASH_COLOR2):
#         self.label = label
#         self.interval = interval
#         self.colorA = colorA
#         self.colorB = colorB
#         self.isVisible = True
#         self.enabled = False

#         self.timer = QTimer()
#         self.timer.setInterval(self.interval)
#         self.timer.timeout.connect(self._flash)

#     def _flash(self):
#         color = self.colorA if self.isVisible else self.colorB
#         self.label.setStyleSheet(flashStyle(color))
#         self.isVisible = not self.isVisible

#     def toggle(self, enable=True):
#         self.enabled = enable
#         if enable:
#             self.timer.start()
#         else:
#             self.timer.stop()
#             # Reset to default color if needed
#             self.label.setStyleSheet(flashStyle(self.colorB))


from PyQt5.QtCore import QTimer
from AvaSphere.Matrix.Interface.Components.Style.Style import flashStyle, flashColor1, flashColor2

FLASH_INTERVAL = 500


class Flash:
    def __init__(self, label, interval=FLASH_INTERVAL, colorA=flashColor1(), colorB=flashColor2()):
        self.label = label
        self.interval = interval
        self.colorA = colorA
        self.colorB = colorB
        self.isVisible = True
        self.enabled = False

        self.timer = QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self._flash)

    def _flash(self):
        color = flashColor1() if self.isVisible else flashColor2()
        self.label.setStyleSheet(flashStyle(color))
        self.isVisible = not self.isVisible

    def toggle(self, enable=True):
        self.enabled = enable
        if enable:
            self.timer.start()
        else:
            self.timer.stop()
            # Reset to default color if needed
            self.label.setStyleSheet(flashColor2())
