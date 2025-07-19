
import os
import shutil
import atexit
from pathlib import Path

class ClearCaches:

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def clearCached(self):
        try:
            for root, dirs, files in os.walk(os.getcwd()):
                for d in dirs:
                    if d == '__pycache__':
                        shutil.rmtree(self.getDir(root, d))
                        #print(f"Cleared cache: {self.getDir(root, d)}")
        except Exception as e:
            print(f"Error occurred while clearing cache: {e}")
        # for root, dirs, files in os.walk(startDir):
        #     for d in dirs:
        #         if d == '__pycache__':
        #             shutil.rmtree(self.getDir(root, d))

    def registerExitCleanup(self):
        try:
            atexit.register(self.clearCached)
        except Exception as e:
            print(f"Error occurred while registering exit cleanup: {e}")


