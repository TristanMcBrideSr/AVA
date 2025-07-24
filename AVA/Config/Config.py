##---------------------------------------------------------------------------------------------------------##
## OmniAI (PRIVATE BETA): Not installable, for proprietary model loading only.
## DO NOT SET TO TRUE OR USE unless you have private access. This will cause errors.
## Used for proprietary models including Sybil. OmniAI client NOT installable/public.
##---------------------------------------------------------------------------------------------------------##

import os
import threading

from dotenv import load_dotenv

from Config.Components.OmniAIConfig import OmniAIConfig
from Config.Components.OpenAIConfig import OpenAIConfig
from Config.Components.GoogleConfig import GoogleConfig
from Config.Components.GroqConfig import GroqConfig

load_dotenv()
OMNI_ACCESS = os.getenv("OMNI_ACCESS", "False")  == 'True'  # Set to True in the .env if you have access to OmniAI and its models

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
        self.provider = os.getenv("PROVIDER", "openai").lower()
        self.response = os.getenv("RESPONSE", self.provider).lower()
        self.vision   = os.getenv("VISION", self.provider).lower()
        if OMNI_ACCESS:
            self.omni = OmniAIConfig()
        else:
            self.omni = None
        self.openai = OpenAIConfig()
        self.google = GoogleConfig()
        self.groq   = GroqConfig()

        self.providerMap = {
            "openai": self.openai,
            "google": self.google,
            "groq":   self.groq
        }
        if OMNI_ACCESS:
            self.providerMap["omni"] = self.omni
        self.initialized = True

    def getResponse(self, *args, **kwargs):
        provider = self.providerMap[self.response]
        return provider.getResponse(*args, **kwargs)

    def getVision(self, *args, **kwargs):
        provider = self.providerMap[self.vision]
        return provider.getVision(*args, **kwargs)
