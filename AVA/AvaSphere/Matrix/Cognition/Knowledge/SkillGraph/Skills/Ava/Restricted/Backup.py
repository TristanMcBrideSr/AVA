
import os
from datetime import datetime
import shutil
import re
from pathlib import Path
import logging
import threading
import inspect

from HoloAI import HoloLink
from AvaSphere.Matrix.Cognition.Database.Database import Database

logger = logging.getLogger(__name__)


class Backup:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Backup, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.holoLink = HoloLink()
        self.db          = Database()  
        self.sourceDir   = self.db.sourceDir
        self.backupDir   = self.db.backupDir
        self.excludeDirs = self.db.excludeDirs
        self.actionMap = {
            "create-backup":          self._createBackup,
            "delete-previous-backup": self._deletePreviousBackup,
            "delete-last-backups":    self._deleteLastBackups,
            "delete-all-backups":     self._deleteAllBackups,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Create backups."
        }

    def backupSkill(self, action: str, *args):
        self.holoLink.calledActions(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.holoLink.executeSkill('system', name, self.actionMap, action, *args)

    def _getDir(self, *paths: str) -> str:
        return str(Path(*paths).resolve())

    def _createBackup(self) -> str:
        destinationPath = self._buildNormalBackup()
        try:
            shutil.copytree(
                self.sourceDir,
                destinationPath,
                ignore=shutil.ignore_patterns(*self.excludeDirs)
            )
            return f"Successfully created backup."#: {destinationPath}"
        except Exception as e:
            logger.error(f"Error creating backup:", exc_info=True)
            return f"Error creating backup: {e}"

    def _deletePreviousBackup(self) -> str:
        try:
            backups = [
                self._getDir(self.targetPath, b)
                for b in os.listdir(self.targetPath)
                if self._isDateBackup(b)
            ]
            backups = sorted(backups, key=os.path.getmtime, reverse=True)

            if backups:
                latestBackup = backups[0]
                if os.path.isdir(latestBackup):
                    shutil.rmtree(latestBackup)
                elif os.path.isfile(latestBackup):
                    os.remove(latestBackup)
                return f"Deleted previous backup: {os.path.basename(latestBackup)}"
            return "No previous backup found to delete"
        except Exception as e:
            logger.error(f"Error deleting previous backup:", exc_info=True)
            return f"Error deleting previous backup: {e}"


    def _deleteLastBackups(self, count: int) -> str:
        if not isinstance(count, int):
            return "Provide a valid integer for count"

        try:
            backups = [
                self._getDir(self.targetPath, b)
                for b in os.listdir(self.targetPath)
                if self._isDateBackup(b)
            ]
            backups = sorted(backups, key=os.path.getmtime, reverse=True)
            toDelete = backups[:count]

            for b in toDelete:
                if os.path.isdir(b):
                    shutil.rmtree(b)
                elif os.path.isfile(b):
                    os.remove(b)

            return f"Deleted last {len(toDelete)} backup(s)"
        except Exception as e:
            logger.error(f"Error deleting last backups:", exc_info=True)
            return f"Error deleting last backups: {e}"

    def _deleteAllBackups(self) -> str:
        try:
            backups = [
                self._getDir(self.targetPath, b)
                for b in os.listdir(self.targetPath)
                if self._isDateBackup(b)
            ]
            for b in backups:
                if os.path.isdir(b):
                    shutil.rmtree(b)
                elif os.path.isfile(b):
                    os.remove(b)
            return "Deleted all backups"
        except Exception as e:
            logger.error(f"Error deleting all backups:", exc_info=True)
            return f"Error deleting all backups: {e}"

    def _validatePaths(self) -> bool:
        if not os.path.exists(self.sourceDir):
            return False
        if not os.path.exists(self.backupDir):
            os.makedirs(self.backupDir)
        return True

    def _buildNormalBackup(self) -> str:
        self._validatePaths()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return self._getDir(self.backupDir, f"{timestamp}")

    def _isDateBackup(self, folderName: str) -> bool:
        return bool(re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", folderName))