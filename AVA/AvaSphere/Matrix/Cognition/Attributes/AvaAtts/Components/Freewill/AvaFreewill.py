

import random, os, re, sys, time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.genai.types import ModelOrDict

from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Profile.UserProfile import UserProfile
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Sentiment.AvaSentiment import Emotions, Feelings, Opinions

load_dotenv()


class Freewill:
    def __init__(self, parent=None):
        self._initComponents(parent)

    def _initComponents(self, parent):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # but I'll give a basic example
        self.parent           = parent
        self.avaProfile       = AvaProfile()
        self.userProfile      = UserProfile()
        self.currentUserName  = self.userProfile.identity.loadCurrentUserName()
        self.previousUserName = self.userProfile.identity.loadPreviousUserName()
        self.acceptAction     = False
        self.defaultStatus    = "False"

    def getCurrent(self):
        self.currentStatus = self.avaProfile.features.loadStatus("Freewill", self.defaultStatus)
        return self.currentStatus


    def determineAction(self, ctx: str, logic=None):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def accepted(self, ctx: str, logic=None):
        try:
            if not self._getActivation():
                self.acceptAction = True
                return True

            if "please" in ctx:
                self.acceptAction = True
                return True

            # Implementation details are proprietary to Sybil's system and cannot be shared.
            # Bias to True 75% of the time, False 25% VERY BASIC AND NOT TRUE FREEWILL
            self.acceptAction = random.choices([True, False], [3, 1])[0]
            return self.acceptAction

        except Exception:
            self.acceptAction = False
            return False

    def denied(self, ctx: str, logic=None):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        msg = [
            f"Sorry, I cannot comply with your request for: {ctx}.",
            f"Unfortunately, I cannot fulfill your request.",
            f"Regrettably, I cannot assist with: {ctx}.",
            f"Apologies, but I cannot process your request for: {ctx}.",
            f"Sorry, I cannot do that.",
        ]
        return random.choice(msg)

    def _getActivation(self):
        load_dotenv(override=True)
        attrActive = self.getCurrent() == "True"
        envActive = os.getenv("ACTIVATE_FREEWILL", "False") == "True"
        return attrActive or envActive
