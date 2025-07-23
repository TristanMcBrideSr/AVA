
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Profile.UserProfile import UserProfile


class UpdateUserInfo:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.atts = UserAtts()
        self.actionMap = {
            **self.atts.updateMap,
        }

class GetUserInfo:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.atts = UserAtts()
        self.actionMap = {
            **self.atts.getMap,
        }


class UserAtts:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.userProfile      = UserProfile()
        self.currentUserName  = self.userProfile.identity.loadCurrentUserName()
        self.previousUserName = self.userProfile.identity.loadPreviousUserName()
        self.getMap = {
            'get-user-likes':          self._getUserLikes,
            'get-user-dislikes':       self._getUserDislikes,
            'get-user-contact-info':   self._getUserContactInfo,
            'get-user-personal-info':  self._getUserPersonalInfo,
            'get-user-medical-info':   self._getUserMedicalInfo,
            'get-user-family-info':    self._getUserFamilyInfo,
            'get-user-favorites-info': self._getUserFavoritesInfo,
            'get-user-pets-info':      self._getUserPetsInfo,

        }
        self.updateMap = {
            'update-user-name':            self._updateName,
            'add-user-likes':              self._addUserLikes,
            'add-user-dislikes':           self._addUserDislikes,
            'remove-user-like':            self._removeUserLike,
            'remove-user-dislike':         self._removeUserDislike,
            'delete-user-likes':           self._deleteUserLikes,
            'delete-user-dislikes':        self._deleteUserDislikes,
            'delete-all-user-preferences': self._deleteAllUserPreferences,

        }

    def _metaData(self):
        return {
            "className": self.__class__.__name__,
            "description": "Allows me preform various actions including updating the current user name, updating and getting user preferences and attributes."
        }

    def _updateName(self, name: str) -> str:
        try:
            if name != self.currentUserName:
                self.previousUserName = self.currentUserName
                self.currentUserName = name
                self.userProfile.identity.saveAllUserNames(name)
                self.userProfile.identity.saveCurrentUserName(self.currentUserName)
                self.userProfile.identity.savePreviousUserName(self.previousUserName)
        except Exception as e:
            return f"Name error: {e}"

    def _addUserLikes(self, like: str) -> str:
        try:
            self.userProfile.preferences.setPreferences(self.currentUserName, "likes", like)
            return f"Added likes: {like}"
        except Exception as e:
            return f"Error adding likes: {e}"

    def _addUserDislikes(self, dislike: str) -> str:
        try:
            self.userProfile.preferences.setPreferences(self.currentUserName, "dislikes", dislike)
            return f"Added dislikes: {dislike}"
        except Exception as e:
            return f"Error adding dislikes: {e}"

    def _getUserLikes(self, userName: str) -> str:
        try:
            likes = self.userProfile.preferences.getPreferences(userName, "likes")
            return f"{userName} likes: {likes or 'None'}"
        except Exception as e:
            return f"Error retrieving likes: {e}"

    def _getUserDislikes(self, userName: str) -> str:
        try:
            dislikes = self.userProfile.preferences.getPreferences(userName, "dislikes")
            return f"{userName} dislikes: {dislikes or 'None'}"
        except Exception as e:
            return f"Error retrieving dislikes: {e}"

    def _removeUserLike(self, like: str) -> str:
        try:
            self.userProfile.preferences.removePreferences(self.currentUserName, "likes", like)
            return f"Removed like: {like}"
        except Exception as e:
            return f"Error removing like: {e}"

    def _removeUserDislike(self, dislike: str) -> str:
        try:
            self.userProfile.preferences.removePreferences(self.currentUserName, "dislikes", dislike)
            return f"Removed dislike: {dislike}"
        except Exception as e:
            return f"Error removing dislike: {e}"

    def _deleteUserLikes(self) -> str:
        try:
            self.userProfile.preferences.deletePreferences(self.currentUserName, "likes")
            return f"Deleted likes for {self.currentUserName}"
        except Exception as e:
            return f"Error deleting likes: {e}"

    def _deleteUserDislikes(self) -> str:
        try:
            self.userProfile.preferences.deletePreferences(self.currentUserName, "dislikes")
            return f"Deleted dislikes for {self.currentUserName}"
        except Exception as e:
            return f"Error deleting dislikes: {e}"

    def _deleteAllUserPreferences(self) -> str:
        try:
            self.userProfile.preferences.deleteAllPreferences(self.currentUserName)
            return f"All preferences deleted for {self.currentUserName}"
        except Exception as e:
            return f"Error deleting all preferences: {e}"

    def getAllUserPreferences(self) -> str:
        try:
            return self.userProfile.preferences.getAllPreferences(self.currentUserName)
        except Exception as e:
            return f"Error retrieving preferences: {e}"


    def _getUserContactInfo(self, userName: str) -> str:
        return self._getUserInfoSection(userName, "Contact")

    def _getUserPersonalInfo(self, userName: str) -> str:
        return self._getUserInfoSection(userName, "Personal")

    def _getUserMedicalInfo(self, userName: str) -> str:
        return self._getUserInfoSection(userName, "Medical")

    def _getUserFamilyInfo(self, userName: str) -> str:
        return self._getUserInfoSection(userName, "Family")

    def _getUserFavoritesInfo(self, userName: str) -> str:
        return self._getUserInfoSection(userName, "Favorites")

    def _getUserPetsInfo(self, userName: str) -> str:
        return self._getUserInfoSection(userName, "Pets")

    def _getUserInfoSection(self, userName: str, sectionName: str) -> str:
        try:
            if userName == "my":
                userName = self.currentUserName
            else:
                userName = self.userProfile.profiles.formatUserName(userName)

            if userName:
                try:
                    return str(self.userProfile.profiles.getUserProfile(userName, sectionName))
                except Exception:
                    return f"{sectionName} Info: Not Found"
        except Exception as e:
            return f"An error occurred while trying to get the user {sectionName.lower()} info: {e}"
