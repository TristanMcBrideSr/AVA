
import inspect
import logging
import os
import threading
from dotenv import load_dotenv
from SkillLink import SkillLink

from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes

logger = logging.getLogger(__name__)


class State:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(State, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillLink = SkillLink()
        self.attributes    = Attributes()
        self.actionMap = {
            "deactivate": self._deactivate,
            "standby":    self._standby,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Manage state."
        }

    def stateSkill(self, action: str, *args):
        self.skillLink.calledActions(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)

    # ─────────────────────── Mode Functions ──────────────────────
    def _activate(self, featureName: str):
        # featureName = featureName.capitalize()
        # return f"{featureName} activated."
        pass

    def _deactivate(self) -> str:
        name = self._getUserName()
        # familyMembers = self._currentFamilyMembers()
        # isFamilyActivated = self._getActivation("Family")
        # if not isFamilyActivated:
        #     return f"Ask {name} for confirmation before deactivating yourself."
        # if name in familyMembers:
        #     return f"Ask {name} for confirmation before deactivating yourself."
        # return f"You must tell {name}, they are not authorized to have you deactivate yourself."
        return f"Ask {name} for confirmation before deactivating yourself."

    def _standby(self) -> str:
        return "Going into standby mode."

    def _getUserName(self) -> str:
        defaultUserName = os.getenv("DEFAULT_USER_NAME", "User")
        return self.attributes.getCurrentAttribute("User", "Name", defaultUserName)

    def _currentFamilyMembers(self) -> str:
        familyMembers = self.attributes.getValidFamilyNames()
        return familyMembers if familyMembers else "No family members found."

    def _getActivation(self, key, envVar=None):
        load_dotenv(override=True)
        envVar     = envVar or f"ACTIVATE_{key.upper()}"
        attrActive = self.attributes.getCurrentAttribute("Ava", f"{key}-Activated", "False") == "True"
        envActive  = os.getenv(envVar, "False") == "True"
        return attrActive or envActive
