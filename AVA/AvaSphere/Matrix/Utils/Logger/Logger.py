
import logging
import os
import warnings
from HoloAI import HoloLog

from AvaSphere.Matrix.Cognition.Database.Database import Database

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API.")
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")

def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
    import traceback, sys
    sys.stderr.write(warnings.formatwarning(message, category, filename, lineno, line))
    traceback.print_stack(file=sys.stderr)

warnings.showwarning = warn_with_traceback

logsDir = Database().logsDir

HoloLog(logsDir, 'ERROR')