
import os
import logging
from itertools import cycle
from dotenv import load_dotenv

from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Freewill.AvaFreewill import Freewill
from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph
from AvaSphere.Matrix.Cognition.Knowledge.Learning.Learning import Learning
from AvaSphere.Matrix.Cognition.Knowledge.Logic.Logic import Logic#, CognitiveFlow
from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes, UserProfile
from AvaSphere.Matrix.Cognition.Memory.AvaMemory import Memory
from AvaSphere.Matrix.Cognition.Router.Router import Router
from AvaSphere.Matrix.Cognition.Processors.Main.MainProcessor import MainProcess
from AvaSphere.Matrix.Cognition.Processors.Sub.SubProcessor import SubProcess
from AvaSphere.Matrix.Utils.Tokenizer.Tokenizer import Tokenizer

load_dotenv()
logger = logging.getLogger(__name__)


class CognitiveProcess:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.attributes = Attributes()
        self.logic      = Logic()
        self.learning   = Learning()
        self.memory     = Memory()
        self.skillGraph = SkillGraph()
        self.tokenizer  = Tokenizer()
        self.router     = Router()
        self.freewill      = Freewill(self)
        self.mainProcess   = MainProcess(self)
        self.subProcess    = SubProcess(self)
        #self.cognitiveFlow = CognitiveFlow(self)
        self.processTypes = cycle(['Thinking', 'Clarifying', 'Gathering', 'Getting', 'Defining', 'Executing', 'Refining', 'Reflecting', 'Decision'])
        self.processMap = {
            'Thinking':   lambda ctx, logic: self.mainProcess.process(ctx, logic),
            'Clarifying': lambda ctx, logic: self.mainProcess.process(ctx, logic),
            'Gathering':  lambda ctx, logic: self.subProcess.process(ctx, logic),
            'Getting':    lambda ctx, logic: self.subProcess.process(ctx, logic),
            'Defining':   lambda ctx, logic: self.subProcess.process(ctx, logic),
            'Executing':  lambda ctx, logic: self.subProcess.process(ctx, logic),
            'Refining':   lambda ctx, logic: self.subProcess.process(ctx, logic),
            'Reflecting': lambda ctx, logic: self.mainProcess.process(ctx, logic),
            'Decision':   lambda ctx, logic: self.mainProcess.process(ctx, logic)
        }

    def process(self, ctx: str, logic=None, name: str = ""):
        if name:
            processType = name
        else:
            processType = next(self.processTypes)
        matrix = self.processMap.get(processType)
        result = matrix(ctx, logic) if matrix else None
        #self.cognitiveFlow.showProcess(processType, ctx, result)
        return result

    def _getActivation(self, key, envVar=None):
        load_dotenv(override=True)
        envVar     = envVar if envVar else f"ACTIVATE_{key.upper()}"
        attrActive = self.attributes.getCurrentAttribute("Ava", f"{key}-Activated", "False") == "True"
        envActive  = os.getenv(envVar, "False") == "True"
        return attrActive or envActive

    # def evaluate(self, ctx: str, response: str, stage: str) -> str:
    #     self.learning.evaluate(ctx, response, stage)

    def savePerception(self, ctx: str):
        self.memory.savePerception(ctx)

    def retrievePerception(self):
        return self.memory.retrievePerception()

    def clearPerception(self):
        self.memory.clearPerception()

    def _printPerception(self):
        self.memory.printPerception()
