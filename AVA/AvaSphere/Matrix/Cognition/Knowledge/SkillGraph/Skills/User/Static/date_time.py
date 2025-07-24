
# I left this in the codebase for reference, but it is not currently used if you use it will override Ava's skills

# from datetime import datetime
# import inspect
# import threading
# import logging
# from SkillLink import SkillLink

# logger = logging.getLogger(__name__)


# class DTManager:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:
#                 if not cls._instance:
#                     cls._instance = super(DTManager, cls).__new__(cls, *args, **kwargs)
#         return cls._instance

#     def __init__(self):
#         if hasattr(self, 'initialized'):
#             return
#         self._initComponents()
#         self.initialized = True

#     def _initComponents(self):
#         self.skillLink = SkillLink()
#         self.actionMap = {
#             "what is the date": self._getCurrentDate,
#             "what is the time": self._getCurrentTime,
#         }

#     def _metaData(self):
#         return {
#             "className": f"{self.__class__.__name__}",
#             "description": "Get current date and time information"
#         }

#     def executeAction(self, ctx: str) -> str:
#         """
#         Description: Executes the requested action for date/time management based on context.
#         """
#         # self.skillLink.calledActions(self, locals())
#         name = inspect.currentframe().f_code.co_name
#         return self.skillLink.executeSkill('user', name, self.actionMap, ctx)

#     def _getCurrentDate(self, *args):
#         return datetime.now().strftime('%d-%B-%Y')

#     def _getCurrentTime(self, *args):
#         return datetime.now().strftime('%H:%M')
