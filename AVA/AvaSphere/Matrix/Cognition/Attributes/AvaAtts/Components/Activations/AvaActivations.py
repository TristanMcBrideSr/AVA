import os
import random
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile

class Activation:
    def __init__(self, parent=None, featureName=None, promptText=None, commands=None, defaultStatus="False"):
        self.parent          = parent if parent else None
        self.db              = self.parent.db
        self.avaProfile      = AvaProfile()
        self.featureName     = featureName
        self.defaultStatus   = defaultStatus
        self.promptText      = promptText
        self.commands        = commands or {}
        self.currentStatus   = self.avaProfile.loadStatus(featureName, self.defaultStatus)
        if self.defaultStatus == "Not Set":
            self.checkForStatus()


    def _metaData(self):
        return {"className": self.__class__.__name__, "description": f"Allows me to use {self.featureName.lower()}."}

    def saveStatus(self, status):
        self.avaProfile.saveStatus(self.featureName, status)

    def getCurrent(self):
        self.currentStatus = self.avaProfile.loadStatus(self.featureName, self.defaultStatus)
        return self.currentStatus

    def getPrevious(self):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def process(self, content):
        targetStatus = self.commands.get(content)
        if targetStatus is None:
            return

        if self.currentStatus != targetStatus:
            self.saveStatus(targetStatus)
            self.currentStatus = targetStatus
            if content.startswith("reset"):
                return f"{self.featureName} reset to default"
            state = "activated" if targetStatus == "True" else "deactivated"
            return f"{self.featureName} {state}"

    def checkForStatus(self):
        statusMap = {
            "yes": "True",
            "true": "True",
            "no": "False",
            "false": "False"
        }
        if self.currentStatus == self.defaultStatus:
            while True:
                print(self.promptText)
                userInput = input().strip().lower()
                if userInput in statusMap:
                    newStatus = statusMap[userInput]
                    self.saveStatus(newStatus)
                    self.currentStatus = newStatus
                    break
                else:
                    print("Invalid status. Please provide a valid status (True/False or Yes/No).")



class ActivateMemory(Activation):
    def __init__(self, parent):
        commands = {
            "activate your memory":   "True",
            "deactivate your memory": "False",
            "reset your memory":      "False"
        }
        promptText = "Should I be able to remember? Please provide a status (Yes or No):"
        super().__init__(parent, "Memory", promptText, commands)


class ActivateLearning(Activation):
    def __init__(self, parent):
        commands = {
            "activate your learning":   "True",
            "deactivate your learning": "False",
            "reset your learning":      "False"
        }
        promptText = "Should I be able to learn? Please provide a status (Yes or No):"
        super().__init__(parent, "Learning", promptText, commands)


class ActivateEmotions(Activation):
    def __init__(self, parent):
        commands = {
            "activate your emotions":   "True",
            "deactivate your emotions": "False",
            "reset your emotions":      "False"
        }
        promptText = "Should I be able to feel emotions? Please provide a status (Yes or No):"
        super().__init__(parent, "Emotions", promptText, commands)


class ActivateFeelings(Activation):
    def __init__(self, parent):
        commands = {
            "activate your feelings":   "True",
            "deactivate your feelings": "False",
            "reset your feelings":      "False"
        }
        promptText = "Should I be able to feel feelings? Please provide a status (Yes or No):"
        super().__init__(parent, "Feelings", promptText, commands)


class ActivateFreewill(Activation):
    def __init__(self, parent):
        commands = {
            "activate your free will":   "True",
            "deactivate your free will": "False",
            "reset your free will":      "False"
        }
        promptText = "Should I be able to have free will? Please provide a status (Yes or No):"
        super().__init__(parent, "Freewill", promptText, commands)


class ActivateFillerWords(Activation):
    def __init__(self, parent):
        commands = {
            "use filler words":             "True",
            "activate your filler words":   "True",
            "don't use filler words":       "False",
            "dont use filler words":        "False",
            "deactivate your filler words": "False",
            "reset your filler words":      "False"
        }
        promptText = "Should I be able to use filler words? Please provide a status (Yes or No):"
        super().__init__(parent, "FillerWords", promptText, commands)


class ActivateProfanity(Activation):
    def __init__(self, parent):
        commands = {
            "use profanity":             "True",
            "activate your profanity":   "True",
            "don't use profanity":       "False",
            "dont use profanity":        "False",
            "deactivate your profanity": "False",
            "reset your profanity":      "False"
        }
        promptText = "Should I be able to use profanity? Please provide a status (Yes or No):"
        super().__init__(parent, "Profanity", promptText, commands)


class ActivateFamily(Activation):
    def __init__(self, parent):
        commands = {
            "your allowed to have a family":        "True",
            "activate your family features":        "True",
            "you are not allowed to have a family": "False",
            "deactivate your family features":      "False",
            "reset your family features":           "False"
        }
        promptText = "Should I be able to have a family? Please provide a status (Yes or No):"
        super().__init__(parent, "Family", promptText, commands)


class ActivateSecurity(Activation):
    def __init__(self, parent):
        commands = {
            "activate your security":   "True",
            "deactivate your security": "False",
            "reset your security":      "False"
        }
        promptText = "Should I be able to have security? Please provide a status (Yes or No):"
        super().__init__(parent, "Security", promptText, commands)