
import os
import sqlite3
import threading
from datetime import datetime, timedelta
import time
from pathlib import Path
from dotenv import load_dotenv
from SynMem import SynMem

from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Cognition.Database.Database import Database


load_dotenv()


class Memory:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Memory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.dbLock = threading.Lock()
        self._initComponents()
        self.initialized = True 

    def _initComponents(self):
        self.db           = Database()
        self.attributes   = Attributes()
        self.synMem       = SynMem()
        self.sessionStart = datetime.now()

        self.sensoryLimit       = 10
        self.sensoryExpireUnit  = "days"
        self.sensoryExpireValue = 7

        self.memoryExpireUnit   = "minutes"
        self.memoryExpireValue  = 30

        self.imageExpireUnit    = "days"
        self.imageExpireValue   = 30

        self.cleanupExpireUnit  = "days"
        self.cleanupExpireValue = 15

        self.perceptionLimit    = 10
        self._setSynMemDirs()
        self._setSynMemConfig()
        self._startAutoMaintenance()
        self._performStartupChecks()
        self.actionMap = {
            "retrieve-conversation-details":  self.retrieveConversationDetails,
            "retrieve-interaction-details":   self.retrieveInteractionDetails,
            "retrieve-image-details":         self.retrieveImageDetails,
            "retrieve-last-interaction-date": self.retrieveLastInteractionDate,
            "retrieve-last-interaction-time": self.retrieveLastInteractionTime,
            "clear-first-entry":              self.clearFirstEntry,
            "clear-last-entry":               self.clearLastEntry,
            "clear-all-entries":              self.clearAllEntries,
        }

    def _setSynMemDirs(self):
        synMemDirs = [
            self.db.senDir,
            self.db.stmUserConversationDetails,
            self.db.stmUserInteractionDetails,
            self.db.ltmUserConversationDetails,
            self.db.ltmUserInteractionDetails,
            self.db.stmCreatedImages,
            self.db.ltmCreatedImages,
            self.db.stmCreatedImageDetails,
            self.db.ltmCreatedImageDetails,
        ]
        self.synMem.setSynMemDirs(synMemDirs)

    def _setSynMemConfig(self):
        synMemConfig = [
            self.perceptionLimit,
            self.sensoryLimit,
            self.sensoryExpireUnit,
            self.sensoryExpireValue,
            self.memoryExpireUnit,
            self.memoryExpireValue,
            self.imageExpireUnit,
            self.imageExpireValue,
            self.cleanupExpireUnit,
            self.cleanupExpireValue,
            ]
        self.synMem.setSynMemConfig(synMemConfig)
        self.getUserName()  # Ensure user name is set at initialization

    def getUserName(self):
        name = self.attributes.getCurrentAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User"))
        #print(f"Memory Current User : {name}")
        return name

    # ─── Helpers ────────────────────────────────────────────────────────
    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def getTimedelta(self, unit, value):
        return timedelta(**{unit: value})

    # ─── Save ────────────────────────────────────────────────────────
    def savePerception(self, ctx: str):
        self.synMem.savePerception(ctx)

    def process(self, ctx: str, response: str):
        if not self._getActivation("TESTING", "TEST_MODE") or self._getActivation("Learning"):
            memoryProcess = self.saveToMemory if self._getActivation("Memory") else self.saveSensory
            memoryProcess(ctx, response)
        else:
            print(f"\nMemory processing skipped in Test Mode:\n {ctx} -> {response}\n")

    def saveToMemory(self, content: str, response: str) -> None:
        self.saveSensory(content, response)
        self.saveConversationDetails(content, response)
        self.saveInteractionDetails()

    def _getActivation(self, key, envVar=None):
        load_dotenv(override=True)
        envVar     = envVar if envVar else f"ACTIVATE_{key.upper()}"
        attrActive = self.attributes.getCurrentAttribute("Ava", f"{key}-Activated", "False") == "True"
        envActive  = os.getenv(envVar, "False") == "True"
        return attrActive or envActive

    def saveSensory(self, ctx, response):
        path     = self.getDir(self.db.senDir)
        userName = self.getUserName()
        self.synMem.saveSensory(ctx, response, userName, path)

    def saveConversationDetails(self, ctx, response):
        path     = self.getDir(self.db.stmUserConversationDetails)
        userName = self.getUserName()
        self.synMem.saveConversationDetails(ctx, response, userName, path)

    def saveInteractionDetails(self):
        path     = self.getDir(self.db.stmUserInteractionDetails)
        userName = self.getUserName()
        self.synMem.saveInteractionDetails(userName, path)

    # ─── Retrieve ────────────────────────────────────────────────────────
    def retrievePerception(self):
        return self.synMem.retrievePerception()

    def retrieveSensory(self) -> str:
        senDb = self.getDir(self.db.senDir, f"{self.getUserName()}.db")
        return self.synMem.retrieveSensory(senDb)

    def retrieveConversationDetails(self, user: str = None, startDate: str = None, endDate: str = None) -> str:
        user = user or self.getUserName()
        paths = [
            self.getDir(self.db.stmUserConversationDetails),
            self.getDir(self.db.ltmUserConversationDetails)
        ]
        return self.synMem.retrieveConversationDetails(user, paths, startDate, endDate)

    def retrieveInteractionDetails(self, startDate: str = None, endDate: str = None) -> str:
        paths = [
            self.getDir(self.db.stmUserInteractionDetails),
            self.getDir(self.db.ltmUserInteractionDetails)
        ]
        return self.synMem.retrieveInteractionDetails(paths, startDate, endDate)

    def retrieveImageDetails(self, startDate: str = None, endDate: str = None) -> str:
        paths = [
            self.getDir(self.db.stmCreatedImageDetails),
            self.getDir(self.db.ltmCreatedImageDetails)
        ]
        return self.synMem.retrieveImageDetails(paths, startDate, endDate)

    def retrieveLastInteractionDate(self, user: str = None) -> str:
        userName = user or self.getUserName()
        paths = [
            self.getDir(self.db.senDir),
            self.getDir(self.db.stmUserConversationDetails),
            self.getDir(self.db.ltmUserConversationDetails)
        ]
        return self.synMem.retrieveLastInteractionDate(userName, paths)

    def retrieveLastInteractionTime(self, user: str = None) -> str:
        userName = user or self.getUserName()
        paths = [
            self.getDir(self.db.senDir),
            self.getDir(self.db.stmUserConversationDetails),
            self.getDir(self.db.ltmUserConversationDetails)
        ]
        return self.synMem.retrieveLastInteractionTime(userName, paths)

    # ─── Checks ────────────────────────────────────────────────────────
    def _startAutoMaintenance(self, interval=5*60):  # every 5 mins
        self.synMem.startAutoMaintenance(interval)

    def _performStartupChecks(self, delay: int = 1):
        self.synMem.performStartupChecks(delay)

    # ─── Clear ────────────────────────────────────────────────────────
    def clearPerception(self):
        self.synMem.clearPerception()

    def clearFirstEntry(self, user: str = None):
        userName = user or self.getUserName()
        return self.synMem.clearFirstEntry(userName)

    def clearLastEntry(self, user: str = None):
        userName = user or self.getUserName()
        return self.synMem.clearLastEntry(userName)

    def clearAllEntries(self, user: str = None):
        userName = user or self.getUserName()
        return self.synMem.clearAllEntries(userName)

    # ─── Image ────────────────────────────────────────────────────────
    def saveCreatedImage(self, imageSubject: str, imageData: str) -> None:
        path1 = self.getDir(self.db.createdImages)
        path2 = self.getDir(self.db.stmCreatedImageDetails)
        return self.synMem.saveCreatedImage(imageSubject, imageData, path1, path2)

    def retrieveCreatedImage(self, directory: str, imageName: str):
        return self.synMem.retrieveCreatedImage(directory, imageName)

    # ─── View ────────────────────────────────────────────────────────
    def viewDatabase(self, path: str, limit=None):
        return self.synMem.viewDatabase(path, limit) 

    def viewDetailsDatabase(self, path: str, limit=None):
        return self.synMem.viewDetailsDatabase(path, limit) 

    # ─── Print ────────────────────────────────────────────────────────
    def printPerception(self):
        if self.synMem.perception:
            print("Perception Feedback:")
            for feedback in self.synMem.perception:
                print(feedback)
        else:
            #pass
            print("No Perception Feedback Available.")