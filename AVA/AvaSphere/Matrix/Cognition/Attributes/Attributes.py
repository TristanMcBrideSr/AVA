
import os
from dotenv import load_dotenv
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.AvaAtts import *
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.UserAtts import *

load_dotenv()

class Attributes:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.userAtts      = UserAtts()
        self.avaAtts       = AvaAtts(self)
        self.printMetaData = os.getenv('SHOW_METADATA', 'False') == 'True'

    def getMetaData(self, printMetaData=False):
        metaList = []

        for label, data in [
            ("Ava", self.avaAtts.getMetaData()),
            ("User", self.userAtts.getMetaData())
        ]:
            for key, meta in data.items():
                metaList.append({
                    "className": meta.get('className', 'Unknown'),
                    "description": meta.get('description', 'No description'),
                    "label": label
                })

        if printMetaData or self.printMetaData:
            self.printMetaDataInfo(metaList)

        # If you want to keep the formatted string result as before:
        return "\n".join(
            f"[{m['label']}] Class: {m['className']} | Description: {m['description']}"
            for m in metaList
        )

    def process(self, content):
        #return "\n".join(filter(None, (self.avaAtts.process(content), self.userAtts.process(content)))) or None
        pass

    def getCurrentAttribute(self, attName, attType, default):
        return self._getAttribute("getCurrentAttribute", attName, attType, default)

    def getPreviousAttribute(self, attName, attType, default):
        return self._getAttribute("getPreviousAttribute", attName, attType, default)

    def getIntensity(self, attName):
        return self.avaAtts.getIntensity(attName)

    # def getEmotions(self):
    #     return self.avaAtts.getEmotions()

    # def getFeelings(self, userName=None):
    #     return self.avaAtts.getFeelings(userName)

    # def getOpinions(self, userName=None):
    #     return self.avaAtts.getOpinions(userName)

    # def deleteFeelings(self, userName=None):
    #     return self.avaAtts.deleteFeelings(userName)

    # def deleteOpinions(self, userName=None):
    #     return self.avaAtts.deleteOpinions(userName)

    def getCurrentUserProfile(self):
        return self.userAtts.getCurrentUserProfile()

    # def determineAction(self, content):
    #     return self.avaAtts.determineAction(content)

    # def getSpecialOccasion(self):
    #     return self.userAtts.getSpecialOccasion()

    # def getInstructions(self, content):
    #     return self.avaAtts.getVoiceInstructions(content)

    def getFamilyMembers(self):
        return self.avaAtts.getFamilyMembers()

    def saveAllUserNames(self, name):
        return self.userAtts.saveAllUserNames(name)

    def saveCurrentUserName(self, name):
        return self.userAtts.saveCurrentUserName(name)

    def savePreviousUserName(self, name):
        return self.userAtts.savePreviousUserName(name)

    def getValidUserNames(self):
        return self.userAtts.getValidUserNames()

    def getValidFamilyNames(self):
        return self.avaAtts.getValidFamilyNames()

    def getAllUserPreferences(self):
        return self.userAtts.getAllUserPreferences()

    def getUserLikes(self):
        return self.userAtts.getUserLikes()

    def getUserDislikes(self):
        return self.userAtts.getUserDislikes()

    def _getAttribute(self, method, attName, attType, default):
        sources = {"ava": self.avaAtts, "user": self.userAtts}
        source = sources.get(attName.lower())
        if source and hasattr(source, method):
            return getattr(source, method)(attType.lower())
        return default

    def _source(self, name):
        return {
            "ava": self.avaAtts,
            "user": self.userAtts
        }.get(name.lower())

    def printMetaDataInfo(self, metaList):
        print("Human-readable Format:")
        for m in metaList:
            print(f"\n=== MetaData ===\n")
            print(f"Class: {m['className']} | Description: {m['description']}")
            print("\n" + "=" * 50 + "\n")

        print("My-readable Format:")
        print(metaList)

