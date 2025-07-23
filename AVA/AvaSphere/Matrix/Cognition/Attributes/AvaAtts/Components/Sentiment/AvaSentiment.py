
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
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        self.parent = parent
        self._initComponents(parent)
        self.initialized = True

    def _metaData(self):
        return {
            "className": self.__class__.__name__, 
            "description": getattr(self, "DESCRIPTION", "Sentiment Base Class")
        }

    def _getCurrentUserName(self):
        if not hasattr(self, "userProfile") or self.userProfile.identity is None:
            raise AttributeError(f"{self.__class__.__name__} has no userProfile set!")
        return self.userProfile.identity.loadCurrentUserName()

    def restrictAtts(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def _restrictWeights(self, attributes, maxTotal):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def _getActivation(self, key, envVar=None):
        load_dotenv(override=True)
        envVar = envVar or f"ACTIVATE_{key.upper()}"
        attrActive = self.avaProfile.features.loadStatus(f"{key}", self.defaultStatus) == "True"
        envActive = os.getenv(envVar, self.defaultStatus) == "True"
        return attrActive or envActive

    def handleTriggers(self, content):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def _applyBiases(self, weights):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def _initComponents(self, parent): raise NotImplementedError
    def saveStates(self): raise NotImplementedError
    def updateState(self): raise NotImplementedError
    def getCurrent(self): raise NotImplementedError
    def getPrevious(self): raise NotImplementedError

    def _printWeights(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def _printCurrentState(self):
        state = self.getCurrent()
        print(f"\nCurrent {self.__class__.__name__.lower()}: {state}")

    def _updateWeightAtts(self, *changes):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass



class Emotions(Sentiment):
    ACTIVATION_KEY = "Emotions"
    DESCRIPTION    = "Allows me to have emotions."

    def _initComponents(self, parent):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        self.parent = parent
        self.avaProfile  = AvaProfile()
        self.userProfile = UserProfile()
        self.defaultEmotion = 'Excited'
        self.defaultStatus  = 'False'

    def _loadStatesFromProfile(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def saveStates(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def getCurrent(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultEmotion

    def getPrevious(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultEmotion

    def getEmotions(self, userName=None):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultEmotion

    def updateState(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def _getTriggerBiases(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass


class Feelings(Sentiment):
    ACTIVATION_KEY = "Feelings"
    DESCRIPTION    = "Allows me to have feelings."

    def _initComponents(self, parent):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        self.parent = parent
        self.avaProfile  = AvaProfile()
        self.userProfile = UserProfile()
        self.defaultFeeling = "Neutral"
        self.defaultStatus  = "False"

    def _loadStatesFromProfile(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def saveStates(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass
        
    def getCurrent(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultFeeling

    def getPrevious(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultFeeling

    def getFeelings(self, userName=None):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultFeeling

    def updateState(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass


class Opinions(Sentiment):
    ACTIVATION_KEY = "Feelings"
    DESCRIPTION    = "Allows me to have opinions."

    def _initComponents(self, parent):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        self.parent = parent
        self.avaProfile  = AvaProfile()
        self.userProfile = UserProfile()
        self.defaultOpinion = "Like"
        self.defaultStatus  = "False"

    def _loadStatesFromProfile(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def saveStates(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def getCurrent(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultOpinion

    def getPrevious(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultOpinion

    def getOpinions(self, userName=None):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # For demonstration purposes, we return a placeholder value.
        return self.defaultOpinion

    def updateState(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass