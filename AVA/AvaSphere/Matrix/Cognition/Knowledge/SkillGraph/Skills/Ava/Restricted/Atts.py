
import logging
import os
import threading
import inspect
from pathlib import Path
from SkillLink import SkillLink

from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Manager.AvaManager import GetAvaInfo, UpdateAvaInfo
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Manager.UserManager import GetUserInfo, UpdateUserInfo

logger = logging.getLogger(__name__)


class UpdateAva:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UpdateAva, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillLink = SkillLink()
        self.updateAvaInfo = UpdateAvaInfo()
        self.actionMap = {
            **self.updateAvaInfo.actionMap,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Allows me update my features and attributes."
        }

    def updateSelfSkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)


class AvaInfo:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AvaInfo, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillLink = SkillLink()
        self.getAvaInfo    = GetAvaInfo()
        self.actionMap = {
            **self.getAvaInfo.actionMap,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Allows me get information about myself, including my name, age, and other attributes."
        }

    def selfInfoSkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)


class UpdateUser:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UpdateUser, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillLink  = SkillLink()
        self.updateUserInfo = UpdateUserInfo()
        self.actionMap = {
            **self.updateUserInfo.actionMap,
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Allows me preform various actions including updating the current user name, updating and getting user preferences and attributes."
        }

    def updateUserSkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)



class UserInfo:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UserInfo, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillLink = SkillLink()
        self.getUserInfo   = GetUserInfo()
        self.actionMap = {
            **self.getUserInfo.actionMap,
        }

    def _metaData(self):
        return {
            "className": f"{self.__class__.__name__}", 
            "description": "Get information about different users."
        }

    def userInfoSkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)




