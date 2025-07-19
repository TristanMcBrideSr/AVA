
import re
import os
import threading
from dotenv import load_dotenv
# from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Regression.Regression import *
# from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Regulators.Regulators import *
# from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Triggers.Triggers import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Profile.UserProfile import UserProfile

load_dotenv()

class Sentiment:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if hasattr(self, 'initialized'):
            return
        self.parent = parent
        # Implementation details are proprietary to Sybil's system and cannot be shared.



class Emotions(Sentiment):

    def _initComponents(self, parent):
        self.parent = parent
        # Implementation details are proprietary to Sybil's system and cannot be shared.


class Feelings(Sentiment):

    def _initComponents(self, parent):
        self.parent = parent
        # Implementation details are proprietary to Sybil's system and cannot be shared.


class Opinions(Sentiment):

    def _initComponents(self, parent):
        self.parent = parent
        # Implementation details are proprietary to Sybil's system and cannot be shared.