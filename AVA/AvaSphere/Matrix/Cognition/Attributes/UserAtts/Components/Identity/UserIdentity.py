import os
from dotenv import load_dotenv

#from AvaSphere.Matrix.Evolution.Attributes.User.Assets.Biometrics.Biometrics import TextAnalyzer
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Profile.UserProfile import UserProfile

load_dotenv()


class Name:
    def __init__(self, parent):
        self.db               = parent.db
        self.userProfile      = UserProfile()
        self.currentUserName  = self.userProfile.identity.loadCurrentUserName()
        self.previousUserName = self.userProfile.identity.loadPreviousUserName()
        #self.neuralLink       = parent.neuralLink

    def _metaData(self):
        return {"className": "UserIdentity", "description": "Allows me analyze content and voices to extract user names."}

    def getCurrent(self):
        return self.userProfile.identity.loadCurrentUserName()

    def getPrevious(self):
        return self.userProfile.identity.loadPreviousUserName()

    def saveAllUserNames(self, name):
        self.userProfile.identity.saveAllUserNames(name)

    def saveCurrentUserName(self, name):
        self.userProfile.identity.saveCurrentUserName(name)

    def savePreviousUserName(self, name):
        self.userProfile.identity.savePreviousUserName(name)

    def getCurrentUserProfile(self):
        userName = self.getCurrent()
        return self.userProfile.profiles.getUserProfile(userName)

    def getAllUserNames(self):
        return self.userProfile.identity.loadAllUserNames()

    def getValidUserNames(self):
        return self.userProfile.profiles.getValidUserNames()

    def getAllUserPreferences(self):
        try:
            return self.userProfile.preferences.getAllPreferences(self.currentUserName)
        except Exception as e:
            return f"Error retrieving preferences: {e}"

    def getUserLikes(self):
        try:
            likes = self.userProfile.preferences.getPreferences(self.currentUserName, "likes")
            return f"{likes or 'None'}"
        except Exception as e:
            return f"Error retrieving likes: {e}"

    def getUserDislikes(self):
        try:
            dislikes = self.userProfile.preferences.getPreferences(self.currentUserName, "dislikes")
            return f"{dislikes or 'None'}"
        except Exception as e:
            return f"Error retrieving dislikes: {e}"
