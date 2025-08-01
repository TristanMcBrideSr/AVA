
import os
import threading
from dotenv import load_dotenv
from HoloAI import HoloAI

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
        self.holoAI   = HoloAI()
        self.provider = os.getenv("PROVIDER", "openai").lower()
        self.response = os.getenv("RESPONSE", self.provider).lower()
        self.vision   = os.getenv("VISION", self.provider).lower()

        self.openai = {
            'response': os.getenv("OPENAI_RESPONSE_MODEL", "gpt-4.1"),
            'vision':   os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")
        }
        self.google = {
            'response': os.getenv("GOOGLE_RESPONSE_MODEL", "gemini-2.5-flash"),
            'vision':   os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")
        }
        self.groq = {
            'response': os.getenv("GROQ_RESPONSE_MODEL", "llama-3.3-70b-versatile"),
            'vision':   os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
        }
        self.anthropic = {
            'response': os.getenv("ANTHROPIC_RESPONSE_MODEL", "claude-3.5-sonnet"),
            'vision':   os.getenv("ANTHROPIC_VISION_MODEL", "claude-3.5-sonnet")
        }

        self.providerMap = {
            "openai": self.openai,
            "google": self.google,
            "groq":   self.groq,
            "anthropic": self.anthropic,
        }
        self.initialized = True

    def getResponse(self, system, user):
        return self.getHoloAI(mode='response', system=system, user=user)

    def getVision(self, system, user, paths, collect=5):
        return self.getHoloAI(mode='vision', system=system, user=user, paths=paths, collect=collect)

    def getHoloAI(self, **kwargs):
        mode    = kwargs.get('mode', 'response')
        system  = kwargs.get('system')
        user    = kwargs.get('user')
        paths   = kwargs.get('paths')
        collect = kwargs.get('collect', 5)

        if mode not in ('response', 'vision'):
            raise ValueError("mode must be either 'response' or 'vision'")

        providerKey = getattr(self, mode)
        provider = self.providerMap[providerKey]
        model = provider[mode]

        funcMap = {
            'response': lambda: self.holoAI.Response(system=system, input=user, model=model),
            'vision': lambda: self.holoAI.Vision(system=system, input=user, model=model, paths=paths, collect=collect)
        }
        return funcMap[mode]()


##---------------------------------------------------------------------------------------------------------##
## We left this old Config class and corresponding config files for each provider here for reference, 
## on how it was done before we created the HoloAI pip package.
## This is not used in the current implementation, but you can refer to it if needed.
##---------------------------------------------------------------------------------------------------------##
## OmniAI (PRIVATE BETA): Not installable, for proprietary model loading only.
## DO NOT SET TO TRUE OR USE unless you have private access. This will cause errors.
## Used for proprietary models including Sybil. OmniAI client NOT installable/public.
##---------------------------------------------------------------------------------------------------------##

# import os
# import threading

# from dotenv import load_dotenv

# from Config.Components.OmniAIConfig import OmniAIConfig
# from Config.Components.OpenAIConfig import OpenAIConfig
# from Config.Components.GoogleConfig import GoogleConfig
# from Config.Components.GroqConfig import GroqConfig

# load_dotenv()
# OMNI_ACCESS = os.getenv("OMNI_ACCESS", "False")  == 'True'  # Set to True in the .env if you have access to OmniAI and its models

# class Config:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:
#                 if not cls._instance:
#                     cls._instance = super(Config, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if getattr(self, 'initialized', False):
#             return
#         self.provider = os.getenv("PROVIDER", "openai").lower()
#         self.response = os.getenv("RESPONSE", self.provider).lower()
#         self.vision   = os.getenv("VISION", self.provider).lower()
#         if OMNI_ACCESS:
#             self.omni = OmniAIConfig()
#         else:
#             self.omni = None
#         self.openai = OpenAIConfig()
#         self.google = GoogleConfig()
#         self.groq   = GroqConfig()

#         self.providerMap = {
#             "openai": self.openai,
#             "google": self.google,
#             "groq":   self.groq
#         }
#         if OMNI_ACCESS:
#             self.providerMap["omni"] = self.omni
#         self.initialized = True

#     def getResponse(self, *args, **kwargs):
#         provider = self.providerMap[self.response]
#         return provider.getResponse(*args, **kwargs)

#     def getVision(self, *args, **kwargs):
#         provider = self.providerMap[self.vision]
#         return provider.getVision(*args, **kwargs)

