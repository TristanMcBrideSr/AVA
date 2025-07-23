
import inspect
import logging
import os
import threading
from dotenv import load_dotenv
from SkillLink import SkillLink

from AvaSphere.Matrix.Cognition.Memory.AvaMemory import Memory as AMemory

logger = logging.getLogger(__name__)

class Memory:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Memory, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillLink = SkillLink()
        self.aMemory       = AMemory()
        self.actionMap = {
            **self.aMemory.actionMap, # Inherit actions from Memory
        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Manage memory."
        }

    def memorySkill(self, action: str, *args):
        self.skillLink.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillLink.executeSkill('system', name, self.actionMap, action, *args)