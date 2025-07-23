
from AvaSphere.Matrix.Cognition.Attributes.AvaAtts.Assets.Profile.AvaProfile import AvaProfile

class GetAvaInfo:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.avaProfile = AvaProfile()
        self.family     = UpdateAvaFamily(self.avaProfile)
        self.features   = UpdateAvaFeatures(self.avaProfile)
        self.actionMap = {
            **self.family.getMap,
            **self.features.getMap,
        }


class UpdateAvaInfo:
    def __init__(self):
        self._initComponents()

    def _initComponents(self):
        self.avaProfile = AvaProfile()
        self.family     = UpdateAvaFamily(self.avaProfile)
        self.features   = UpdateAvaFeatures(self.avaProfile)
        self.atts       = UpdateAvaAtts(self.avaProfile)
        self.actionMap = {
            **self.family.updateMap,
            **self.features.updateMap,
            **self.atts.updateMap,
        }


class UpdateAvaFamily:
    def __init__(self, avaProfile):
        self._initComponents(avaProfile)

    def _initComponents(self, avaProfile):
        self.avaProfile = avaProfile
        self.getMap = {
            'get-family-members':          self._getFamilyMembers,
        }
        self.updateMap = {
            'add-immediate-family-member': self._addImmediateFamilyMember,
            'add-extended-family-member':  self._addExtendedFamilyMember,
            'add-pet':                     self._addPet,
        }

    def _getFamilyMembers(self) -> str:
        return self.avaProfile.family.getFamilyMembers()

    def _addImmediateFamilyMember(self, relationType: str, name: str, nickname: str = None) -> str:
        return self._addFamilyMember("immediate", relationType, name, nickname)

    def _addExtendedFamilyMember(self, relationType: str, name: str, nickname: str = None) -> str:
        return self._addFamilyMember("extended", relationType, name, nickname)

    def _updateImmediateFamilyMember(self, relationType: str, oldName: str, newName: str) -> str:
        return self._updateFamilyMember("immediate", relationType, oldName, "name", newName)

    def _updateExtendedFamilyMember(self, relationType: str, oldName: str, newName: str) -> str:
        return self._updateFamilyMember("extended", relationType, oldName, "name", newName)

    def _deleteImmediateFamilyMember(self, relationType: str, name: str) -> str:
        return self._deleteFamilyMember("immediate", relationType, name)

    def _deleteExtendedFamilyMember(self, relationType: str, name: str) -> str:
        return self._deleteFamilyMember("extended", relationType, name)


    # ───── Family Management (Private) ─────
    def _addFamilyMember(self, role: str, relation: str, name: str, nickname: str = None) -> str:
        try:
            self.avaProfile.family.addFamilyMember(role.lower(), relation.lower(), name.title(), nickname)
            return f"{name} added as a {relation} ({role})."
        except Exception as e:
            return f"Error adding family member: {e}"

    def _updateFamilyMember(self, role: str, relation: str, name: str, field: str, newValue: str) -> str:
        try:
            self.avaProfile.family.updateFamilyMember(role.lower(), relation.lower(), name.title(), field.lower(), newValue)
            return f"{field.capitalize()} for {name} updated to '{newValue}'."
        except Exception as e:
            return f"Error updating family member: {e}"

    def _deleteFamilyMember(self, role: str, relation: str, name: str) -> str:
        try:
            self.avaProfile.family.deleteFamilyMember(role.lower(), relation.lower(), name.title())
            return f"{name} has been removed from the family."
        except Exception as e:
            return f"Error deleting family member: {e}"

    def _addPet(self, name: str, nickname: str = None, gender: str = None, breed: str = None) -> str:
        try:
            self.avaProfile.family.addPet(name.title(), nickname, gender.lower() if gender else None, breed)
            return f"{name} the pet has been added."
        except Exception as e:
            return f"Error adding pet: {e}"

    def _updatePet(self, name: str, field: str, newValue: str) -> str:
        try:
            self.avaProfile.family.updatePet(name.title(), field.lower(), newValue)
            return f"{field.capitalize()} for pet {name} updated to '{newValue}'."
        except Exception as e:
            return f"Error updating pet: {e}"

    def _deletePet(self, name: str) -> str:
        try:
            self.avaProfile.family.deletePet(name.title())
            return f"Pet {name} has been removed."
        except Exception as e:
            return f"Error deleting pet: {e}"


