
import logging

from itertools import cycle
from dotenv import load_dotenv

# Core Evolution - Utils
load_dotenv()
logger = logging.getLogger(__name__)

class SubProcess:
    def __init__(self, parent=None):
        self._initComponents(parent)

    def _initComponents(self, parent):
        self.parent       = parent
        self.skillGraph   = self.parent.skillGraph
        self.processTypes = cycle(['Gathering', 'Getting', 'Defining', 'Executing', 'Refining'])
        self.processMap = {
            'Gathering':  lambda ctx, logic: self._gatheringActions(ctx, logic),
            'Getting':    lambda ctx, logic: self._gettingActions(ctx, logic),
            'Defining':   lambda ctx, logic: self._definingActions(ctx, logic),
            'Executing':  lambda ctx, logic: self._executingActions(ctx, logic),
            'Refining':   lambda ctx, logic: self._refiningActions(ctx, logic),
        }

    def process(self, ctx: str, logic=None, name: str = ""):
        if name:
            processType = name
        else:
            processType = next(self.processTypes)
        matrix = self.processMap.get(processType)
        result = matrix(ctx, logic) if matrix else None
        return result

    def _gatheringActions(self, ctx, logic):
        return self.skillGraph.getUserActions(ctx)

    def _gettingActions(self, ctx, logic):
        return self.skillGraph.getActions(logic)

    def _definingActions(self, ctx, logic):
        return self.skillGraph.getAvaActions()

    def _executingActions(self, ctx, logic):
        return self.skillGraph.executeAction(ctx, logic)

    def _refiningActions(self, ctx, logic):
        state = logic
        return "\n".join(
            f"{item[0]} {item[1]}" if isinstance(item, tuple) else str(item)
            for item in state if item
        )