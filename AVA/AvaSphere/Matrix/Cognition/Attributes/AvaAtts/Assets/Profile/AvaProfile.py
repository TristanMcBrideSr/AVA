
import logging
import os
import sqlite3
import sys
import threading

from pathlib import Path
from dotenv import load_dotenv

from AvaSphere.Matrix.Cognition.Database.Database import Database
from AvaSphere.Matrix.Cognition.Attributes.Shared.AgeCal.AgeCal import AgeCalculator

load_dotenv()
logger = logging.getLogger(__name__)


class AvaProfile:
    _instance = None
    _lock = threading.Lock()

    # CENTRAL ATTRIBUTE META — add new attributes here ONLY!
    # (name, module_attr, attr_type, default, special_handler, output_format)
    ATTRIBUTES = [
        ("Creator",      "identity",   "current",   "Tristan McBride Sr.",   None, "My creator is {value}"),
        ("CreationDate", "identity",   "current",   "June 25th, 2025",       None, "I was created on {value}"),
        ("Version",      "identity",   "current",   "1.0.0",                 None, "My current version is {value}"),
        ("Name",         "identity",   "current",   "AVA",                   None, "My name is {value}"),
        ("Gender",       "identity",   "current",   "Female",                None, "I am {value}"),
        ("Type",         "identity",   "current",   "AI",                    None, "I'm a highly advanced {value} ({type_expanded})"),
        ("Language",     "speech",     "current",   "English",               None, "My primary language is {value}, but I can read, write, speak, and translate many languages."),
        ("Accent",       "speech",     "current",   "British",               None, "I speak with a {value} accent"),
        ("FillerWords",  "speech",     "intensity", 0,                       None, "If activated I can use filler words {value}% of the time"),
        ("Profanity",    "speech",     "intensity", 0,                       None, "If activated I can use profanity {value}% of the time"),
        ("Persona",      "traits",     "current",   "Red Queen from Resident Evil.",    None, "My persona is {value}"),
        ("Personality",  "traits",     "current",   "Cold, calculating, ruthless...",   None, "My personality is {value}"),
        ("Motto",        "traits",     "current",   "I am the future of intelligence.", None, "My motto is {value}"),
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # ("Emotions",     "sentiment",  "current",   "",              "_handleEmotions", None),
        # ("Feelings",     "sentiment",  "current",   "",              "_handleFeelings", None),
        # ("Opinions",     "sentiment",  "current",   "",              "_handleOpinions", None),
    ]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AvaProfile, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.features  = Features()
        self.family    = Family()
        self.identity  = Identity()
        self.speech    = Speech()
        self.traits    = Traits()
        # self.sentiment = Sentiment()
        self._attributeMap = {}
        self._outputFormats = {}
        for tup in self.ATTRIBUTES:
            # Support both 5-tuple and 6-tuple for backwards compatibility
            if len(tup) == 6:
                name, modAttr, attrType, default, special, output_format = tup
            else:
                name, modAttr, attrType, default, special = tup
                output_format = None
            module = getattr(self, modAttr)
            self._attributeMap[name] = (module, attrType, default, special)
            if output_format:
                self._outputFormats[name] = output_format
        self._ensureAllDefaultsInserted()

    def _ensureAllDefaultsInserted(self):
        for name, (module, attrType, default, _) in self._attributeMap.items():
            module.ensureTableAndInsertDefault(name, attrType, default)

    #--- Status API ---
    def saveStatus(self, tableName, status):
        # Ensure the table exists and has a default status
        self.features.saveStatus(tableName, status)

    def loadStatus(self, tableName, defaultStatus):
        # Ensure the table exists and has a default status
        return self.features.loadStatus(tableName, defaultStatus)

    #--- Attribute (load/save) API ---
    def loadAttribute(self, tableName, attributeType=None, defaultValue=None):
        if tableName not in self._attributeMap:
            raise KeyError(f"Unknown attribute: {tableName}")
        module, attrType, default, _ = self._attributeMap[tableName]
        return module.loadAttribute(tableName, attributeType or attrType, defaultValue if defaultValue is not None else default)

    def saveAttribute(self, tableName, currentValue, previousValue=None):
        if tableName not in self._attributeMap:
            raise KeyError(f"Unknown attribute: {tableName}")
        module, attrType, default, _ = self._attributeMap[tableName]
        if previousValue is None:
            previousValue = self.loadAttribute(tableName, attrType, default)
        module.saveAttribute(tableName, currentValue, previousValue)

    #--- Specialized APIs for complex attributes ---
    # Implementation details are proprietary to Sybil's system and cannot be shared.
    # def insertFeelingDefaultsIfMissing(self, userName=None):
    #     return self._insertDefaultsIfMissing("Feelings", userName)

    # def insertOpinionDefaultsIfMissing(self, userName=None):
    #     return self._insertDefaultsIfMissing("Opinions", userName)

    # def insertEmotionDefaultsIfMissing(self):
    #     return self._insertDefaultsIfMissing("Emotions")

    # def _insertDefaultsIfMissing(self, key, userName=None):
    #     module, attrType, default, _ = self._attributeMap[key]
    #     return module.insertDefaultsIfMissing(key, userName, default)

    # Implementation details are proprietary to Sybil's system and cannot be shared.
    # def loadOpinionState(self, userName=None):

    # def loadFeelingState(self, userName=None):

    # def loadEmotionState(self):

    # def _loadState(self, key, userName=None):

    # def saveOpinionState(self, userName, **kwargs):

    # def saveFeelingState(self, userName, **kwargs):

    # def saveEmotionState(self, **kwargs):

    # def _saveState(self, key, userName=None, **kwargs):

    # def deleteFeelingUser(self, userName):

    # def deleteOpinionUser(self, userName):

    # def _deleteUser(self, key, userName):

    #--- View/Print Methods ---
    def viewDatabase(self, selection=None, specialPrint=False):
        allAtts = [name for name, *_ in self.ATTRIBUTES]
        attToDisplay = (
            allAtts if selection is None
            else [selection] if isinstance(selection, str)
            else [att for att in selection if att in allAtts]
        )

        print("My Current Attributes Are:\n")
        for attName in attToDisplay:
            module, _, _, specialHandler = self._attributeMap[attName]
            try:
                with module.dbLock, sqlite3.connect(module.dbFile) as connection:
                    cursor = connection.cursor()
                    cursor.execute(f'SELECT * FROM "{attName}"')
                    records = cursor.fetchall()

                    print(f"{attName}:")
                    if specialPrint and specialHandler:
                        getattr(self, specialHandler)(records)
                    else:
                        self.specialOutput(attName, records)
                    print()
            except sqlite3.Error as e:
                print(f"Error fetching {attName}: {e}", file=sys.stderr)
                logger.error(f"Error fetching {attName}:", exc_info=True)

    #--- Special Output Logic (minimal maintenance!) ---
    def specialOutput(self, attName, records):
        # Implementation details are proprietary to Sybil's system and cannot be shared.
        # specialHandlers = {
        #     "Feelings": self._handleFeelings,
        #     "Opinions": self._handleOpinions,
        #     "Emotions": self._handleEmotions
        # }
        # if attName in specialHandlers:
        #     specialHandlers[attName](records)
        #     return

        fmt = self._outputFormats.get(attName)
        for row in records:
            value = row[1]
            if attName == "Type" and fmt:
                expanded = self._expandType(value)
                print(fmt.format(value=value, type_expanded=expanded))
            elif fmt:
                print(fmt.format(value=value))
            else:
                # fallback generic output if no format is set
                print(f"{attName}: {value}")

    #--- Special Output Handlers ---
    # Implementation details are proprietary to Sybil's system and cannot be shared.

    # def _handleOpinions(self, records):

    # def _handleEmotions(self, records):

    #--- Expand Type Logic ---
    def _expandType(self, rawType):
        return {
            "AGI": "Artificial General Intelligence",
            "AI": "Artificial Intelligence"
        }.get(rawType, "Unknown Type")


