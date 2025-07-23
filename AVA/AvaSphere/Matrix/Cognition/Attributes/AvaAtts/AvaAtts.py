
from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Sentiment.AvaSentiment import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Freewill.AvaFreewill import Freewill
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Freewill.AvaFreewill import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Activations.AvaActivations import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Identity.AvaIdentity import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Family.AvaFamily import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Speech.AvaSpeech import *
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Components.Traits.AvaTraits import *



class AvaAtts:
    def __init__(self, parent):
        self._initComponents(parent)

    def _initComponents(self, parent):
        self.parent    = parent
        self.db        = Database()
        self.components = {
            'freewill-activated': ActivateFreewill(self), 'memory-activated':    ActivateMemory(self),    'learning-activated':    ActivateLearning(self), 
            'security-activated': ActivateSecurity(self), 'profanity-activated': ActivateProfanity(self), 'fillerwords-activated': ActivateFillerWords(self),
            'family-activated':   ActivateFamily(self),   'emotions-activated':  ActivateEmotions(self),  'feelings-activated':    ActivateFeelings(self),

            'freewill':  Freewill(self),  'emotions':    Emotions(self),    'feelings': Feelings(self),   'opinions': Opinions(self),
            'creator':   Creator(self),   'creation':    Creation(self),    'Version':  Version(self),
            'name':      Name(self),      'type':        Type(self),        'gender': Gender(self),
            'persona':   Persona(self),   'personality': Personality(self), 'motto': Motto(self),
            'language':  Language(self),  'accent':      Accent(self),
            'profanity': Profanity(self), 'fillerwords': FillerWords(self),
            'family':    Family(self),    'voice':       Voice(self)
        }

    def getMetaData(self):
        data = {}
        for name, component in self.components.items():
            if component and hasattr(component, "_metaData") and callable(component._metaData):
                data[name] = component._metaData()
        return data

    def process(self, content):
        for component in self.components.values():
            if hasattr(component, "process") and callable(component.process):
                completion = component.process(content)
                if completion:
                    return completion
        return None

    def getCurrentAttribute(self, attrName):
        component = self.components.get(attrName.lower())
        if component and hasattr(component, "getCurrent") and callable(component.getCurrent):
            return component.getCurrent()
        return f"Attribute '{attrName}' not found or does not support getCurrent."

    def getPreviousAttribute(self, attrName):
        component = self.components.get(attrName.lower())
        if component and hasattr(component, "getPrevious") and callable(component.getPrevious):
            return component.getPrevious()
        return f"Attribute '{attrName}' not found or does not support getPrevious."

    def getIntensity(self, attrName):
        component = self.components.get(attrName.lower())
        if component and hasattr(component, "getIntensity") and callable(component.getIntensity):
            return component.getIntensity()
        return f"Attribute '{attrName}' not found or does not support getIntensity."

    # def getEmotions(self):
    #     return self.components['emotions'].getEmotions()

    # def getFeelings(self, userName=None):
    #     return self.components['feelings'].getFeelings(userName)

    # def getOpinions(self, userName=None):
    #     return self.components['opinions'].getOpinions(userName)

    # def getVoiceInstructions(self, content):
    #     return self.components['voice'].getVoiceInstructions(content)

    def getFamilyMembers(self):
        return self.components['family'].getFamilyMembers()

    def getValidFamilyNames(self):
        return self.components['family'].getValidFamilyNames()

    # def deleteFeelings(self, userName=None):
    #     return self.components['feelings'].deleteFeelings(userName)

    # def deleteOpinions(self, userName=None):
    #     return self.components['opinions'].deleteOpinions(userName)
