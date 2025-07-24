
from pathlib import Path
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

from AvaSphere.Echo.Echo import Echo
from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Cognition.Router.Router import Router
from SyncLink import SyncLink
from SynLrn import SynLrn

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)


class Learning:
    STAGES = [
        "thinking", "clarifying", "gathering",
        "defining", "refining",   "reflecting", "decision"
    ]

    def __init__(self):
        self.attributes       = Attributes()
        self.db               = Database()
        self.learningDir      = self.db.learningDir
        self.knowledgeBaseDir = self.db.knowledgeBaseDir
        self.dbName           = 'Learned.db'
        # self.neuralLink      = NeuralLink()
        self.echo             = Echo()
        self.router           = Router()
        self.syncLink         = SyncLink(githubRepo="TristanMcBrideSr/SkillForge", repoFolder="SkillForge/KnowledgeBase", syncDir=self.knowledgeBaseDir)
        self.syncActivated    = os.getenv("ACTIVATE_KNOWLEDGE_SYNC", "False")
        if self.syncActivated:
            self.syncLink.startSync(override=True)  # Download the latest KnowledgeBase the from SkillForge
        # self.getLearningLink = self.neuralLink.getLink("learningLink")
        # self.getLearningCore = self.neuralLink.getCore("learningCore")
        # We need to import the KnowledgeBase after the Sync so that it can be synced and updated first before being used
        import AvaSphere.Matrix.Cognition.Knowledge.Learning.KnowledgeBase.KnowledgeBase as KnowledgeBase
        self.synLearn    = SynLrn(stages=Learning.STAGES, learningDir=self.learningDir, dbName=self.dbName, fallbacks=self.fallbacks, knowledgeBase=KnowledgeBase)

        #self.viewDatabase()

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def viewDatabase(self, stage: str = None):
        self.synLearn.viewDatabase(stage)

    # The higher you set the minScore, the more accurate the results will be and the less results you will get. ideal setting is 60-75
    def retrieveStage(self, ctx: str, stage: str, minScore: int = 40, fallbackCount: int = 5, structured: bool = False):
        results = self.synLearn.retrieveStage(ctx, stage, minScore, fallbackCount)
        if structured:
            out = []
            for entry in results:
                ctxText, resText = self.synLearn.splitEntry(entry)
                out.append(self._handleJsonFormat("user", ctxText))
                out.append(self._handleJsonFormat("assistant", resText))
            return out
        else:
            result = "\n\n".join([f"Example {i + 1}:\n{entry}" for i, entry in enumerate(results)])
            #print (f"\n[RETRIEVED STAGE] Stage: {stage.capitalize()}\n{result}\n")
            return result

    def thinking(self, ctx: str, structured: bool = False):   return self.retrieveStage(ctx, "thinking", structured=structured)
    def clarifying(self, ctx: str, structured: bool = False): return self.retrieveStage(ctx, "clarifying", structured=structured)
    def gathering(self, ctx: str, structured: bool = False):  return self.retrieveStage(ctx, "gathering", structured=structured)
    def defining(self, ctx: str, structured: bool = False):   return self.retrieveStage(ctx, "defining", structured=structured)
    def refining(self, ctx: str, structured: bool = False):   return self.retrieveStage(ctx, "refining", structured=structured)
    def reflecting(self, ctx: str, structured: bool = False): return self.retrieveStage(ctx, "reflecting", structured=structured)
    def decision(self, ctx: str, structured: bool = False):   return self.retrieveStage(ctx, "decision", structured=structured)

    def _getShowProcess(self):
        load_dotenv(override=True)
        return os.getenv('SHOW_LEARNING_PROCESS', 'False') == 'True'

    def _getActivation(self, key, envVar=None):
        load_dotenv(override=True)
        envVar     = envVar if envVar else f"ACTIVATE_{key.upper()}"
        attrActive = self.attributes.getCurrentAttribute("Ava", f"{key}-Activated", "False") == "True"
        envActive = os.getenv(envVar, "False") == "True"
        return envActive or attrActive

    def evaluate(self, ctx: str, response: str, stage: str) -> str:
        isLearningActivated = self._getActivation("Learning")
        if not response or response == "None" or response == ["None"]:
            if isLearningActivated:
                print(f"[LEARNED NOT ADDED] Stage: '{stage}' | Context: '{ctx}' | Response: '{response}'")
            return
        stage = stage.strip().lower()
        if stage not in self.STAGES:
            return
        correct = self._humanEvaluation(ctx, response, stage) if isLearningActivated else self._selfEvaluation(ctx, response, stage)
        if correct == "yes":
            self.synLearn.addToLearned(stage, ctx, response)
            if isLearningActivated:
                #self.echo.synthesize(f"I'm glad to hear my {stage} was correct, I'll add it to what I've learned.")
                print(f"I'm glad to hear my {stage} was correct, I'll add it to what I've learned.")
            return f"I'm glad to hear my {stage} was correct, I'll add it to what I've learned."
        else:
            if isLearningActivated:
                #self.echo.synthesize(f"I'm sorry my {stage} was incorrect, I will not add it to what I've learned.")
                print(f"I'm sorry my {stage} was incorrect, I will not add it to what I've learned.")
            return f"I'm sorry my {stage} was incorrect, I will not add it to what I've learned."

    def _humanEvaluation(self, ctx: str, response: str, stage: str) -> str:
        print(f"\n[HUMAN EVALUATION] Stage: {stage.capitalize()}")
        print(f"Context:\n{ctx}\n")
        print(f"Response:\n{response}\n")
        while True:
            self.echo.synthesize(f"Was my {stage} logic correct.")
            userInput = self.echo.recognize().strip().lower()
            # userInput = input(f"Was my {stage} logic correct (Yes/No): ").strip().lower()
            if userInput in ("yes", "no"):
                return userInput
            self.echo.synthesize("Please respond with 'yes' or 'no'.")
            #print("Please respond with 'yes' or 'no'.")

    def _selfEvaluation(self, ctx: str, response, stage: str) -> str:
        """
        Performs self-evaluation of the response using a neural process (In this case, a simple OpenAI API call).
        It checks if the response is appropriate and accurate for the given context and stage.
        If the response is a list, it joins the elements into a single string.
        If the response is not a string, it converts it to a string.
        It then processes the response and returns 'yes' or 'no' based on the evaluation.
        """
        if isinstance(response, list):
            response = " ".join(str(r) for r in response if isinstance(r, str))
        # decision = self.neuralLink.runNeuralProcess("learning", self.getLearningLink, self.getLearningCore, ctx, response, stage)
        # decision = self._process(ctx, response, stage) # Uncomment this line if you want to use the router for self-evaluation
        decision = "no"  # Can be replaced with self._process(ctx, response, stage) if you want to use the router or change to
        # yes to simulate a positive response or no if you want to simulate a negative response for testing purposes
        if self._getShowProcess():
            print(f"\n[SELF EVALUATION] Stage: {stage.capitalize()}, Decision: {decision}\n")
        return "yes" if "yes" in decision.lower() else "no"

    def _process(self, ctx: str, response, stage: str) -> str:
        """
        Processes the context and response using the router to get a response from the AI assistant.
        The system message provides instructions for the AI assistant, and the user message contains the context and response to evaluate.
        It returns the AI's response, which is either 'yes' or 'no'.
        """
        system = (
            "You are an AI assistant that evaluates responses based on the context provided. "
            "Your task is to determine if the response is appropriate and accurate for the given context. "
            "Answer with 'yes' or 'no'."
        )
        user = (
            f"Evaluate this response in the context of '{stage}' logic:\n\n"
            f"Context: {ctx}\n\nResponse: {response}\n\n"
            "Is the response appropriate and accurate with no errors? Answer with 'yes' or 'no'."
        )
        return self.router.getResponse(system, user)

    def _handleJsonFormat(self, role="user", content=""):
        return self.synLearn.handleJsonFormat(role, content)

    def _handleTypedFormat(self, role="user", content=""):
        return self.synLearn.handleTypedFormat(role, content)

    def getUserName(self, user):
        users = {
            "current":  self.attributes.getCurrentAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User")),
            "previous": self.attributes.getPreviousAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User"))
        }
        return users.get(user, os.getenv("DEFAULT_USER_NAME", "User"))

    def fallbacks(self, fallbackType: str) -> list:
        currentUser = self.getUserName("current")
        fallbackMap = {
            "thinking": [
            ],
            "clarifying": [
                "user:\nCan you generate digital sounds?\n\nassistant:\n['creationSkill(\"create-self-skill\", \"create a skill to generate digital sounds\")']",
                "user:\nCan you create a relaxing ambient loop?\n\nassistant:\n['creationSkill(\"create-self-skill\", \"create a skill to generate relaxing ambient sound loops\")']",
                "user:\nWhat can you do?\n\nassistant:\nNone",
                "user:\nHello\n\nassistant:\nNone",
            ],
            "gathering": [],
            "defining": [],
            "refining": [],
            "reflecting": [],
            "decision": []
        }
        return fallbackMap.get(fallbackType.lower(), [])
