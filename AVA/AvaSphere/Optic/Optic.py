import threading
import inspect
import logging
from HoloAI import HoloLink

from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Cognition.Memory.AvaMemory import Memory
#from AvaSphere.Matrix.Cognition.Router.Router import Router
#from AvaSphere.Optic.Components.Gen.OpticGen import Gen
from AvaSphere.Optic.Components.Rec.OpticRec import Rec


logger = logging.getLogger(__name__)


class Optic:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Optic, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        super().__init__()
        if hasattr(self, 'initialized'):
            return

        self._initComponents()

        self.initialized = True

    def _initComponents(self):
        self.holoLink  = HoloLink()
        self.db         = Database()
        self.attributes = Attributes()
        self.memory     = Memory()
        #self.router    = Router() # DO NOT USE ROUTER IN OPTIC, USE IT DIRECTLY IN THE REC AND GEN COMPONENTS, AS USING IT IN OPTIC CAUSES ISSUES
        self.rec        = Rec(self)
        #self.gen       = Gen(self)
        self.actionMap = {
            **self.rec.actionMap,
            #**self.gen.actionMap,
        }

    def _metaData(self):
        return {
            "className": f"{self.__class__.__name__}",
            "description": "View my environment, what the user is doing on the computer, describing and comparing media, recognizing users from the front and rear cameras as well as creating images, videos and gifs."
        }

    def opticSkill(self, action: str, *args):
        self.holoLink.calledActions(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.holoLink.executeSkill('system', name, self.actionMap, action, *args)
