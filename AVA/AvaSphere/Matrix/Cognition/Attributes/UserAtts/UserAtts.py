import os
from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Components.Identity.UserIdentity import *


class UserAtts:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.db                  = Database()
        self.components = {
            'name':    Name(self),
        }

    def getMetaData(self):
        data = {}
        for name, component in self.components.items():
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

    def getValidUserNames(self):
        return self.components['name'].getValidUserNames()

    def getAllUserNames(self):
        return self.components['name'].getAllUserNames()

    def getAllUserPreferences(self):
        return self.components['name'].getAllUserPreferences()

    def getUserLikes(self):
        return self.components['name'].getUserLikes()

    def getUserDislikes(self):
        return self.components['name'].getUserDislikes()

    def saveAllUserNames(self, name):
        self.components['name'].saveAllUserNames(name)

    def saveCurrentUserName(self, name):
        self.components['name'].saveCurrentUserName(name)

    def savePreviousUserName(self, name):
        self.components['name'].savePreviousUserName(name)
