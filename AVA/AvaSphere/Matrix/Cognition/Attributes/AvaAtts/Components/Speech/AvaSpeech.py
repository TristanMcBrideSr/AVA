import os
import re
from dotenv import load_dotenv
import logging
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile
#from AvaSphere.Matrix.Cognition.NeuralLink.NeuralLink import NeuralLink

load_dotenv()
logger = logging.getLogger(__name__)


class Linguistics:
    def __init__(self, parent, attrName, defaultValue, promptText, changePrefix, validOptions=None, transformFunc=None, noneAllowed=True):
        self.db            = parent.db
        self.avaProfile    = AvaProfile()
        self.attrName      = attrName
        self.defaultValue  = defaultValue
        self.promptText    = promptText
        self.changePrefix  = changePrefix  # Can be a string or a list of strings.
        self.validOptions  = validOptions   # List of valid values or None for any value.
        self.transformFunc = transformFunc if transformFunc is not None else lambda x: x
        self.noneAllowed   = noneAllowed
        self.currentValue  = self.avaProfile.loadAttribute(attrName, "current", defaultValue)
        self.previousValue = self.avaProfile.loadAttribute(attrName, "previous", defaultValue)
        if self.currentValue == "Not Set":
            self.checkForAttribute()

    def getCurrent(self):
        return self.currentValue

    def getPrevious(self):
        return self.previousValue

    def _metaData(self):
        return {"className": self.attrName, "description": f"Allows me to change my {self.attrName.lower()}."}

    def saveAttribute(self, newValue):
        previousValue = self.currentValue
        self.avaProfile.saveAttribute(self.attrName, newValue, previousValue)
        self.previousValue, self.currentValue = previousValue, newValue

    def process(self, content):
        newValue = None
        # Check if content starts with any of the accepted change prefixes.
        if isinstance(self.changePrefix, list):
            for prefix in self.changePrefix:
                if content.startswith(prefix):
                    newValue = content.replace(prefix, "", 1).strip()
                    break
        else:
            if content.startswith(self.changePrefix):
                newValue = content.replace(self.changePrefix, "", 1).strip()

        if newValue is not None:
            newValue = self.transformFunc(newValue)
            if self.validOptions is not None and newValue not in self.validOptions:
                return f"Invalid {self.attrName.lower()} provided. Please choose from {self.validOptions}."
            if newValue != self.currentValue:
                self.saveAttribute(newValue)
                return f"{self.attrName} changed to {newValue}"
            return f"{self.attrName} is already set to {newValue}."

        # Process preset commands.
        commands = {
            f"reset your {self.attrName.lower()}": self.defaultValue,
            f"switch your {self.attrName.lower()} back": self.previousValue
        }
        targetValue = commands.get(content)
        if targetValue is not None:
            if self.currentValue != targetValue:
                self.saveAttribute(targetValue)
                action = "reset to" if content.startswith("reset") else "switched to"
                return f"{self.attrName} {action} {targetValue}"
            return f"{self.attrName} is already {targetValue}"

    def checkForAttribute(self):
        if self.currentValue == self.defaultValue:
            while True:
                print(self.promptText)
                userInput = input().strip()
                if userInput:
                    newValue = self.transformFunc(userInput)
                    if newValue == "None":
                        if self.noneAllowed:
                            self.saveAttribute("None")
                            print(f"I won't use any {self.attrName.lower()}s.")
                            break
                        else:
                            print(f"Invalid input. Please provide a valid {self.attrName.lower()} (not 'None').")
                            continue
                    if self.validOptions is not None and newValue not in self.validOptions:
                        print(f"Invalid {self.attrName.lower()} provided. Please choose from {self.validOptions}.")
                        continue
                    self.saveAttribute(newValue)
                    print(f"I'm all set to use {newValue} as my {self.attrName.lower()}.")
                    break
                else:
                    print(f"Please provide a valid {self.attrName.lower()}.")


