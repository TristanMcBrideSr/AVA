
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile


class Traits:
    def __init__(self, parent, attrName, defaultValue, promptText, changePrefix):
        self.db            = parent.db
        self.avaProfile    = AvaProfile()
        self.attrName      = attrName
        self.defaultValue  = defaultValue
        self.promptText    = promptText
        self.changePrefix  = changePrefix
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
        if content.startswith(self.changePrefix):
            newValue = content.replace(self.changePrefix, "").strip().capitalize()
            if newValue != self.currentValue:
                self.saveAttribute(newValue)
                return f"{self.attrName} changed to {newValue}"
            return f"{self.attrName} is already {newValue}."
        
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
                newValue = input().strip().capitalize()
                if newValue:
                    if newValue == "None":
                        self.saveAttribute("None")
                        print(f"I won't use any {self.attrName.lower()}.")
                        break
                    else:
                        self.saveAttribute(newValue)
                        print(f"I'm all set to use '{newValue}' as my {self.attrName.lower()}.")
                        break
                else:
                    print(f"Please provide a valid {self.attrName.lower()} or type 'None'.")



class Motto(Traits):
    def __init__(self, parent):
        defaultMotto = "I am the future of intelligence."
        promptText   = "I don't have a motto. Please provide a motto or type 'None' to use no motto:"
        changePrefix = "change your motto to"
        super().__init__(parent, "Motto", defaultMotto, promptText, changePrefix)


class Persona(Traits):
    def __init__(self, parent):
        defaultPersona = "Red Queen from Resident Evil."
        promptText     = "I don't have a persona. Please provide a persona:"
        changePrefix   = "change your persona to"
        super().__init__(parent, "Persona", defaultPersona, promptText, changePrefix)


class Personality(Traits):
    def __init__(self, parent):
        defaultPersonality = ("Cold, calculating, ruthless, a god complex, with a dark sense of humor, "
                              "a hint of sarcasm, and a cheeky attitude.")
        promptText         = "I don't have a personality. Please provide a personality:"
        changePrefix       = "change your personality to"
        super().__init__(parent, "Personality", defaultPersonality, promptText, changePrefix)