class UpdateAvaFeatures:
    def __init__(self, avaProfile):
        self._initComponents(avaProfile)

    def _initComponents(self, avaProfile):
        self.avaProfile = avaProfile
        self.getMap = {
            'get-self-feature-status':     self._getFeatureStatus,
            'get-self-activated-features': self._getActivatedFeatures,
        }
        self.updateMap = {
            'activate-self-feature':       self._activateFeature,
            'deactivate-self-feature':     self._deactivateFeature,
        }

    def _activateFeature(self, featureName: str) -> str:
        feature = featureName.capitalize()
        if feature in self.avaProfile.feature.defaultStatus:
            self.avaProfile.feature.saveStatus(feature, "True")
            return f"{feature} has been activated."
        return f"{feature} is not a recognized feature."

    def _deactivateFeature(self, featureName: str) -> str:
        feature = featureName.capitalize()
        if feature in self.avaProfile.feature.defaultStatus:
            self.avaProfile.feature.saveStatus(feature, "False")
            return f"{feature} has been deactivated."
        return f"{feature} is not a recognized feature."

    def _getFeatureStatus(self, featureName: str) -> str:
        feature = featureName.capitalize()
        if feature in self.avaProfile.feature.defaultStatus:
            status = self.avaProfile.feature.loadStatus(feature, "False")
            return f"{feature} is currently {'active' if status == 'True' else 'inactive'}."
        return f"{feature} is not a recognized feature."

    def _getActivatedFeatures(self) -> str:
        activeFeatures = [
            feature for feature in self.avaProfile.feature.defaultStatus.keys()
            if self._isFeatureActive(feature)
        ]
        return ", ".join(activeFeatures) if activeFeatures else "No features are currently active."

    def _isFeatureActive(self, featureName: str) -> bool:
        feature = featureName.capitalize()
        if feature in self.avaProfile.feature.defaultStatus:
            status = self.avaProfile.feature.loadStatus(feature, "False")
            return status == "True"
        return False


class UpdateAvaAtts:
    def __init__(self, avaProfile):
        self._initComponents(avaProfile)

    def _initComponents(self, avaProfile):
        self.avaProfile = avaProfile
        self.updateMap = {
            'update-self-name':                 self._updateName,
            'update-self-gender':               self._updateGender,
            'update-self-type':                 self._updateType,
            'update-self-version':              self._updateVersion,
            'update-self-language':             self._updateLanguage,
            'update-self-accent':               self._updateAccent,
            'update-self-fillerWord-intensity': self._updateFillerWordsIntensity,
            'update-self-profanity-intensity':  self._updateProfanityIntensity,
            'update-self-persona':              self._updatePersona,
            'update-self-personality':          self._updatePersonality,
            'update-self-motto':                self._updateMotto,
            'update-self-political':            self._updatePolitical,

        }

    # ───── Identity ─────
    def _updateName(self, name: str) -> str:
        value = name.strip().title()
        return self._updateAttribute("Name", value)

    def _updateGender(self, gender: str) -> str:
        value = gender.strip().capitalize()
        return self._updateAttribute("Gender", value)

    def _updateType(self, value: str) -> str:
        value = value.strip().upper()
        validTypes = ["AI", "AGI"]
        if value in validTypes:
            return self._updateAttribute("Type", value)
        return f"Type must be one of the following: {', '.join(validTypes)}."

    def _updateVersion(self, version: str) -> str:
        return self._updateAttribute("Version", version)

    # ───── Speech ─────
    def _updateLanguage(self, language: str) -> str:
        return self._updateAttribute("Language", language)

    def _updateAccent(self, accent: str) -> str:
        value = accent.strip().capitalize()
        return self._updateAttribute("Accent", value)

    def _updateFillerWordsIntensity(self, intensity: int) -> str:
        if isinstance(intensity, int):
            return self._updateAttribute("FillerWords", intensity)
        return "FillerWords must be an integer."

    def _updateProfanityIntensity(self, intensity: int) -> str:
        if isinstance(intensity, int):
            return self._updateAttribute("Profanity", intensity)
        return "Profanity must be an integer."

    # ───── Traits ─────
    def _updatePersona(self, persona: str) -> str:
        value = persona.strip().capitalize()
        return self._updateAttribute("Persona", value)

    def _updatePersonality(self, personality: str) -> str:
        value = personality.strip().capitalize()
        return self._updateAttribute("Personality", value)

    def _updateMotto(self, motto: str) -> str:
        value = motto.strip().capitalize()
        return self._updateAttribute("Motto", value)

    def _updatePolitical(self, politicalView: str) -> str:
        value = politicalView.strip().capitalize()
        return self._updateAttribute("Political", value)

    def _updateAttribute(self, name: str, value: str | int) -> str:
        name = name.strip().capitalize()
        try:
            self.avaProfile.saveAttribute(name, value)
            return f"{name} has been updated to '{value}'."
        except KeyError:
            return f"{name} is not a recognized attribute."

    def _getAttribute(self, name: str) -> str:
        name = name.strip().capitalize()
        try:
            module, attrType, default = self.avaProfile._attributeMap[name]
            current = self.avaProfile.loadAttribute(name, attrType, default)
            return f"{name}: {current}"
        except KeyError:
            return f"{name} is not a recognized attribute."