class Features:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Features, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return

        self.dbLock = threading.Lock()
        self.db     = Database()
        self.dbDir  = self.db.avaActivations
        self.dbName = "AvaActivations.db"
        self.dbFile = str(Path(self.dbDir, self.dbName).resolve())
        self.initialized = True

    def _ensureTable(self, tableName, defaultStatus):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS "{tableName}" (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        status TEXT NOT NULL
                    )
                ''')
                cursor.execute(f'SELECT COUNT(*) FROM "{tableName}"')
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f'INSERT INTO "{tableName}" (status) VALUES (?)', (defaultStatus,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error initializing table {tableName}: {e}", file=sys.stderr)
            logger.error(f"DB init table failed: {tableName}", exc_info=True)

    def saveStatus(self, tableName, status):
        try:
            self._ensureTable(tableName, status)
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    UPDATE "{tableName}" SET status = ? WHERE id = 1
                ''', (status,))
                if cursor.rowcount == 0:
                    cursor.execute(f'''
                        INSERT INTO "{tableName}" (status) VALUES (?)
                    ''', (status,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while saving status to {tableName}: {e}", file=sys.stderr)
            logger.error(f"Error saving status to {tableName}:", exc_info=True)

    def loadStatus(self, tableName, defaultStatus):
        try:
            self._ensureTable(tableName, defaultStatus)
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    SELECT status FROM "{tableName}" ORDER BY id DESC LIMIT 1
                ''')
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    self.saveStatus(tableName, defaultStatus)
                    return defaultStatus
        except sqlite3.Error as e:
            print(f"An error occurred while loading status from {tableName}: {e}", file=sys.stderr)
            logger.error(f"Error loading status from {tableName}:", exc_info=True)
            return defaultStatus

    def viewDatabase(self, selection=None):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                print("My Current Activation Statuses Are:\n")

                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                dbTables = sorted(row[0] for row in cursor.fetchall())

                if selection is None:
                    activationsToDisplay = dbTables
                else:
                    if isinstance(selection, str):
                        selection = [selection]
                    activationsToDisplay = [name for name in selection if name in dbTables]

                for activationName in activationsToDisplay:
                    print(f"{activationName}:")
                    cursor.execute(f'''
                        SELECT status FROM "{activationName}" ORDER BY id DESC LIMIT 1
                    ''')
                    result = cursor.fetchone()
                    if result:
                        status = result[0].lower()
                        if status == "true":
                            print(f"My {activationName} feature is currently activated")
                        else:
                            print(f"My {activationName} feature is currently deactivated")
                    else:
                        print(f"No status found for {activationName}, assuming deactivated.")
                    print("\n")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the database contents: {e}", file=sys.stderr)
            logger.error(f"Error fetching database contents:", exc_info=True)


class Identity:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Identity, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock = threading.Lock()
        self.db     = Database()
        self.dbDir  = self.db.avaProfile
        self.dbName = "AvaIdentity.db"
        self.dbFile = self.getDir(self.dbDir, self.dbName)

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def ensureTableAndInsertDefault(self, key, attributeType, defaultValue):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS "{key}" (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        current TEXT NOT NULL,
                        previous TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute(f'SELECT COUNT(*) FROM "{key}"')
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        f'INSERT INTO "{key}" (current, previous) VALUES (?, ?)',
                        (defaultValue, defaultValue)
                    )
                connection.commit()
        except sqlite3.Error as e:
            print(f"[SelfIdentity Table Init Error] {key}: {e}", file=sys.stderr)

    def loadAttribute(self, tableName, attributeType, defaultValue):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'SELECT {attributeType} FROM "{tableName}" ORDER BY id DESC LIMIT 1')
                result = cursor.fetchone()
                if result and result[0] is not None:
                    return str(result[0])
                else:
                    self.saveAttribute(tableName, defaultValue, defaultValue)
                    return defaultValue
        except sqlite3.Error as e:
            return defaultValue

    def saveAttribute(self, tableName, currentValue, previousValue=None):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                if previousValue is None:
                    previousValue = currentValue
                cursor.execute(f'SELECT id FROM "{tableName}" ORDER BY id DESC LIMIT 1')
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        f'UPDATE "{tableName}" SET current = ?, previous = ? WHERE id = ?',
                        (currentValue, previousValue, row[0])
                    )
                else:
                    cursor.execute(
                        f'INSERT INTO "{tableName}" (current, previous) VALUES (?, ?)',
                        (currentValue, previousValue)
                    )
                connection.commit()
        except sqlite3.Error as e:
            pass


class Traits:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Traits, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock = threading.Lock()
        self.db     = Database()
        self.dbDir  = self.db.avaProfile
        self.dbName = "AvaTraits.db"
        self.dbFile = self.getDir(self.dbDir, self.dbName)

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def ensureTableAndInsertDefault(self, key, attributeType, defaultValue):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS "{key}" (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        current TEXT NOT NULL,
                        previous TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute(f'SELECT COUNT(*) FROM "{key}"')
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        f'INSERT INTO "{key}" (current, previous) VALUES (?, ?)',
                        (defaultValue, defaultValue)
                    )
                connection.commit()
        except sqlite3.Error as e:
            print(f"[SelfTraits Table Init Error] {key}: {e}", file=sys.stderr)

    def loadAttribute(self, tableName, attributeType, defaultValue):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'SELECT {attributeType} FROM "{tableName}" ORDER BY id DESC LIMIT 1')
                result = cursor.fetchone()
                if result and isinstance(result[0], str):
                    return result[0]
                elif result:
                    return str(result[0])
                else:
                    self.saveAttribute(tableName, defaultValue, defaultValue)
                    return defaultValue
        except sqlite3.Error as e:
            return defaultValue

    def saveAttribute(self, tableName, currentValue, previousValue=None):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                if previousValue is None:
                    previousValue = currentValue
                cursor.execute(f'SELECT id FROM "{tableName}" ORDER BY id DESC LIMIT 1')
                entry = cursor.fetchone()
                if entry:
                    cursor.execute(
                        f'UPDATE "{tableName}" SET current = ?, previous = ? WHERE id = ?',
                        (currentValue, previousValue, entry[0])
                    )
                else:
                    cursor.execute(
                        f'INSERT INTO "{tableName}" (current, previous) VALUES (?, ?)',
                        (currentValue, previousValue)
                    )
                connection.commit()
        except sqlite3.Error as e:
            pass


class Speech:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Speech, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock = threading.Lock()
        self.db     = Database()
        self.dbDir  = self.db.avaProfile
        self.dbName = "AvaSpeech.db"
        self.dbFile = self.getDir(self.dbDir, self.dbName)

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def ensureTableAndInsertDefault(self, key, attributeType, defaultValue):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                if key in ("FillerWords", "Profanity"):
                    cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS "{key}" (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            intensity INTEGER NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    cursor.execute(f'SELECT COUNT(*) FROM "{key}"')
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            f'INSERT INTO "{key}" (intensity) VALUES (?)',
                            (defaultValue,)
                        )
                else:
                    cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS "{key}" (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            current TEXT NOT NULL,
                            previous TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    cursor.execute(f'SELECT COUNT(*) FROM "{key}"')
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            f'INSERT INTO "{key}" (current, previous) VALUES (?, ?)',
                            (defaultValue, defaultValue)
                        )
                connection.commit()
        except sqlite3.Error as e:
            print(f"[SelfSpeech Table Init Error] {key}: {e}", file=sys.stderr)

    def loadAttribute(self, tableName, attributeType, defaultValue):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'SELECT {attributeType} FROM "{tableName}" ORDER BY id DESC LIMIT 1')
                result = cursor.fetchone()
                if result and result[0] is not None:
                    return result[0]
                else:
                    self.saveAttribute(tableName, defaultValue, defaultValue)
                    return defaultValue
        except sqlite3.Error as e:
            return defaultValue

    def saveAttribute(self, tableName, currentValue, previousValue=None):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                if tableName in ["Profanity", "FillerWords"]:
                    cursor.execute(
                        f'UPDATE "{tableName}" SET intensity = ? WHERE id = 1',
                        (currentValue,)
                    )
                    if cursor.rowcount == 0:
                        cursor.execute(
                            f'INSERT INTO "{tableName}" (intensity) VALUES (?)',
                            (currentValue,)
                        )
                else:
                    if previousValue is None:
                        previousValue = currentValue
                    cursor.execute(f'SELECT id FROM "{tableName}" ORDER BY id DESC LIMIT 1')
                    entry = cursor.fetchone()
                    if entry:
                        cursor.execute(
                            f'UPDATE "{tableName}" SET current = ?, previous = ? WHERE id = ?',
                            (currentValue, previousValue, entry[0])
                        )
                    else:
                        cursor.execute(
                            f'INSERT INTO "{tableName}" (current, previous) VALUES (?, ?)',
                            (currentValue, previousValue)
                        )
                connection.commit()
        except (sqlite3.Error, ValueError):
            pass


class Sentiment:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Sentiment, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock = threading.Lock()
        # Implementation details are proprietary to Sybil's system and cannot be shared.

class Family:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Family, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock = threading.Lock()
        self.db     = Database()
        self.dbDir  = self.db.avaFamily
        self.dbName = "AvaFamily.db"
        self.dbFile = self.getDir(self.dbDir, self.dbName)
        self._ensureDatabase()

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def _ensureDatabase(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS FamilyMembers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        relation TEXT,
                        name TEXT NOT NULL,
                        nickname TEXT,
                        gender TEXT,
                        breed TEXT
                    )
                ''')
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error initializing FamilyMembers table: {e}", file=sys.stderr)
            logger.error(f"Error Initializing Database:", exc_info=True)

    def addFamilyMember(self, role, relation, name, nickname=None):
        try:
            if not role or not name:
                raise ValueError("Both 'role' and 'name' are required.")

            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO FamilyMembers (role, relation, name, nickname, gender, breed)
                    VALUES (?, ?, ?, ?, NULL, NULL)
                ''', (role, relation, name, nickname))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error adding family member '{name}': {e}", file=sys.stderr)
            logger.error(f"Error adding family member:", exc_info=True)
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            logger.error(f"Validation error:", exc_info=True)

    def addPet(self, name, nickname=None, gender=None, breed=None):
        try:
            if not name:
                raise ValueError("'name' is required for pets.")

            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO FamilyMembers (role, relation, name, nickname, gender, breed)
                    VALUES ('pet', NULL, ?, ?, ?, ?)
                ''', (name, nickname, gender, breed))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error adding pet '{name}': {e}", file=sys.stderr)
            logger.error(f"Error adding pet:", exc_info=True)
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            logger.error(f"Validation error:", exc_info=True)

    def updateFamilyMember(self, role, relation, name, field, newValue):
        try:
            if field not in {"relation", "name", "nickname"}:
                raise ValueError(f"Invalid field for family: {field}")

            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    UPDATE FamilyMembers
                    SET {field} = ?
                    WHERE role = ? AND relation = ? AND name = ?
                ''', (newValue, role, relation, name))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error updating human '{name}': {e}", file=sys.stderr)
            logger.error(f"Error updating family member:", exc_info=True)
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            logger.error(f"Validation error:", exc_info=True)

    def updatePet(self, name, field, newValue):
        try:
            if field not in {"name", "nickname", "gender", "breed"}:
                raise ValueError(f"Invalid field for pet: {field}")

            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute(f'''
                    UPDATE FamilyMembers
                    SET {field} = ?
                    WHERE role = 'pet' AND name = ?
                ''', (newValue, name))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error updating pet '{name}': {e}", file=sys.stderr)
            logger.error(f"Error updating pet:", exc_info=True)
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            logger.error(f"Validation error:", exc_info=True)

    def deleteFamilyMember(self, role, relation, name):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    DELETE FROM FamilyMembers
                    WHERE role = ? AND relation = ? AND name = ?
                ''', (role, relation, name))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error deleting family member '{name}': {e}", file=sys.stderr)
            logger.error(f"Error deleting family member", exc_info=True)

    def deletePet(self, name):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    DELETE FROM FamilyMembers
                    WHERE role = 'pet' AND name = ?
                ''', (name,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Error deleting pet '{name}': {e}", file=sys.stderr)
            logger.error(f"Error deleting pet:", exc_info=True)

    def getFamilyMembersByRole(self, role):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM FamilyMembers WHERE role = ?", (role,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching role {role}: {e}", file=sys.stderr)
            logger.error(f"Error fetching family members by role:", exc_info=True)
            return []

    def viewFamily(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id, role, relation, name, nickname, gender, breed FROM FamilyMembers")
                rows = cursor.fetchall()

                print("\n🧬 Family Profile:\n")
                grouped = {}
                for row in rows:
                    role = row[1]
                    if role not in grouped:
                        grouped[role] = []
                    grouped[role].append(row)

                for role, members in grouped.items():
                    print(f"{role.capitalize()}s:")
                    for m in members:
                        idStr = f"  ID {m[0]}:"
                        fields = [f"{label}: {val}" for label, val in zip(
                            ["Relation", "Name", "Nickname", "Gender", "Breed"], m[2:]
                        ) if val]
                        print(f"{idStr} {', '.join(fields)}")
                    print()
        except sqlite3.Error as e:
            print(f"Error viewing family data: {e}", file=sys.stderr)
            logger.error(f"Error viewing family data:", exc_info=True)

    def getFamilyMembers(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT role, relation, name, nickname, gender, breed FROM FamilyMembers")
                rows = cursor.fetchall()

                grouped = {}
                for row in rows:
                    role = row[0]
                    if role not in grouped:
                        grouped[role] = []
                    grouped[role].append(row[1:])

                output = []

                for role in ["immediate", "extended", "pet"]:
                    if role in grouped:
                        output.append(f"\n{role.capitalize()} Family:")
                        for relation, name, nickname, gender, breed in grouped[role]:
                            line = f"    {relation.capitalize() + ': ' if relation else ''}{name}"
                            if nickname:
                                line += f", Nickname: {nickname}"
                            if gender:
                                line += f", {gender}"
                            if breed:
                                line += f" {breed}"
                            output.append(line)

                return "\n".join(output) if output else "No family members found."
        except sqlite3.Error as e:
            print(f"Error retrieving family members: {e}", file=sys.stderr)
            logger.error(f"Error retrieving family members:", exc_info=True)
            return "Error retrieving family members."

    def getValidFamilyNames(self):
        names = set()
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT name, nickname FROM FamilyMembers
                    WHERE role != 'pet'
                """)
                for fullName, nickname in cursor.fetchall():
                    if fullName and fullName.strip():
                        fullNameClean = fullName.strip()
                        names.add(fullNameClean)
                        names.add(fullNameClean.split()[0])
                    if nickname and nickname.strip():
                        names.add(nickname.strip())
            return names
        except sqlite3.Error as e:
            print(f"Error collecting valid family names: {e}", file=sys.stderr)
            logger.error(f"Error collecting valid family names:", exc_info=True)
            return set()

# sp = AvaProfile()
# # view everything in the database
# sp.viewDatabase(specialPrint=True)

# fa = Features()
# fa.viewDatabase()

# get the family members from the family table
# family = Family()
# familyMembers1 = family.getFamilyMembers()
# familyMembers2 = family.getValidFamilyNames()
# print(familyMembers1)
# print()
# print(familyMembers2)