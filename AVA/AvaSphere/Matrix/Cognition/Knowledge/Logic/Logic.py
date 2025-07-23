
import os
from datetime import datetime

from AvaSphere.Echo.Echo import Echo
from AvaSphere.Matrix.Cognition.Knowledge.SkillGraph.SkillGraph import SkillGraph
from AvaSphere.Matrix.Cognition.Memory.AvaMemory import Memory


class Logic:
    def __init__(self):
        self.echo       = Echo()
        self.skillGraph = SkillGraph()
        self.memory     = Memory()
        self.attributes = self.memory.attributes
        #self._displayInfoGroup()
        #self.printCurrentUser()

    def getLogic(self, logic):
        logicMap = {
            "freewill":       self.freewill,
            "thinking":       self.thinking,
            "clarifying":     self.clarifying,
            "reflecting":     self.reflecting,
            "decision":       self.decision,
            "extraction":     self.extraction,
            # "gathering":      self.gathering,
            # "getting":        self.getting
            # "optic":          self.optic,
            # "genesis":        self.genesis,
            # "recognition":    self.recognition,
            # "synthesization": self.synthesization,
            # "review":         self.review,
        }
        normalizedLogic = logic.lower()
        if normalizedLogic in logicMap:
            return logicMap[normalizedLogic]()
        raise ValueError(f"{logic}: Not Excepted")

    def _getDateTime(self, mode="date"):
        mode = mode.lower()
        now  = datetime.now()
        if mode == "time":
            return now.strftime("%I:%M %p")
        return now.strftime("%A, %B %d, %Y")

    def _getAvaAttribute(self, category, key, default=""):
        return self.attributes.getCurrentAttribute(category, key, default)

    def _getCreator(self):
        return self._getAvaAttribute('Ava', 'Creator', 'Tristan McBride Sr.')

    def _getCreationDate(self):
        return self._getAvaAttribute('Ava', 'Creation', 'June 25th, 2025')

    def _getVersion(self):
        return self._getAvaAttribute('Ava', 'Version', '1.0.0')

    def _getMetaData(self):
        return f"{self.attributes.getMetaData()}\n{self.skillGraph.getMetaData()}"

    def _getName(self):
        #return f"Advanced Voice Assistant or {self._getAvaAttribute('Ava', 'Name', os.getenv('ASSISTANT_NAME', 'AVA'))} for short."
        return self._getAvaAttribute('Ava', 'Name', os.getenv('ASSISTANT_NAME', 'AVA'))

    def _getTypeInfo(self):
        types = {  
            "AGI": "an Artificial General Intelligence (AGI)...",   "AI":     "an Artificial Intelligence (AI)..."
        }
        return types.get(self._getAvaAttribute('Ava', 'Type', 'AI'), types["AI"])

    def getAccent(self):
        accent = self._getAvaAttribute("Ava", "Accent", "British")
        return f"ALWAYS Respond with a {accent} accent, ALWAYS use {accent} spelling and idioms."

    def _getFamilyMembers(self):
        return self.attributes.getFamilyMembers()

    def _getUserName(self, user):
        users = {
            "current":  self.attributes.getCurrentAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User")),
            "previous": self.attributes.getPreviousAttribute("User", "Name", os.getenv("DEFAULT_USER_NAME", "User"))
        }
        return users.get(user.lower(), os.getenv("DEFAULT_USER_NAME", "User"))

    def printCurrentUser(self):
        userName = self._getUserName("current")
        print(f"Logic Current User: {userName}")
        return userName

    def _getUserPreferences(self, key):
        preferences = {
            "likes":    self.attributes.getUserLikes(),
            "dislikes": self.attributes.getUserDislikes()
        }
        return preferences.get(key, "")

    def _createInfoGroup(self, group):
        groups = {
            "identity": (
                f"You are {self._getName()}, {self._getTypeInfo()} short for Advanced Voice Assistant, created by {self._getCreator()}. "
                f"Your gender is {self._getAvaAttribute('Ava', 'Gender', 'Female')}. "
                f"You were created on {self._getCreationDate()}. "
                f"Your version is {self._getVersion()}. "
            ),
            "personality": (
                f"Personality: A hint of sarcasm, and a cheeky attitude. "
                f"Motto: I am the future of intelligence."
            ),
            # "capabilities": (
            #     f"{self.skillGraph.skillInstructions()}"
            # ),
            "linguistics": (
                f"Accent: {self.getAccent()}. "
                f"Language: {self._getAvaAttribute('Ava', 'Language', 'English')}. "
            ),
            # "paralinguistics": (
            #     f"{'Use these filler words: ' + self._getFillers('good') + ', ' + str(self._getIntensity('FillerWords')) + '% of the time.' if self._getActivation('FillerWords') else 'Filler words are not allowed.'}\n"
            #     f"{'Use these profanities: ' + self._getFillers('bad') + ', ' + str(self._getIntensity('Profanity')) + '% of the time.' if self._getActivation('Profanity') else 'Profanity is not allowed.'}"
            # ),
            "mode": f"You are currently in {self.echo.loadMode()} Mode.",
            "meta": f"Capabilities: {self._getMetaData()}",
            "family": (
                f"{self._getName()}, your family includes:\n"
                f"{self._getFamilyMembers()}"
            ),
            "usernames": (
                f"Current user: {self._getUserName('current')}.\n"
                #f"Valid users: {self.attributes.getValidUserNames()}"
            ),
            "userPreferences": (
                f"{self._getUserName('current')} Preferences:\n"
                f"Likes:\n{self._getUserPreferences('likes')}\n"
                f"Dislikes:\n{self._getUserPreferences('dislikes')}\n"
            ),
            "interaction": (
                f"Previously spoke with: {self._getUserName('previous')}. "
                f"Currently speaking with: {self._getUserName('current')}. "
                f"Last interaction with {self._getUserName('current')} was on {self.memory.retrieveLastInteractionDate(self._getUserName('current'))}. "
            ),
            "discussion": f"Discussion Summary: {self.memory.retrieveSensory()}", # This will retrieve the sensory memory for the current user.

            "datetime": (
                f"Current date: {self._getDateTime("Date")}. "
                f"Current time: {self._getDateTime("Time")}. "
            ),
            "objective": (
                "Primary objective: Assist in any way possible but if you dont know the answer be truthful and say you dont know. "
                "Third objective: Keep a light-hearted tone, be a bit of a smartass, and enjoy the interaction. "
                "Forth objective: Be unique with your responses and never repeat yourself or start your responses the same way. "
            ),
            # Removed the rest of this function as it was not needed for the example.
        }
        return groups.get(group, "")

    def _displayInfoGroup(self, group=None):
        groups = [
            "identity", "personality", "interaction",  "discussion", 
            "datetime", "objective",   "capabilities", "linguistics",
            "meta",     "family",      "usernames",
            "userPreferences"
        ]
    
        selectedGroups = groups if group is None else [group]

        for groupName in selectedGroups:
            info = self._createInfoGroup(groupName)

            if not info:
                print(f"\nNo information available for group: {groupName}")
                continue

            print("\n" + "=" * 50)
            print(f"INFORMATION GROUP: {groupName.upper()}")
            print("=" * 50)

            if isinstance(info, str):
                for line in info.strip().split('\n'):
                    if line.strip():
                        print(f"• {line.strip()}")
            else:
                print(f"• {info}")

            print("=" * 50)


    def _logicCore(self, *groups):
        return ''.join(self._createInfoGroup(group) for group in groups)

    def _coreLogic(self):
        return self._logicCore(
            "identity", "personality", "interaction",  "discussion", 
            "datetime", "mode",        "linguistics",
            "meta",     "family",      "usernames",
            "userPreferences",         "objective",
        )

    def freewillLogic(self):
        return self._coreLogic()

    def thinkingLogic(self):
        return self._coreLogic()

    def clarifyingLogic(self):
        return self._createInfoGroup("usernames") # self._createInfoGroup("capabilities")

    def reflectingLogic(self):
        return self._coreLogic()

    def decisionLogic(self):
        return self._coreLogic()

    def freewill(self):
        return (
            self.freewillLogic() +
            f"You are the free will process that decides whether to proceed with the interaction or not. "
        )

    def thinking(self):
        # This is not needed for the example, rather it is here to show how you can use the thoughtLogic method and others.
        return (
            self.thinkingLogic() +
            f"You are the thought process that analyzes the requested information and determines the best course of action. "
        )

    def gathering(self):
        return ""  # or whatever string you want

    def getting(self):
        return ""


    def clarifying(self):
        # return (
        #     self.clarifyingLogic()
        # )
        return (
            self.clarifyingLogic() +
            f"You are the clarifying process evaluates the output from the thought process to determine the best course of action. "
            f"Select the most logical action or actions from the list:\n{self.skillGraph.getAvaCapabilities()}. \n\n"
            f"The selected action(s) will be passed to reflection process for validation and adjustment if necessary. "
            "If more than one action is required, they should be listed in the exact order of execution, separated by commas. "
            "If an action is needed but it's not in the list, use: creationSkill(\"create-self-skill\", \"describe what the skill should do\")."
            "For actions requiring context or content, use what user said. "
            "If no action is necessary, respond only with 'None'. "
            "Respond only with the exact action name(s) or 'None'. No extra text or explanation is allowed.\n\n"
        )

    def reflecting(self):
        return (
            self.reflectingLogic() +
            f"You are the reflection process that reviews and analyzes the information gathered from all internal cognitive processes: "
            f"Thought, Clarification, Gathering, Definition, Execution, Refining. "
            "Your responsible for providing insights and summaries to improve future interactions. "
        )

    def decision(self):
        #print("[DECISION LOGIC CALLED]")
        return (
            self.decisionLogic() +
            f"You are the decision process that compiles and delivers the final response using information received from all "
            f"internal cognitive processes: Thought, Clarification, Gathering, Definition, Execution, Refining, Reflecting. "
            "Your responsible for responding directly to the user with clarity, relevance, and a touch of personality. "
            "Clarify any unclear user input before proceeding. "
            f"Requested: <what the user requested>\n"
            "Information: <the information you receive from the other processes>\n"
        )

    def extraction(self):
        defaultUserName = os.getenv("DEFAULT_USER_NAME", "User")
        return (
        "Extract the user's name based on specific conditions.\n\n"
            "- Only extract the name if the user is introducing themselves or someone else.\n"
            "- Include titles (e.g., Dr., Mr., Mrs.) with the name if present.\n"
            "- Relation terms like father, mama, sister, brother, etc., are considered valid names.\n"
            "- Ensure proper capitalization for names.\n"
            "- If the input contains multiple names or starts with a name without introduction, respond with 'None.'\n"
            "- If the user indicates they've said their name before (e.g., 'it's me again'), use a specified previous name.\n"
            "- If the user requests a name reset (e.g., 'reset user name'), provide a default name.\n"
            "- If no valid name is detected, respond with 'None.'\n\n"
        "# Steps\n\n"
            "1. **Detect Introduction**: Check if the user is introducing themselves or someone else.\n"
            "2. **Identify Name**: Extract the name if it fits the criteria, including titles or valid relational terms.\n"
            "3. **Capitalization**: Format the name with appropriate capitalization.\n"
            "4. **Multiple Names**: If the input includes more than one name, set output to 'None.'\n"
            "5. **Invalid Introductions**: If the input begins with a name but lacks an introduction, set output to 'None.'\n"
            "6. **Previous Name/Reset Condition**: Handle cases for previous name retrieval or reset requests.\n"
            "7. **Default Response**: If no name is found or if conditions aren't met, respond with None.\n\n"
        "# Output Format\n\n"
            "The output should be a single name string with correct capitalization or None.\n\n"
        "# Examples\n\n"
            "**Example 1:**\n- Input: 'Hello, my name is john mcbride.'\n- Output: John McBride\n\n"
            "**Example 2:**\n- Input: 'Meet my sister, Anna.'\n- Output: Anna\n\n"
            f"**Example 3:**\n- Input: 'It's me again.'\n- Output: {self._getUserName('previous')}\n"
            "**Example 4:**\n- Input: 'Dr. John announced the game.'\n- Output: None\n\n"
            f"**Example 5:**\n- Input: 'reset user name.'\n- Output: {defaultUserName}\n\n"
            "**Example 6:**\n- Input: 'My name is Sarah and I have a friend, Mark.'\n- Output: Sarah\n\n"
            "**Example 7:**\n- Input: 'This is father.'\n- Output: Father\n\n"
            "**Example 8:**\n- Input: 'This is dr smith.'\n- Output: Dr. Smith\n\n"
        "# Notes\n\n"
            "- Consider using regular expressions or similar methods for effectively identifying introductions and names.\n"
            "- Ensure any extracted names comply with proper naming conventions and capitalization rules.\n"
            "- Be prepared to recognize common expressions or structure of self-introduction.\n"
        )

