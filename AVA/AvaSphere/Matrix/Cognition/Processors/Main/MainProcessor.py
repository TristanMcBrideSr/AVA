
import os
import logging

from itertools import cycle
from dotenv import load_dotenv


# Core Evolution - Utils
load_dotenv()
logger = logging.getLogger(__name__)


class MainProcess:
    def __init__(self, parent=None):
        self._initComponents(parent)

    def _initComponents(self, parent):
        self.parent       = parent
        self.router       = self.parent.router
        self.logic        = self.parent.logic
        self.learning     = self.parent.learning
        self.attributes   = self.parent.attributes
        self.tokenizer    = self.parent.tokenizer
        self.processTypes = cycle(['Thinking', 'Clarifying', 'Reflection', 'Decision'])
        self.processMap = {
            'Thinking':   lambda ctx, logic: self._thinkingStage(ctx, logic),
            'Clarifying': lambda ctx, logic: self._clarifyingStage(ctx, logic),
            'Reflection': lambda ctx, logic: self._reflectionStage(ctx, logic),
            'Decision':   lambda ctx, logic: self._decisionStage(ctx, logic)
        }

    def process(self, ctx: str, logic=None, name: str = ""):
        if name:
            processType = name
        else:
            processType = next(self.processTypes)
        matrix = self.processMap.get(processType)
        result = matrix(ctx, logic) if matrix else None
        return result

    def _thinkingStage(self, ctx, logic):
        # system, user = self._getTCLogic("Thinking", ctx)
        # self._showTokens("Thinking", system, user)
        # return self._runContent(system, user)
        return ""

    def _clarifyingStage(self, ctx, logic):
        system, user = self._getTCLogic("Clarifying", ctx)
        self._showTokens("Clarifying", system, user)
        return self._runContent(system, user)

    def _reflectionStage(self, ctx, logic):
        # system, user = self._getRDLogic("Reflecting", ctx, logic)
        # self._showTokens("Reflecting", system, user)
        # return self._runContent(system, user)
        return ""

    def _decisionStage(self, ctx, logic):
        system, user = self._getRDLogic("Decision", ctx, logic)
        self._showTokens("Decision", system, user)
        return self._runContent(system, user)

    # -- Util Methods --

    def _runContent(self, system, user):
        # return self.neuralLink.runNeuralProcess(
        #     "content", self.getCoertextLink, self.getCoertextCore, system, user
        # )
        return self.router.getResponse(system, user)

    def customOverride(self) -> bool:
        load_dotenv(override=True)
        return os.getenv("DEV_OVERRIDE", "False") == "True"

    def _getTCLogic(self, processType: str, ctx: str) -> tuple:
        learnedMethod    = processType.lower()
        learned          = getattr(self.learning, learnedMethod)(ctx)
        # print(f"\n{processType}:\n")
        # print(f"\n{learned}\n")
        system           = self.logic.getLogic(processType) + learned
        return system, ctx

    def _getRDLogic(self, processType: str, content: str, logic: str) -> tuple:
        if logic is None:
            raise ValueError(f"Logic parameter is required for {processType} process.")
        formattedContent = f"Requested: {content}\nInformation: {logic}\n"
        system = self.logic.getLogic(processType)
        return system, formattedContent

    def _getName(self):
        defaultAssistantName = os.getenv("ASSISTANT_NAME", "AVA")
        return self.attributes.getCurrentAttribute("Ava", "Name", defaultAssistantName)

    def _getUserName(self, user):
        users = {
            "current":  self.attributes.getCurrentAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User")),
            "previous": self.attributes.getPreviousAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User"))
        }
        return users.get(user.lower(), os.getenv("DEFAULT_USER_NAME", "User"))

    def _showTokens(self, processType: str, system: str, user: str) -> None:
        load_dotenv(override=True)
        showTokens = os.getenv("SHOW_TOKENS", "False") == "True"
        name       = self._getName()
        userName   = self._getUserName('current')
        if showTokens:
            self.tokenizer.calculateTokens(name, processType, system)
            self.tokenizer.calculateTokens(userName, user)