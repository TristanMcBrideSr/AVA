
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile


class Family:
    def __init__(self, parent=None):
        self.parent        = parent
        self.defaultStatus = "False"
        self.avaProfile    = AvaProfile()
        self._initDefaultFamily()
        self.currentStatus = self.avaProfile.loadStatus("Family", self.defaultStatus)

    def _metaData(self):
        return { "className": self.__class__.__name__,"description": "Provides me with my family information."}

    # def _initDefaultFamily(self):
    #     self.defaultMembers = (
    #         ("immediate", "father", "Tristan McBride Sr.", "Trouble", None, None),
    #     )
    def _initDefaultFamily(self):
        self.defaultMembers = [
            ("immediate", "father", "Tristan McBride Sr.", "Trouble", None, None)
        ]
        # for role, relation, name, nickname, gender, breed in self.defaultMembers:
        #     # Only add if not already present
        #     existing = [
        #         member for member in self.avaProfile.family.getFamilyMembersByRole(role)
        #         if member[3] == name  # column index 3 is 'name'
        #     ]
        #     if not existing:
        #         self.avaProfile.family.addFamilyMember(role, relation, name, nickname)
        for role, relation, name, nickname, gender, breed in self.defaultMembers:
            if role == "pet":
                # Only add if not already present
                pets = self.avaProfile.family.getFamilyMembersByRole("pet")
                found = any(row[3] == name for row in pets)
                if not found:
                    self.avaProfile.family.addPet(name, nickname, gender, breed)
            else:
                members = self.avaProfile.family.getFamilyMembersByRole(role)
                found = any(row[2] == relation and row[3] == name for row in members)
                if not found:
                    self.avaProfile.family.addFamilyMember(role, relation, name, nickname)

    def getCurrent(self):
        self.currentStatus = self.avaProfile.loadStatus("Family", self.defaultStatus)
        return self.currentStatus

    def getPrevious(self):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def process(self, content):
        # This function is kept empty on purpose. DO NOT REMOVE.
        pass

    def familylActivated(self):
        return self.getCurrent() == 'True'

    def getParents(self):
        return self.avaProfile.family.getParents()

    def getSiblings(self):
        return self.avaProfile.family.getSiblings()

    def getGrandparents(self):
        return self.avaProfile.family.getGrandparents()

    def getPets(self):
        return self.avaProfile.family.getPets()

    def getFamilyMembers(self):
        if self.familylActivated():
            return self.avaProfile.family.getFamilyMembers()
        else:
            return "You do not have a family as your family features are not activated."

    def getValidFamilyNames(self):
        return self.avaProfile.family.getValidFamilyNames()
