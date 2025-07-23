
import os, re
from dotenv import load_dotenv

from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile

class Identity:
    def __init__(self, parent, attrName, defaultValue, promptText, changePrefix, validOptions=None, transformFunc=None):
        self.db            = parent.db
        self.avaProfile    = AvaProfile()
        self.attrName      = attrName
        self.defaultValue  = defaultValue
        self.promptText    = promptText
        self.changePrefix  = changePrefix
        self.validOptions  = validOptions  # List of valid values or None for any value.
        # If no transformation function is provided, use identity.
        self.transformFunc = transformFunc if transformFunc is not None else lambda x: x
        self.currentValue  = self.avaProfile.loadAttribute(attrName, "current", defaultValue)
        self.previousValue = self.avaProfile.loadAttribute(attrName, "previous", defaultValue)
        if self.currentValue == "Not Set":
            self.checkForAttribute()

    def _metaData(self):
        return {"className": self.attrName, "description": f"Allows me to change my {self.attrName.lower()}."}

    def isMutable(self):
        return True  # Most attributes CAN be changed

    def getCurrent(self):
        return self.currentValue

    def getPrevious(self):
        return self.previousValue

    def saveAttribute(self, newValue):
        if not self.isMutable():
            return f"{self.attrName} is immutable and cannot be changed."
        previousValue = self.currentValue
        self.avaProfile.saveAttribute(self.attrName, newValue, previousValue)
        self.previousValue, self.currentValue = previousValue, newValue

    def process(self, content):
        if content.startswith(self.changePrefix):
            newValue = content.replace(self.changePrefix, "").strip()
            newValue = self.transformFunc(newValue)
            if self.validOptions and newValue not in self.validOptions:
                return f"Invalid {self.attrName.lower()} provided. Please choose from {self.validOptions}."
            if newValue != self.currentValue:
                self.saveAttribute(newValue)
                return f"{self.attrName} changed to {newValue}"
            return f"{self.attrName} is already set to {newValue}."

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
        if not self.isMutable():
            return 
        if self.currentValue == self.defaultValue:
            while True:
                print(self.promptText)
                userInput = input().strip()
                if userInput:
                    newValue = self.transformFunc(userInput)
                    if self.validOptions and newValue not in self.validOptions:
                        print(f"Invalid {self.attrName.lower()} provided. Please choose from {self.validOptions}.")
                        continue
                    self.saveAttribute(newValue)
                    print(f"I'm all set to use {newValue} as my {self.attrName.lower()}.")
                    break
                else:
                    print(f"Please provide a valid {self.attrName.lower()}.")

    @staticmethod
    def formatTitleWithSuffixFix(text):
        monthCorrections = {
            "jan": "January",   "janurary": "January",
            "feb": "February",  "febuary":  "February",
            "mar": "March",     "march":    "March",
            "apr": "April",     "april":    "April",
            "may": "May",
            "jun": "June",      "june":     "June",
            "jul": "July",      "july":     "July",
            "aug": "August",    "agust":    "August",
            "sep": "September", "sept":     "September", "septemberr": "September",
            "oct": "October",   "octobre":  "October",
            "nov": "November",  "novem":    "November",
            "dec": "December",  "decem":    "December"
        }

        # Normalize input
        text = text.strip().lower()

        # Correct misspelled/abbreviated months
        for wrong, correct in monthCorrections.items():
            pattern = r'\b' + re.escape(wrong) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)

        # Capitalize text properly
        titled = text.title()

        # Add missing ordinal suffix
        def add_suffix(match):
            day = int(match.group(2))
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day if 10 < day % 100 > 13 else 0, "th")
            return f"{match.group(1)} {day}{suffix}, {match.group(3)}"

        titled = re.sub(r'(\b[A-Za-z]+\b)\s+(\d{1,2}),\s+(\d{4})', add_suffix, titled)

        # Fix casing on suffix if already present
        titled = re.sub(r'(\d+)(St|Nd|Rd|Th)', lambda m: m.group(1) + m.group(2).lower(), titled)

        return titled




class Creator(Identity):
    def __init__(self, parent):
        # Default
        defaultSelfCreator = "Tristan McBride Sr."
        promptText         = "I don't know who created me. Please give me a creator:"
        changePrefix       = "change my creator to"
        # Transform to title case.
        super().__init__(parent, "Creator", defaultSelfCreator, promptText, changePrefix,
                         transformFunc=lambda x: x.title())

    def isMutable(self):
        return False

class Creation(Identity):
    def __init__(self, parent):
        # Default
        defaultSelfCreationDate = "June 25th, 2025"
        promptText              = "I don't know when I was created. Please give me a creation date:"
        changePrefix            = "change your creation date to"
        # Transform to title case.
        super().__init__(parent, "CreationDate", defaultSelfCreationDate, promptText, changePrefix,
                         #transformFunc=Identity.formatTitleWithSuffixFix)
                         transformFunc=lambda x: x.title())

    def isMutable(self):
        return False



class Version(Identity):
    def __init__(self, parent):
        # Default
        defaultSelfVersion = "1.0.0"
        promptText         = "I don't know what my version is. Please give me a version:"
        changePrefix       = "change your version to"
        # Transform to uppercase.
        super().__init__(parent, "Version", defaultSelfVersion, promptText, changePrefix,
                         transformFunc=lambda x: x.upper())

    def isMutable(self):
        return False

class Name(Identity):
    def __init__(self, parent):
        load_dotenv(override=True)
        defaultSelfName = os.getenv("ASSISTANT_NAME", "AVA")
        promptText      = "I don't know what my name is. Please give me a name:"
        changePrefix    = "change your name to"
        # Transform to uppercase.
        super().__init__(parent, "Name", defaultSelfName, promptText, changePrefix,
                         transformFunc=lambda x: x.upper())

class Gender(Identity):
    def __init__(self, parent):
        # Default
        defaultSelfGender = "Female"
        validGenders      = ["Female", "Male"]
        promptText        = ("I don't have a gender yet. Please set my gender:\n"
                             "Choose from Female or Male.")
        changePrefix      = "change your gender to"
        super().__init__(parent, "Gender", defaultSelfGender, promptText, changePrefix,
                         validOptions=validGenders, transformFunc=lambda x: x.capitalize())

class Type(Identity):
    def __init__(self, parent):
        # Default
        defaultSelfType = "AI"
        validTypes      = ["AI", "AGI"]
        promptText      = ("I don't have a type yet. Please give me a new type from the following:\n"
                           "AI, AGI")
        changePrefix    = "change your type to"
        super().__init__(parent, "Type", defaultSelfType, promptText, changePrefix,
                         validOptions=validTypes, transformFunc=lambda x: x.upper())
