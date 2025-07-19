import os
import threading
from pathlib import Path
from dotenv import load_dotenv
import logging

from SkillsManager import SkillsManager, SkillLink
from AvaSphere.Matrix.Cognition.Database.Database import Database

load_dotenv()
logger = logging.getLogger(__name__)

class SkillGraph:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SkillGraph, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.db            = Database()
        self.skillsManager = SkillsManager()
        self.skillLink     = SkillLink(githubRepo="TristanMcBrideSr/SkillForge", repoFolder="SkillForge", forgedDir=self.db.forgedSkillsDir)
        self.envDir        = self._getDir(self.db.projectEnvDir, "Skills")
        self.showSkills    = os.getenv('SHOW_SKILLS', 'False') == 'True'
        self.showMetaData  = os.getenv('SHOW_METADATA', 'False') == 'True'
        self.syncActivated = os.getenv("ACTIVATE_SKILL_SYNC", "False")
        if self.syncActivated == "True":
            self.skillList=["research"]
            self.skillLink.startSync() #(skillList=self.skillList, override=False)  # Download the latest skills from SkillForge
        self.dynamicComponents()
        self.forgedComponents()
        self.staticComponents()
        self.restrictedComponents()
        self.setMoveDirs()
        self.setMoveSettings()
        self.autoMove()
        if self.showSkills:
            self.getAvaCapabilities()
        if self.showMetaData:
            self.getMetaData()

    def _getDir(self, *paths: str) -> str:
        return str(Path(*paths).resolve())

    def dynamicComponents(self):
        self.dynamicUserSkills = []
        self.dynamicAvaSkills = []
        self.skillsManager.loadComponents(
            paths=[
                [self.db.userSkillsDir, self.db.userDynamicDir],
                [self.db.avaSkillsDir, self.db.avaDynamicDir]
            ],
            components=[
                self.dynamicUserSkills,
                self.dynamicAvaSkills
            ],
            reloadable=[
                True,
                True
            ]
        )

    def forgedComponents(self):
        self.forgedAvaSkills = []
        self.skillsManager.loadComponents(
            paths=[
                [self.db.forgedSkillsDir]
            ],
            components=[
                self.forgedAvaSkills
            ],
            reloadable=[
                False,
            ]
        )

    def staticComponents(self):
        self.staticUserSkills = []
        self.staticAvaSkills = []
        self.skillsManager.loadComponents(
            paths=[
                [self.db.userStaticDir],
                [self.db.avaStaticDir, self.db.opticDir]
            ],
            components=[
                self.staticUserSkills,
                self.staticAvaSkills
            ],
            reloadable=[
                False,
                False
            ]
        )

    def restrictedComponents(self):
        self.restrictedUserSkills = []
        self.restrictedAvaSkills = []
        self.skillsManager.loadComponents(
            paths=[
                [self.db.userRestrictedDir],
                [self.db.avaRestrictedDir]
            ],
            components=[
                self.restrictedUserSkills,
                self.restrictedAvaSkills
            ],
            reloadable=[
                False,
                False
            ]
        )

    def getUserActions(self, content):
        skills = (
            self.dynamicUserSkills + self.staticUserSkills +
            self.restrictedUserSkills
        )
        return self.skillsManager.getComponents(skills, content)

    def getAvaActions(self):
        skills = (
            self.dynamicAvaSkills + self.forgedAvaSkills +
            self.staticAvaSkills + self.restrictedAvaSkills
        )
        return self.skillsManager.getComponents(skills)

    def reloadSkills(self):
        self.skillsManager.reloadSkills()

    def getMetaData(self):
        metaData = (
                self.dynamicUserSkills + self.staticUserSkills +
                self.dynamicAvaSkills + self.staticAvaSkills +
                self.restrictedUserSkills + self.restrictedAvaSkills +
                self.forgedAvaSkills
        )
        return self.skillsManager.getMetaData(metaData, self.showMetaData)

    def getAvaCapabilities(self):
        description = False
        capabitites = (self.dynamicAvaSkills + self.forgedAvaSkills + self.staticAvaSkills + self.restrictedAvaSkills)
        return self.skillsManager.getCapabilities(capabitites, self.showSkills, description)

    def checkActions(self, action: str) -> str:
        return self.skillsManager.checkActions(action)

    def getActions(self, action: str) -> list:
        return self.skillsManager.getActions(action)

    def executeAction(self, actions, action):
        return self.skillsManager.executeAction(actions, action)

    def executeActions(self, actions, action):
        return self.skillsManager.executeActions(actions, action)

    def setMoveDirs(self):
        self.skillsManager.setMoveDirs(
            primarySkillDir=self.db.userSkillsDir,
            primaryDynamicDir=self.db.userDynamicDir,
            primaryStaticDir=self.db.userStaticDir,
            secondarySkillDir=self.db.avaSkillsDir,
            secondaryDynamicDir=self.db.avaDynamicDir,
            secondaryStaticDir=self.db.avaStaticDir
        )

    def setMoveSettings(self, storageUnit="days", storageValue=7, checkInterval=10, noMoveLimit=3):
        self.skillsManager.setMoveSettings(storageUnit, storageValue, checkInterval, noMoveLimit)

    def manualMove(self, sourceDir, destinationDir, minAge=None):
        return self.skillsManager.manualMove(sourceDir, destinationDir, minAge)

    def autoMove(self):
        self.skillsManager.autoMove()

    def skillInstructions(self):
        """
        Get skill instructions for the ava based on its capabilities.
        """
        # If you want to use the default skill instructions without examples, uncomment the next line
        # and comment the line below it.
        #return self.skillsManager.skillInstructions(self.getAvaCapabilities())
        skillExamples = ""
        return self.skillsManager.skillInstructions(self.getAvaCapabilities(), skillExamples)

    def skillExamples(self):
        """
        Get examples of how to use skills from your naming conventions.
        This should be customized to match your skill naming conventions.
        """
        return (
            # "Single Action Examples:\n" # Don't change this line
            # "- ['getDate()']\n" # Change to match your skill naming conventions
            # "- ['getTime()']\n" # Change to match your skill naming conventions
            # "- ['getDate()', 'getTime()']\n"
            "Skill With Sub-Action Examples:\n" # Don't change this line
            "- ['appSkill(\"open\", \"Notepad\")']\n" # Change to match your skill naming conventions
            "- ['appSkill(\"open\", \"Notepad\")', 'appSkill(\"open\", \"Word\")']\n"
            "- ['weatherSkill(\"get-weather\", \"47.6588\", \"-117.4260\")']\n" # Change to match your skill naming conventions
        )

    # ----- Can be used with both skills and tools -----
    def isStructured(self, *args):
        """
        Check if any of the arguments is a list of dictionaries.
        This indicates structured input (multi-message format).
        """
        return self.skillsManager.isStructured(*args)

    def handleTypedFormat(self, role: str = "user", content: str = ""):
        """
        Format content for Google GenAI APIs.
        """
        return self.skillsManager.handleTypedFormat(role, content)

    def handleJsonFormat(self, role: str = "user", content: str = ""):
        """
        Format content for OpenAI APIs and similar JSON-based APIs.
        """
        return self.skillsManager.handleJsonFormat(role, content)

    def formatTypedExamples(self, items):
        """
        Handle roles for Google GenAI APIs, converting items to Gemini Content/Part types.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleTypedFormat
            - dict: wrapped as Content with role, value as text
            - list of dicts: each dict converted to Content with role, dict as text
        Returns a flat list of Content objects.
        """
        return self.skillsManager.formatTypedExamples(items)

    def formatJsonExamples(self, items):
        """
        Handle roles for OpenAI APIs, converting items to JSON message format.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleJsonFormat
            - dict: added as-is
            - list of dicts: each dict is added individually
        Returns a flat list of message dicts.
        """
        return self.skillsManager.formatJsonExamples(items)

    def formatExamples(self, items, formatFunc):
        """
        Ultra-robust handler for message formatting.
        Accepts string, dict, list of any mix, any nested depth.
        Silently ignores None. Converts numbers and bools to strings.
        """
        return self.skillsManager.formatExamples(items, formatFunc)

    def handleTypedExamples(self, items):
        """
        Handle roles for Google GenAI APIs, converting items to Gemini Content/Part types.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleTypedFormat
            - dict: wrapped as Content with role, value as text
            - list of dicts: each dict converted to Content with role, dict as text
        Returns a flat list of Content objects.
        """
        return self.skillsManager.handleTypedExamples(items)

    def handleJsonExamples(self, items):
        """
        Handle roles for OpenAI APIs, converting items to JSON message format.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleJsonFormat
            - dict: added as-is
            - list of dicts: each dict is added individually
        Returns a flat list of message dicts.
        """
        return self.skillsManager.handleJsonExamples(items)

    def handleExamples(self, items, formatFunc):
        """
        Ultra-robust handler for message formatting.
        Accepts string, dict, list of any mix, any nested depth.
        Silently ignores None. Converts numbers and bools to strings.
        """
        return self.skillsManager.handleExamples(items, formatFunc)

    def buildGoogleSafetySettings(self, harassment="BLOCK_NONE", hateSpeech="BLOCK_NONE", sexuallyExplicit="BLOCK_NONE", dangerousContent="BLOCK_NONE"):
        """
        Construct a list of Google GenAI SafetySetting objects.
        """
        return self.skillsManager.buildGoogleSafetySettings(harassment, hateSpeech, sexuallyExplicit, dangerousContent)

