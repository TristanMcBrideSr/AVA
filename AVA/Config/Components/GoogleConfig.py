import os
import threading
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types

from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph
from AvaSphere.Matrix.Utils.Media import Media
load_dotenv()

class GoogleConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(GoogleConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.skillGraph = SkillGraph()

        self._setModels()
        self._setClients()
        self.initialized = True

    def _setModels(self):
        self.genRModel = os.getenv("GOOGLE_RESPONSE_MODEL", "gemini-2.5-flash")
        self.genVModel = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")

    def _setClients(self):
        self.genClient = self.getGoogleClient()

    def getGoogleClient(self):
        try:
            return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        except KeyError:
            raise KeyError("Google API key not found. Please set GOOGLE_API_KEY in your environment variables.")

    def getResponse(self, *args, **kwargs):
        return self.getGoogleResponse(*args, **kwargs)

    def getVision(self, *args, **kwargs):
        return self.getGoogleVision(*args, **kwargs)

    def getGoogleResponse(self, system, ctx):
        model = self.genRModel
        contents = []
        contents.append(self.skillGraph.handleTypedFormat("user", ctx))
        config_args = dict(response_mime_type="text/plain")
        if system is not None:
            config_args['system_instruction'] = [system]
        generate_content_config = types.GenerateContentConfig(**config_args)
        response = self.genClient.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return response.text

    def getGoogleVision(self, system, ctx, paths, collect=5):
        """
        system: Optional system instructions (str or None)
        ctx: user prompt (str)
        paths: str or list of str (media file paths)
        collect: sample every Nth frame (for videos/animations)
        """
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        # Image part assembly
        images = []
        for path in paths:
            frames = Media.getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            # Correct blob part for Gemini
            images.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type=f"image/{mimeType}",
                        data=base64.b64decode(b64)
                    )
                )
            )

        # Always use Part(text=...)
        text_parts = [types.Part(text=ctx)]

        # Gemini requires images first, then prompt
        parts = images + text_parts
        contents = [types.Content(role="user", parts=parts)]

        config_args = dict(response_mime_type="text/plain")
        if system is not None:
            config_args['system_instruction'] = [system]
        generate_content_config = types.GenerateContentConfig(**config_args)

        response = self.genClient.models.generate_content(
            model=self.genVModel,
            contents=contents,
            config=generate_content_config,
        )
        return response.text
