
from dotenv import load_dotenv
from AvaSphere.Matrix.Utils.Logger.Logger import *
from AvaSphere.Echo.Echo import Echo
from AvaSphere.Matrix.Utils.Timer.Timer import Timer

from AvaSphere.Matrix.Cognition.Cognition import CognitiveProcess

load_dotenv()
logger = logging.getLogger(__name__)


class Matrix:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.cognitive = CognitiveProcess()
        self.stage     = [None] * 13

    @Timer.startAutomaticTimer("Thought")
    def process(self, ctx):
        state = []

        # Determine if the users request should be accepted.
        self.cognitive.freewill.determineAction(ctx)
        if not self.cognitive.freewill.accepted(ctx):
            return self.cognitive.freewill.denied(ctx)

        # Stage 1: Thinking about the request
        self.stage[1] = self.cognitive.process(ctx, "", "Thinking")
        if self.stage[1]:
            state.append(self.stage[1])

        # Stage 2: Clarifying what actions to take if any
        self.stage[2] = self.cognitive.process(ctx, self.stage[1], "Clarifying")
        if self.stage[2]:
            state.append(self.stage[2])

        # Stage 3: Gathering/Executing User actions if any
        self.stage[3] = self.cognitive.process(ctx, self.stage[2], "Gathering")
        if self.stage[3]:
            state.append(self.stage[3])

        # Stage 4: Getting/Defining/Executing Ava actions if any
        self.stage[4] = self.cognitive.process(ctx, self.stage[2], "Getting")
        if self.stage[4]:
            actions = self.cognitive.process(ctx, self.stage[2], "Defining")
            for action in self.stage[4]:
                result = self.cognitive.process(actions, action, "Executing")
                state.append(result)

        # Stage 5: Refining all the information
        self.stage[5] = self.cognitive.process(ctx, state, "Refining")
        if self.stage[5]:
            state.append(self.stage[5])

        # Stage 6: Reflecting on the information
        self.stage[6] = self.cognitive.process(ctx, state, "Reflecting")
        if self.stage[6]:
            state.append(self.stage[6])

        # Stage 7: Decision making
        self.stage[7] = self.cognitive.process(ctx, state, "Decision")
        if self.stage[7]:
            self.cognitive.memory.process(ctx, self.stage[7])
        return self.stage[7]

    def evaluate(self, ctx):
        stages = {
            1: "Thinking", 2: "Clarifying", 3: "Gathering",
            4: "Defining", 5: "Refining",   6: "Reflecting",
            7: "Decision"
        }

        for index, label in stages.items():
            self.cognitive.learning.evaluate(ctx, self.stage[index], label)
