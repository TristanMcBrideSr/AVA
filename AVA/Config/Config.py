##---------------------------------------------------------------------------------------------------------##
## OmniAI (PRIVATE BETA): Not installable, for proprietary model loading only.
## DO NOT UNCOMMENT OR USE unless you have private access. This will cause errors.
## Used for proprietary models including Sybil. OmniAI client NOT installable/public.
##---------------------------------------------------------------------------------------------------------##
#from OmniAI import OmniAI

import base64
import cv2
import io
import os
from dotenv import load_dotenv
from PIL import Image
import threading
from openai import OpenAI
from google import genai
from google.genai import types

from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph

load_dotenv()

class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return
        
        self.skillGraph = SkillGraph()
        self.provider = os.getenv("PROVIDER", "openai").lower()
        self.response = os.getenv("RESPONSE", self.provider).lower()
        self.vision   = os.getenv("VISION", self.provider).lower()
        
        #self.omniRModel = os.getenv("OMNI_RESPONSE_MODEL", "omni-1")
        self.gptRModel  = os.getenv("OPENAI_RESPONSE_MODEL", "gpt-4.1")
        self.genRModel  = os.getenv("GOOGLE_RESPONSE_MODEL", "gemini-2.5-flash-preview-04-17")
        #self.omniVModel = os.getenv("OMNI_VISION_MODEL", "omni-1")
        self.gptVModel  = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")
        self.genVModel  = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash-preview-04-17")

        self.gptClient  = self.getOpenAIClient() # OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.genClient  = self.getGoogleClient() # genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        #self.omniClient = self.getOmniClient()
        self.initialized = True

    def getOpenAIClient(self):
        try:
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except KeyError:
            raise KeyError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")

    def getGoogleClient(self):
        try:
            return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        except KeyError:
            raise KeyError("Google API key not found. Please set GOOGLE_API_KEY in your environment variables.")

    # def getOmniClient(self):
    #     try:
    #         return OmniAI(api_key=os.getenv("OMNI_API_KEY"))
    #     except KeyError:
    #         raise KeyError("Omni API key not found. Please set OMNI_API_KEY in your environment variables.")

    def getResponse(self, *args, **kwargs):
        responseMap = {
            #"omni":   self.getOmniResponse,
            "openai": self.getOpenAIResponse,
            "google": self.getGoogleResponse
        }
        try:
            return responseMap[self.response](*args, **kwargs)
        except KeyError:
            raise ValueError("Invalid provider: choose 'omni', 'openai', or 'google'")

    def getVision(self, *args, **kwargs):
        visionMap = {
            #"omni":   self.getOmniVision,
            "openai": self.getOpenAIVision,
            "google": self.getGoogleVision
        }
        try:
            return visionMap[self.vision](*args, **kwargs)
        except KeyError:
            raise ValueError("Invalid provider: choose 'openai' or 'google'")

    # def getOmniResponse(self, system, ctx):
    #     return self.omniClient.Responses(model=self.omniRModel, system=system, user=ctx)

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

    def isStructured(self, system, ctx):
        return self.skillGraph.isStructured(system, ctx)

    # def getOmniVision(self, system, ctx, paths, collect=5):
    #     """
    #     system: Optional system instructions (str or None)
    #     ctx: the prompt
    #     paths: str or list of str (media file paths)
    #     collect: sample every Nth frame (for videos/animations)
    #     """
    #     if isinstance(paths, str):
    #         paths = [paths]
    #     if not paths or not isinstance(paths, list):
    #         raise ValueError("paths must be a string or a list with at least one item.")
    #     contents = []
    #     if system:
    #         sys_out = self.skillGraph.handleJsonFormat("system", system)
    #         if isinstance(sys_out, list):
    #             contents.extend(sys_out)
    #         elif isinstance(sys_out, dict):
    #             contents.append(sys_out)
    #         elif isinstance(sys_out, str):
    #             #contents.append({"role": "system", "content": sys_out})
    #             contents.append(self.skillGraph.handleJsonFormat("system", sys_out))

    #     images = []
    #     for path in paths:
    #         ext = os.path.splitext(path)[1].lower()
    #         if ext in [".gif", ".webp"]:
    #             frames = self._extractFramesPIL(path, collect)
    #         elif ext in [".mp4", ".webm"]:
    #             frames = self._extractFramesVideo(path, collect)
    #         else:
    #             b64, mimeType = self._encodeImageFile(path, "jpeg")
    #             frames = [(b64, mimeType, 0)]
    #         b64, mimeType, idx = frames[0]
    #         images.append({"type": "input_image", "image_url": f"data:image/{mimeType};base64,{b64}"})

    #     user_content = [{"type": "input_text", "text": ctx}] + images
    #     input_payload = contents.copy()
    #     #input_payload.append({"role": "user", "content": user_content})
    #     input_payload.append(self.skillGraph.handleJsonFormat("user", user_content))
    #     return self.omniClient.Responses(model=self.omniVModel, input=input_payload)

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
                #contents.append({"role": "system", "content": sys_out})
                contents.append(self.skillGraph.handleJsonFormat("system", sys_out))

        images = []
        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in [".gif", ".webp"]:
                frames = self._extractFramesPIL(path, collect)
            elif ext in [".mp4", ".webm"]:
                frames = self._extractFramesVideo(path, collect)
            else:
                b64, mimeType = self._encodeImageFile(path, "jpeg")
                frames = [(b64, mimeType, 0)]
            b64, mimeType, idx = frames[0]
            images.append({"type": "input_image", "image_url": f"data:image/{mimeType};base64,{b64}"})

        user_content = [{"type": "input_text", "text": ctx}] + images
        input_payload = contents.copy()
        #input_payload.append({"role": "user", "content": user_content})
        input_payload.append(self.skillGraph.handleJsonFormat("user", user_content))
        response = self.gptClient.responses.create(
            model=self.gptVModel,
            input=input_payload
        )
        return response.output_text

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
            ext = os.path.splitext(path)[1].lower()
            if ext in [".gif", ".webp"]:
                frames = self._extractFramesPIL(path, collect)
            elif ext in [".mp4", ".webm"]:
                frames = self._extractFramesVideo(path, collect)
            else:
                b64, mimeType = self._encodeImageFile(path, "jpeg")
                frames = [(b64, mimeType, 0)]
            b64, mimeType, idx = frames[0]
            # Correct blob part for Gemini
            images.append(
                genai.types.Part(
                    inline_data=genai.types.Blob(
                        mime_type=f"image/{mimeType}",
                        data=base64.b64decode(b64)
                    )
                )
            )

        # Always use Part(text=...)
        text_parts = [genai.types.Part(text=ctx)]

        # Gemini requires images first, then prompt
        parts = images + text_parts
        contents = [genai.types.Content(role="user", parts=parts)]

        config_args = dict(response_mime_type="text/plain")
        if system is not None:
            config_args['system_instruction'] = [system]
        generate_content_config = genai.types.GenerateContentConfig(**config_args)

        response = self.genClient.models.generate_content(
            model=self.genVModel,
            contents=contents,
            config=generate_content_config,
        )
        return response.text

    def _encodeImageFile(self, path, mimeType="jpeg"):
        with open(path, "rb") as imgFile:
            data = imgFile.read()
            return base64.b64encode(data).decode("utf-8"), mimeType

    def _extractFramesPIL(self, path, collect=5):
        with Image.open(path) as img:
            frame_count = getattr(img, "n_frames", 1)
            indices = list({0, frame_count - 1} | set(range(0, frame_count, collect)))
            indices = sorted(idx for idx in indices if idx < frame_count)
            frames = []
            for idx in indices:
                try:
                    img.seek(idx)
                except EOFError:
                    continue
                with io.BytesIO() as buffer:
                    img.convert("RGB").save(buffer, format="PNG")
                    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    frames.append((b64, "png", idx))
            return frames

    def _extractFramesVideo(self, path, collect=5):
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        indices = list({0, total - 1} | set(range(0, total, collect)))
        indices = sorted(idx for idx in indices if idx < total)
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            success, image = cap.read()
            if not success:
                continue
            success, buffer = cv2.imencode(".jpg", image)
            if not success:
                continue
            b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
            frames.append((b64, "jpeg", idx))
        cap.release()
        return frames

    def _unsupportedFormat(self, ext):
        raise ValueError(f"File format '{ext}' is not supported for Vision frame extraction")
