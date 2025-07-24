import os
import threading
from dotenv import load_dotenv
from openai import OpenAI

from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph
from AvaSphere.Matrix.Utils.Media import Media
load_dotenv()

class OpenAIConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(OpenAIConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return
        
        self.skillGraph = SkillGraph()
        
        self._setModels()
        self._setClients()
        self.initialized = True

    def _setModels(self):
        self.gptRModel  = os.getenv("OPENAI_RESPONSE_MODEL", "gpt-4.1")
        self.gptVModel  = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")

    def _setClients(self):
        self.gptClient = self.getOpenAIClient()

    def getOpenAIClient(self):
        try:
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except KeyError:
            raise KeyError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")

    def getResponse(self, *args, **kwargs):
        """
        system: Optional system instructions (str or None)
        ctx: the prompt
        """
        return self.getOpenAIResponse(*args, **kwargs)

    def getVision(self, *args, **kwargs):
        """
        system: Optional system instructions (str or None)
        ctx: the prompt
        paths: str or list of str (media file paths)
        collect: sample every Nth frame (for videos/animations)
        """
        return self.getOpenAIVision(*args, **kwargs)

    def getOpenAIResponse(self, system, ctx):
        isStructured = self.isStructured(system, ctx)
        ctxMap = {
            True:  lambda: self.getStructuredResponse(system, ctx),
            False: lambda: self.getUnstructuredResponse(system, ctx)
        }
        return ctxMap[isStructured]()

    def getStructuredResponse(self, system, ctx):
        contents = []
        contents.extend(self.skillGraph.handleJsonExamples([
            ("system", system), 
            ("user", ctx)
        ]))
        return self.gptClient.responses.create(
            model=self.gptRModel,
            input=contents,
        ).output_text

    def getUnstructuredResponse(self, system, ctx):
        return self.gptClient.responses.create(
            model=self.gptRModel,
            instructions=system, 
            input=ctx
        ).output_text

    def isStructured(self, system, ctx):
        return self.skillGraph.isStructured(system, ctx)

    def getOpenAIVision(self, system, ctx, paths, collect=5):
        """
        system: Optional system instructions (str or None)
        ctx: the prompt
        paths: str or list of str (media file paths)
        collect: sample every Nth frame (for videos/animations)
        """
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")
        contents = []
        if system:
            sys_out = self.skillGraph.handleJsonFormat("system", system)
            if isinstance(sys_out, list):
                contents.extend(sys_out)
            elif isinstance(sys_out, dict):
                contents.append(sys_out)
            elif isinstance(sys_out, str):
                contents.append(self.skillGraph.handleJsonFormat("system", sys_out))

        images = []
        for path in paths:
            frames = Media.getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({"type": "input_image", "image_url": f"data:image/{mimeType};base64,{b64}"})

        user_content = [{"type": "input_text", "text": ctx}] + images
        input_payload = contents.copy()
        input_payload.append(self.skillGraph.handleJsonFormat("user", user_content))
        response = self.gptClient.responses.create(
            model=self.gptVModel,
            input=input_payload
        )
        return response.output_text
