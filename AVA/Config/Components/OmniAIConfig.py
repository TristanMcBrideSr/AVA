##---------------------------------------------------------------------------------------------------------##
## OmniAI (PRIVATE BETA): Not installable, for proprietary model loading only.
## DO NOT UNCOMMENT OR USE unless you have private access. This will cause errors.
## Used for proprietary models including Sybil. OmniAI client NOT installable/public.
##---------------------------------------------------------------------------------------------------------##
#from OmniAI import OmniAI

import os
import threading
from dotenv import load_dotenv
from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph
from AvaSphere.Matrix.Utils.Media import Media
load_dotenv()

OMNI_ACCESS = os.getenv("OMNI_ACCESS", "False") == 'True'  # Set to True in the .env if you have access to OmniAI and its models
if OMNI_ACCESS:
    try:
        from OmniAI import OmniAI  # Import only if OMNI_ACCESS is True
    except ImportError:
        pass


class OmniAIConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(OmniAIConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return
        
        self.skillGraph = SkillGraph()
        
        self._setModels()
        self._setClients()
        self.initialized = True

    def _setModels(self):
        if OMNI_ACCESS:
            self.omniRModel = os.getenv("OMNI_RESPONSE_MODEL", "omni-1")
            self.omniVModel = os.getenv("OMNI_VISION_MODEL", "omni-1")

    def _setClients(self):
        if OMNI_ACCESS:
            self.omniClient = self.getOmniClient()

    def getOmniClient(self):
        try:
            return OmniAI(api_key=os.getenv("OMNI_API_KEY"))
        except KeyError:
            raise KeyError("Omni API key not found. Please set OMNI_API_KEY in your environment variables.")

    def getResponse(self, *args, **kwargs):
        if OMNI_ACCESS:
            return self.getOmniResponse(*args, **kwargs)
        raise ValueError("OmniAI access is not enabled.")

    def getVision(self, *args, **kwargs):
        if OMNI_ACCESS:
            return self.getOmniVision(*args, **kwargs)
        raise ValueError("OmniAI access is not enabled.")

    def getOmniResponse(self, system, ctx):
        return self.omniClient.Responses(model=self.omniRModel, system=system, user=ctx)

    def getOmniVision(self, system, ctx, paths, collect=5):
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
        return self.omniClient.Responses(model=self.omniVModel, input=input_payload)