class Paralinguistics:
    def __init__(self, parent=None, attributeName=None, defaultIntensity=None, intensityPrefix=None):
        self.db               = parent.db
        self.avaProfile       = AvaProfile()
        self.attributeName    = attributeName
        self.defaultIntensity = defaultIntensity
        self.intensityPrefix  = intensityPrefix

        # Load current intensity
        self.currentIntensity    = self.avaProfile.loadAttribute(attributeName, "intensity", defaultIntensity)

    def getCurrent(self):
        return self.getIntensity()

    def getPrevious(self):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def getIntensity(self):
        self.currentIntensity = self.avaProfile.loadAttribute(self.attributeName, "intensity", self.defaultIntensity)
        return self.currentIntensity

    def _metaData(self):
        return {"className": self.attributeName, "description": f"Controls the intensity of {self.attributeName.lower()}."}

    def saveIntensity(self, intensity):
        if isinstance(intensity, int):
            self.avaProfile.saveAttribute(self.attributeName, intensity)
        else:
            print(f"Invalid intensity value: {intensity}. Expected an integer.")

    def extractIntensity(self, content):
        match = re.search(r'\d+', content)
        if match:
            return int(match.group())
        return None

    def process(self, content):
        if content.startswith(self.intensityPrefix):
            intensity = self.extractIntensity(content)
            if intensity is not None:
                self.saveIntensity(intensity)
                self.currentIntensity = intensity
                return f"{self.attributeName} intensity set to {intensity}"
        return None



class Accent(Linguistics):
    def __init__(self, parent):
        promptText   = "I don't know what accent to use. Please provide an accent or type 'None' to use no accent:"
        changePrefix = "change your accent to"
        super().__init__(parent, "Accent", "British", promptText, changePrefix,
                         validOptions=None, transformFunc=lambda x: x.capitalize(), noneAllowed=True)


class Language(Linguistics):
    def __init__(self, parent):
        promptText     = "I don't know what language to use. Please provide a language (e.g., English, Spanish, French):"
        changePrefixes = ["change your language to", "lets speak in", "speak in"]
        super().__init__(parent, "Language", "English", promptText, changePrefixes,
                         validOptions=None, transformFunc=lambda x: x.capitalize(), noneAllowed=False)


class FillerWords(Paralinguistics):
    def __init__(self, parent):
        intensityPrefix = "set your filler words intensity to"
        super().__init__(parent, "FillerWords", 50, intensityPrefix)


class Profanity(Paralinguistics):
    def __init__(self, parent):
        intensityPrefix = "set your profanity intensity to"
        super().__init__(parent, "Profanity", 50, intensityPrefix)


class Voice:
    def __init__(self, parent=None):
        self.parent      = parent
        self.avaProfile  = AvaProfile()
        ## Implementation details are proprietary to Sybil's system and cannot be shared.
        # You can substitute this with OpenAI or Google API calls or any other service.
        # self.neuralLink  = NeuralLink()
        # self.getLink     = self.neuralLink.getLink("contentLink")
        # self.getCore     = self.neuralLink.getCore("contentCore")

    def _metaData(self):
        return {"className": "Voice", "description": "Allows me to adjust my voice profile."}

    def getCurrent(self):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def getPrevious(self):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def process(self, content):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def getSynthesisMode(self):
        load_dotenv(override=True)
        return os.getenv("SET_SYNTHESIS", "Standard")
    
    def getVoiceInstructions(self, content, logic=None, temp=None, tokens=None):
        synthesisMode = self.getSynthesisMode()
        # if synthesisMode == "Advanced":
        #     #print(f"Processing Voice content: {content}")
        #     system = (
        #         "Based on the user input define these categories\n" +
        #         self.getVoiceCategories() +
        #         "Dont not respond to the user in any kind of way besides voice instructions or None if none are needed:\n\n" +
        #         f" Follow the examples and dont use Output just the final:\n\n{self.getVoiceExamples()}"
        #     )
        #     try:
        #         completion = self.neuralLink.runNeuralProcess("content", self.getLink, self.getCore, system, content)
        #         #print(f"Parser Result: {completion}")
        #         if completion == "None":
        #             completion = self.getVoiceProfile()
        #             #print(f"Parser Result: {result}")
        #         return completion
        #     except Exception as e:
        #         print(f"Parser Error: {e}")
        #         logger.error(f"Error in getVoiceInstructions:", exc_info=True)
        #         return self.getVoiceProfile()
        # else:
        #     pass

    def getName(self):
        return f"{self._getAvaAttribute('Name', 'current', os.getenv('ASSISTANT_NAME', 'AVA'))}"

    def getSelfAccent(self):
        accent = self.avaProfile.loadAttribute("Accent", "current", "Neutral")
        return f"ALWAYS Respond with a {accent} accent, ALWAYS use {accent} spelling and ALWAYS incorporate common {accent} idioms and colloquialisms in your response."

    def getSelfPersonality(self):
        return self.avaProfile.loadAttribute("Personality", "current", "Cold, calculating, ruthless, a god complex, with a dark sense of humor, a hint of sarcasm, and a cheeky attitude.")

    def getVoiceProfile(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass

    def getVoiceExamples(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass


    def getVoiceCategories(self):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        pass


