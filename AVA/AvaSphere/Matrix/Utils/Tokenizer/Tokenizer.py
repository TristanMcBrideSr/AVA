
import tiktoken
from AvaSphere.Matrix.Cognition.Attributes.Attributes import Attributes
import os
from dotenv import load_dotenv

load_dotenv()

class Tokenizer:
    def __init__(self):
        self.tokenizer  = tiktoken.get_encoding("cl100k_base")
        self.attributes = Attributes()

    def calculateTokens(self, name=None, processType=None, content=None):
        content    = str(content)
        tokens     = self.tokenizer.encode(content)
        tokenCount = len(tokens)

        if name:
            name = name.lower()
            selfName = self.getSelfName
        
            if name == selfName:
                displayName = name.title()
                print(f"\n{displayName} {processType} Received:\n  {tokenCount} Tokens\n")
            else:
                displayName = name.title()
                print(f"\n{displayName} Used:\n  {tokenCount} Tokens\n")
        else:
            print(f"Used:\n  {tokenCount} Tokens")

    @property
    def getSelfName(self):
        defaultSelfName = os.getenv("ASSISTANT_NAME", "AVA")
        return self.attributes.getCurrentAttribute("Ava",'Name', defaultSelfName).lower()