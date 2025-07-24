import os
import threading
from dotenv import load_dotenv
from groq import Groq

from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph
from AvaSphere.Matrix.Utils.Media import Media
load_dotenv()

class GroqConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(GroqConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.skillGraph = SkillGraph()

        self._setModels()
        self._setClients()
        self.initialized = True

    def _setModels(self):
        self.groqRModel = os.getenv("GROQ_RESPONSE_MODEL", "llama-3.3-70b-versatile")
        self.groqVModel = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    def _setClients(self):
        self.groqClient = self.getGroqClient()

    def getGroqClient(self):
        try:
            return Groq(api_key=os.getenv("GROQ_API_KEY"))
        except KeyError:
            raise KeyError("Groq API key not found. Please set GROQ_API_KEY in your environment variables.")

    def getResponse(self, *args, **kwargs):
        return self.getGroqResponse(*args, **kwargs)

    def getVision(self, *args, **kwargs):
        return self.getGroqVision(*args, **kwargs)

    def getGroqResponse(self, system, ctx):
        """
        system: Optional system instructions (str or None)
        ctx: the prompt
        """
        contents = []
        contents.extend(self.skillGraph.handleJsonExamples([
            ("system", system), 
            ("user", ctx)
        ]))
        response = self.groqClient.chat.completions.create(
            model=self.groqRModel,
            messages=contents,
        )
        return response.choices[0].message.content

    def getGroqVision(self, system, ctx, paths, collect=5):
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

        user_content = [{"type": "text", "text": ctx}] + images
        input_payload = contents.copy()
        input_payload.append(self.skillGraph.handleJsonFormat("user", user_content))
        response = self.groqClient.chat.completions.create(
            model=self.groqVModel,
            messages=input_payload
        )
        return response.choices[0].message.content
