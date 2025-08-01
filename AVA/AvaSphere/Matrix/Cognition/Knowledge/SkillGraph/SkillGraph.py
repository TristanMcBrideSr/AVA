import os
from tabnanny import verbose
import threading
from pathlib import Path
from dotenv import load_dotenv
import logging
import re
from SkillLink import SkillLink, SyncLink
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
        self.skillLink     = SkillLink()
        self.syncLink      = SyncLink(githubRepo="TristanMcBrideSr/SkillForge", repoFolder="SkillForge/Forge", syncDir=self.db.forgedSkillsDir)
        self.envDir        = self._getDir(self.db.projectEnvDir, "Skills")
        self.showSkills    = os.getenv('SHOW_SKILLS', 'False') == 'True'
        self.showMetaData  = os.getenv('SHOW_METADATA', 'False') == 'True'
        self.syncActivated = os.getenv("ACTIVATE_SKILL_SYNC", "False")
        if self.syncActivated:
            # self.skillList=["research"] # List the skills you want to sync from SkillForge
            self.syncLink.startSync() #(syncList=self.skillList, override=False)  # Download the latest skills from SkillForge changing the override parameter to True will overwrite existing skills
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
        #self.generateExamples(self.getAvaCapabilities(), limit=None, verbose=True)
        self.skillInstructions()

    def _getDir(self, *paths: str) -> str:
        return str(Path(*paths).resolve())

    def dynamicComponents(self):
        self.dynamicUserSkills = []
        self.dynamicAvaSkills = []
        self.skillLink.loadComponents(
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
        self.skillLink.loadComponents(
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
        self.skillLink.loadComponents(
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
        self.skillLink.loadComponents(
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
        return self.skillLink.getComponents(skills, content)

    def getAvaActions(self):
        skills = (
            self.dynamicAvaSkills + self.forgedAvaSkills +
            self.staticAvaSkills + self.restrictedAvaSkills
        )
        return self.skillLink.getComponents(skills)

    def reloadSkills(self):
        self.skillLink.reloadSkills()

    def getMetaData(self):
        metaData = (
                self.dynamicUserSkills + self.staticUserSkills +
                self.dynamicAvaSkills + self.staticAvaSkills +
                self.restrictedUserSkills + self.restrictedAvaSkills +
                self.forgedAvaSkills
        )
        return self.skillLink.getMetaData(metaData, self.showMetaData)

    def getAvaCapabilities(self):
        description = False
        capabitites = (self.dynamicAvaSkills + self.forgedAvaSkills + self.staticAvaSkills + self.restrictedAvaSkills)
        return self.skillLink.getCapabilities(capabitites, self.showSkills, description)

    def checkActions(self, action: str) -> str:
        return self.skillLink.checkActions(action)

    def getActions(self, action: str) -> list:
        return self.skillLink.getActions(action)

    def executeAction(self, actions, action):
        return self.skillLink.executeAction(actions, action)

    def executeActions(self, actions, action):
        return self.skillLink.executeActions(actions, action)

    def setMoveDirs(self):
        self.skillLink.setMoveDirs(
            primarySkillDir=self.db.userSkillsDir,
            primaryDynamicDir=self.db.userDynamicDir,
            primaryStaticDir=self.db.userStaticDir,
            secondarySkillDir=self.db.avaSkillsDir,
            secondaryDynamicDir=self.db.avaDynamicDir,
            secondaryStaticDir=self.db.avaStaticDir
        )

    def setMoveSettings(self, storageUnit="days", storageValue=7, checkInterval=10, noMoveLimit=3):
        self.skillLink.setMoveSettings(storageUnit, storageValue, checkInterval, noMoveLimit)

    def manualMove(self, sourceDir, destinationDir, minAge=None):
        return self.skillLink.manualMove(sourceDir, destinationDir, minAge)

    def autoMove(self):
        self.skillLink.autoMove()

    def skillInstructions(self):
        """
        Get skill instructions for the ava based on its capabilities.
        NOTE: the skillInstructions in the skillLink method will automatically use your naming conventions you can also,
        - pass limit=(int e.g 10) to limit the number of examples included in the instructions, or
        - pass verbose=True to view the instructions in detail as it will print the instructions to the console.
        """
        # If you want to override the default skill instructions examples, uncomment the next line
        # and comment the line below it.
        # skillExamples = self.skillExamples() # Customize this to match your skill naming conventions
        # return self.skillLink.skillInstructions(self.getAvaCapabilities(), skillExamples)
        return self.skillLink.skillInstructions(self.getAvaCapabilities())

    def skillExamples(self):
        """
        Get examples of how to use skills from your naming conventions.
        This should be customized to match your skill naming conventions.
        """
        return (
            "Single Action Examples:\n" # Don't change this line
            "- ['getDate()']\n" # Change to match your skill naming conventions
            "- ['getTime()']\n" # Change to match your skill naming conventions
            "- ['getDate()', 'getTime()']\n"
            "Skill With Sub-Action Examples:\n" # Don't change this line
            "- ['appSkill(\"open\", \"Notepad\")']\n" # Change to match your skill naming conventions
            "- ['appSkill(\"open\", \"Notepad\")', 'appSkill(\"open\", \"Word\")']\n"
            "- ['weatherSkill(\"get-weather\", \"47.6588\", \"-117.4260\")']\n" # Change to match your skill naming conventions
            "- ['weatherSkill(\"get-weather\", \"47.6588\", \"-117.4260\")', 'weatherSkill(\"get-forecast\", \"47.6588\", \"-117.4260\")']\n"
        )

    # ----- Can be used with both skills and tools -----
    def isStructured(self, *args):
        """
        Check if any of the arguments is a list of dictionaries.
        This indicates structured input (multi-message format).
        """
        return self.skillLink.isStructured(*args)

    def handleTypedFormat(self, role: str = "user", content: str = ""):
        """
        Format content for Google GenAI APIs.
        """
        return self.skillLink.handleTypedFormat(role, content)

    def handleJsonFormat(self, role: str = "user", content: str = ""):
        """
        Format content for OpenAI APIs and similar JSON-based APIs.
        """
        return self.skillLink.handleJsonFormat(role, content)

    def formatTypedExamples(self, items):
        """
        Handle roles for Google GenAI APIs, converting items to Gemini Content/Part types.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleTypedFormat
            - dict: wrapped as Content with role, value as text
            - list of dicts: each dict converted to Content with role, dict as text
        Returns a flat list of Content objects.
        """
        return self.skillLink.formatTypedExamples(items)

    def formatJsonExamples(self, items):
        """
        Handle roles for OpenAI APIs, converting items to JSON message format.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleJsonFormat
            - dict: added as-is
            - list of dicts: each dict is added individually
        Returns a flat list of message dicts.
        """
        return self.skillLink.formatJsonExamples(items)

    def formatExamples(self, items, formatFunc):
        """
        Ultra-robust handler for message formatting.
        Accepts string, dict, list of any mix, any nested depth.
        Silently ignores None. Converts numbers and bools to strings.
        """
        return self.skillLink.formatExamples(items, formatFunc)

    def handleTypedExamples(self, items):
        """
        Handle roles for Google GenAI APIs, converting items to Gemini Content/Part types.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleTypedFormat
            - dict: wrapped as Content with role, value as text
            - list of dicts: each dict converted to Content with role, dict as text
        Returns a flat list of Content objects.
        """
        return self.skillLink.handleTypedExamples(items)

    def handleJsonExamples(self, items):
        """
        Handle roles for OpenAI APIs, converting items to JSON message format.
        Accepts a list of (role, value) tuples, where value can be:
            - str: will be wrapped using handleJsonFormat
            - dict: added as-is
            - list of dicts: each dict is added individually
        Returns a flat list of message dicts.
        """
        return self.skillLink.handleJsonExamples(items)

    def handleExamples(self, items, formatFunc):
        """
        Ultra-robust handler for message formatting.
        Accepts string, dict, list of any mix, any nested depth.
        Silently ignores None. Converts numbers and bools to strings.
        """
        return self.skillLink.handleExamples(items, formatFunc)

    def buildGoogleSafetySettings(self, harassment="BLOCK_NONE", hateSpeech="BLOCK_NONE", sexuallyExplicit="BLOCK_NONE", dangerousContent="BLOCK_NONE"):
        """
        Construct a list of Google GenAI SafetySetting objects.
        """
        return self.skillLink.buildGoogleSafetySettings(harassment, hateSpeech, sexuallyExplicit, dangerousContent)

    def generateExamples(self, capabilities: str, limit: int=None, verbose: bool=False):
        return self.skillLink.generateExamples(capabilities, limit, verbose)
        