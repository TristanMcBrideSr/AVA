
import os
from AvaSphere.Matrix.Utils.Logger import *
from Config.Config import Config
from AvaSphere.Matrix.Interface.Interface import *
from AvaSphere.Echo.Echo import Echo
from AvaSphere.Matrix.Matrix import Matrix
from AvaSphere.Matrix.Utils.ClearCaches.ClearCaches import ClearCaches


class Ava(QThread):
    def __init__(self):
        super().__init__()
        self.config     = Config()
        self.clearCache = ClearCaches()
        if os.getenv("CLEAR_CACHES", "False") == "True":
            self.clearCache.clearCached()
        self.interface = Interface()
        self.echo      = Echo()
        self.matrix    = Matrix()

    def run(self):
        self.interface.activation()
        while True:
            ctx = self.echo.processState()
            if ctx:
                result = self.matrix.process(ctx)
                self.echo.synthesize(result)
                self.matrix.evaluate(ctx)
                if self.echo.processState(ctx):
                    break
                while True:
                    ctx = self.echo.recognize()
                    if ctx:
                        result = self.matrix.process(ctx)
                        self.echo.synthesize(result)
                        self.matrix.evaluate(ctx)
                        if self.echo.processState(ctx):
                            break

    # def run(self):
    #     self.interface.activation()  # Activate the interface
    #     self.initial()  # Start the initial processing loop

    # def initial(self):
    #     while True:
    #         ctx = self.echo.processState()
    #         if ctx:
    #             self.process(ctx)

    #             if self.echo.processState(ctx):  # Conditional break still valid
    #                 break
    #             if self.followup():
    #                 break

    # def followup(self):
    #     while True:
    #         ctx = self.echo.recognize()
    #         if ctx:
    #             self.process(ctx)
    #             if self.echo.processState(ctx):
    #                 return True  # ← signal to outer loop to break
    #     return False

    # def process(self, ctx: str):
    #     result = self.matrix.process(ctx)
    #     self.echo.synthesize(result)
    #     self.matrix.evaluate(ctx) ## Uncomment for Ava to evaluate each stage after processing


if __name__ == "__main__":
    app     = QApplication(sys.argv)
    xpsx    = Ava()
    xpsx.start()
    sys.exit(app.exec_())


