
import bcrypt
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


class UserProfile:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return

        self._initComponents()
        
        self.initialized = True

    def _initComponents(self):
        self.dbLock      = threading.Lock()
        self.identity    = Identity()
        self.preferences = Preferences()
        self.profiles    = Profiles()


class Identity:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock = threading.Lock()
        self.db = Database()
        self.dbDir = self.db.userIdentityDir
        self.dbName = "UserIdentity.db"
        self.dbFile = self.getDir(self.dbDir, self.dbName)
        self.initUserDefaults()
        self._ensureDatabase()

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def normalizeUserName(self, userName):
        return userName.strip().capitalize()

    def initUserDefaults(self):
        self.userDefaults = {
            "currentUserName": os.getenv("DEFAULT_USER_NAME", "User"),
            "previousUserName": os.getenv("DEFAULT_USER_NAME", "User")
        }

    def _ensureDatabase(self):
        needsInit = not os.path.isfile(self.dbFile)
        tables = ["Current", "Previous", "AllUsers"]
        if not needsInit:
            try:
                with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                    cursor = connection.cursor()
                    for tableName in tables:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
                        if not cursor.fetchone():
                            needsInit = True
                            break
            except sqlite3.Error as e:
                print(f"UserIdentity DB check failed: {e}", file=sys.stderr)
                logger.error("UserIdentity DB check failed", exc_info=True)
                needsInit = True
        if needsInit:
            self.initializeDatabase()
            self.insertDefaultIdentity()

    def initializeDatabase(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                tables = {
                    "Current": '''id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL''',
                    "Previous": '''id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL''',
                    "AllUsers": '''id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, dtstamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'''
                }
                for table, schema in tables.items():
                    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({schema})')
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred during database initialization: {e}", file=sys.stderr)
            logger.error(f"Error Initializing Database:", exc_info=True)

    def insertDefaultIdentity(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                def insertIfEmpty(tableName, insertSql, value):
                    cursor.execute(f'SELECT COUNT(*) FROM "{tableName}"')
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(insertSql, (value,))
                insertIfEmpty("Current", 'INSERT INTO "Current" (name) VALUES (?)', self.userDefaults["currentUserName"])
                insertIfEmpty("Previous", 'INSERT INTO "Previous" (name) VALUES (?)', self.userDefaults["previousUserName"])
                insertIfEmpty("AllUsers", 'INSERT INTO "AllUsers" (name) VALUES (?)', self.userDefaults["currentUserName"])
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred inserting default identity: {e}", file=sys.stderr)
            logger.error(f"Error inserting default identity:", exc_info=True)

    def saveCurrentUserName(self, currentUserName):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO "Current" (id, name) 
                    VALUES ((SELECT id FROM "Current" LIMIT 1), ?)
                ''', (currentUserName,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while saving current user name: {e}", file=sys.stderr)
            logger.error(f"Error Saving Current User Name:", exc_info=True)

    def loadCurrentUserName(self):
        defaultUserName = os.getenv("DEFAULT_USER_NAME", "User")
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    SELECT name FROM "Current" ORDER BY id DESC LIMIT 1
                ''')
                result = cursor.fetchone()
                return result[0] if result else defaultUserName
        except sqlite3.Error as e:
            print(f"An error occurred while loading current user name: {e}", file=sys.stderr)
            logger.error(f"Error Loading Current User Name:", exc_info=True)
            return defaultUserName

    def savePreviousUserName(self, previousUserName):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO "Previous" (id, name) 
                    VALUES ((SELECT id FROM "Previous" LIMIT 1), ?)
                ''', (previousUserName,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while saving previous user name: {e}", file=sys.stderr)
            logger.error(f"Error Saving Previous User Name:", exc_info=True)

    def loadPreviousUserName(self):
        defaultUserName = os.getenv("DEFAULT_USER_NAME", "User")
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    SELECT name FROM "Previous" ORDER BY id DESC LIMIT 1
                ''')
                result = cursor.fetchone()
                return result[0] if result else defaultUserName
        except sqlite3.Error as e:
            print(f"An error occurred while loading previous user name: {e}", file=sys.stderr)
            logger.error(f"Error Loading Previous User Name:", exc_info=True)
            return defaultUserName

    def saveAllUserNames(self, userName):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO "AllUsers" (name) 
                    VALUES (?)
                ''', (userName,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while saving all user names: {e}", file=sys.stderr)
            logger.error(f"Error Saving All User Names:", exc_info=True)

    def loadAllUserNames(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    SELECT name, dtstamp FROM "AllUsers"
                ''')
                result = cursor.fetchall()
                return "\n".join([f"Name: {row[0]}, Timestamp: {row[1]}" for row in result])
        except sqlite3.Error as e:
            print(f"An error occurred while loading all user names: {e}", file=sys.stderr)
            logger.error(f"Error Loading All User Names:", exc_info=True)
            return ""

    def deleteUserName(self, userName):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    DELETE FROM "AllUsers" WHERE name = ? COLLATE NOCASE
                ''', (userName,))
                connection.commit()
                print(f"User name {userName} deleted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting user name {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Deleting User Name {userName}:", exc_info=True)

    def deleteAllUserNames(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    DELETE FROM "AllUsers"
                ''')
                connection.commit()
                print("All user names deleted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting all user names: {e}", file=sys.stderr)
            logger.error(f"Error Deleting All User Names:", exc_info=True)

    def viewAllUsers(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM "AllUsers"')
                print("All User Names:")
                for row in cursor.fetchall():
                    print(row)
        except sqlite3.Error as e:
            print(f"An error occurred while viewing all users: {e}", file=sys.stderr)
            logger.error(f"Error Viewing All Users:", exc_info=True)

    def viewDatabase(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM "Current"')
                print("Current User Names:")
                for row in cursor.fetchall():
                    print(row)
                cursor.execute('SELECT * FROM "Previous"')
                print("\nPrevious User Names:")
                for row in cursor.fetchall():
                    print(row)
        except sqlite3.Error as e:
            print(f"An error occurred while viewing database: {e}", file=sys.stderr)
            logger.error(f"Error Viewing Database:", exc_info=True)



class Preferences:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return

        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock    = threading.Lock()
        self.db        = Database()
        self.dbDir     = self.db.userPreferencesDir
        self.dbName    = "UserPreferences.db"
        self.dbFile    = self.getDir(self.dbDir, self.dbName)
        self._ensureDatabase()

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def normalizeUserName(self, userName):
        return userName.strip().capitalize()

    def _ensureDatabase(self):
        needsInit = not os.path.isfile(self.dbFile)
        tableName = "Preferences"
        if not needsInit:
            try:
                with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                    cursor = connection.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
                    exists = cursor.fetchone()
                    if not exists:
                        needsInit = True
            except sqlite3.Error as e:
                print(f"UserPreferences DB check failed: {e}", file=sys.stderr)
                logger.error("UserPreferences DB check failed", exc_info=True)
                needsInit = True
        if needsInit:
            self.initializeDatabase()
            self.insertDefaultPreferences()

    def initializeDatabase(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS Preferences (
                        username TEXT PRIMARY KEY,
                        likes TEXT,
                        dislikes TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred during database initialization: {e}", file=sys.stderr)
            logger.error(f"Error Initializing Database:", exc_info=True)

    def insertDefaultPreferences(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Preferences WHERE username = ? COLLATE NOCASE", ("User",))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO Preferences (username, likes, dislikes) VALUES (?, ?, ?)
                    ''', ("User", "", ""))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting default preferences: {e}", file=sys.stderr)
            logger.error(f"Error inserting default preferences:", exc_info=True)

    def _getValue(self, userName, column):
        # userName = self.normalizeUserName(userName)
        try:
            sql = f'SELECT {column} FROM Preferences WHERE username = ? COLLATE NOCASE'
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute(sql, (userName,))
                row = cur.fetchone()
                return row[0] if row and row[0] else ""
        except sqlite3.Error as e:
            print(f"An error occurred while fetching value for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Fetching Value for {userName}:", exc_info=True)
            return ""

    def _setValue(self, userName, column, value):
        # userName = self.normalizeUserName(userName)
        try:
            current = self._getValue(userName, column)
            existing = set(map(lambda v: v.strip().lower(), current.split(','))) if current else set()
            new = set(map(lambda v: v.strip().lower(), value)) if isinstance(value, list) else {value.strip().lower()}
            merged = ", ".join(sorted(existing.union(new), key=str.lower))

            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                conn.execute(f'''
                    INSERT INTO Preferences (username, {column})
                    VALUES (?, ?)
                    ON CONFLICT(username) DO UPDATE SET {column} = excluded.{column}
                ''', (userName, merged))
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while setting value for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Setting Value for {userName}:", exc_info=True)

    def _setRawValue(self, userName, column, value):
        # userName = self.normalizeUserName(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                conn.execute(f'''
                    INSERT INTO Preferences (username, {column})
                    VALUES (?, ?)
                    ON CONFLICT(username) DO UPDATE SET {column} = excluded.{column}
                ''', (userName, value))
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while setting raw value for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Setting Raw Value for {userName}:", exc_info=True)

    def setPreferences(self, userName, key, value):
        # userName = self.normalizeUserName(userName)
        self._setValue(userName, key, value)

    def getPreferences(self, userName, key):
        # userName = self.normalizeUserName(userName)
        return self._getValue(userName, key)

    def getAllPreferences(self, userName):
        # userName = self.normalizeUserName(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT likes, dislikes FROM Preferences WHERE username = ? COLLATE NOCASE', (userName,))
                row = cursor.fetchone()
                if row:
                    likes = row[0] or ""
                    dislikes = row[1] or ""
                    return f"Likes: {likes} | Dislikes: {dislikes}"
                return f"No preferences found for '{userName}'"
        except sqlite3.Error as e:
            print(f"An error occurred while fetching all preferences for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Fetching All Preferences for {userName}:", exc_info=True)
            return ""

    def deletePreferences(self, userName, key):
        # userName = self.normalizeUserName(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                conn.execute(f'UPDATE Preferences SET {key} = NULL WHERE username = ? COLLATE NOCASE', (userName,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while deleting preferences for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Deleting Preferences for {userName}:", exc_info=True)

    def deleteAllPreferences(self, userName):
        # userName = self.normalizeUserName(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                conn.execute('DELETE FROM Preferences WHERE username = ? COLLATE NOCASE', (userName,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while deleting all preferences for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Deleting All Preferences for {userName}:", exc_info=True)

    def removePreferences(self, userName, key, value):
        # userName = self.normalizeUserName(userName)
        try:
            current = self._getValue(userName, key)
            if current:
                values = set(map(lambda v: v.strip().lower(), current.split(',')))
                target = value.strip().lower()
                if target in values:
                    values.remove(target)
                    updated = ", ".join(sorted(values, key=str.lower))
                    self._setRawValue(userName, key, updated)
        except sqlite3.Error as e:
            print(f"An error occurred while removing preferences for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Removing Preferences for {userName}:", exc_info=True)



class Profiles:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return

        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.dbLock    = threading.Lock()
        self.db        = Database()
        self.dbDir     = self.db.userProfilesDir
        self.dbName    = "UserProfiles.db"
        self.dbFile    = self.getDir(self.dbDir, self.dbName)
        self.initializeDatabase()

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def normalizeUserName(self, userName):
        return userName.strip().capitalize()

    def initializeDatabase(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA busy_timeout = 5000")
                schemas = {
                    "Personal": '''username TEXT PRIMARY KEY, 
                        name TEXT, maidenName TEXT, nickname TEXT, dob TEXT, birthPlace TEXT''',
                    "Security": '''username TEXT PRIMARY KEY,
                        password TEXT, pinCode TEXT, securityQuestion1 TEXT, securityQuestion2 TEXT, securityQuestion3 TEXT''',
                    "Medical": '''username TEXT PRIMARY KEY, 
                        age TEXT, height TEXT, weight TEXT, bloodType TEXT, medications TEXT,
                        allergies TEXT, allergicReactions TEXT''',
                    "Contact": '''username TEXT PRIMARY KEY, 
                        phoneNumber TEXT, address TEXT, emailAddress1 TEXT, gmailPassword TEXT, emailAddress2 TEXT, outlookPassword TEXT''',
                    "Family": '''username TEXT, 
                        relationType TEXT, relatedUsername TEXT, PRIMARY KEY (username, relatedUsername)''',
                    "Favorites": '''username TEXT PRIMARY KEY,
                        color TEXT, number TEXT, season TEXT, holiday TEXT, footballTeam TEXT, baseballTeam TEXT, basketballTeam TEXT,
                        hockeyTeam TEXT, soccerTeam TEXT, collegeTeam TEXT, athlete TEXT, sport TEXT, song TEXT, artist TEXT, genre TEXT,
                        album TEXT, band TEXT, composer TEXT, singer TEXT, playlist TEXT, musicVideo TEXT, movie TEXT, movieGenre TEXT,
                        movieSeries TEXT, movieSeriesGenre TEXT, tvShow TEXT, tvShowGenre TEXT, tvSeries TEXT, tvSeriesGenre TEXT, book TEXT,
                        bookGenre TEXT, bookSeries TEXT, bookSeriesGenre TEXT, game TEXT, gameGenre TEXT, gameSeries TEXT, gameSeriesGenre TEXT,
                        food TEXT, drink TEXT, dessert TEXT, snack TEXT, candy TEXT, breakfast TEXT, lunch TEXT, dinner TEXT, fastFood TEXT,
                        restaurant TEXT, candyBar TEXT, iceCream TEXT''',
                    "Pets": '''username TEXT PRIMARY KEY,
                        name TEXT, species TEXT, dob TEXT, gender TEXT, breed TEXT, color TEXT, eyeColor TEXT'''
                }
                for table, schema in schemas.items():
                    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({schema})')
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred during database initialization: {e}", file=sys.stderr)
            logger.error(f"Error Initializing Database:", exc_info=True)

    def executeInsert(self, tableName, columnNames, values):
        placeholders = ', '.join(['?'] * len(values))
        columns = ', '.join(columnNames)
        sql = f'INSERT INTO "{tableName}" ({columns}) VALUES ({placeholders})'
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA busy_timeout = 5000")
                cursor.execute(sql, values)
                connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting into {tableName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into {tableName}:", exc_info=True)

    def formatUserName(self, userName):
        if "'s" in userName:
            userName = userName.replace("'s", "")
        return " ".join([name.capitalize() for name in userName.split()]).title()

    def getAllUsernames(self):
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA busy_timeout = 5000")
                usernames = set()
                for table in ["Personal"]:
                    cursor.execute(f"SELECT username FROM {table}")
                    usernames.update(row[0] for row in cursor.fetchall() if row[0] != "User")
            return sorted(usernames, key=lambda name: name.lower())  # Sort alphabetically, case-insensitive
        except sqlite3.Error as e:
            print(f"An error occurred while fetching usernames: {e}", file=sys.stderr)
            logger.error(f"Error Fetching Usernames:", exc_info=True)
            return []

    def deleteUser(self, userName):
        # userName = self.normalizeUserName(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA busy_timeout = 5000")
                for table in ["Personal", "Security", "Medical", "Contact", "Family", "Favorites", "Pets"]:
                    cursor.execute(f'DELETE FROM "{table}" WHERE username = ? COLLATE NOCASE', (userName,))
                connection.commit()
                print(f"User {userName} deleted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting user {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Deleting User {userName}:", exc_info=True)

    def getUserProfile(self, userName=None, tableName=None):
        """
        Retrieve data for a specific user from the specified table or from all tables if tableName is None.
        Auto-calculates age using dob from Personal if applicable.
        """
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                user_info = {}

                def fetchAndFormat(table):
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns_info = cursor.fetchall()
                    columns = [col[1] for col in columns_info]

                    if userName is None:
                        cursor.execute(f"SELECT * FROM {table}")
                    else:
                        cursor.execute(f"SELECT * FROM {table} WHERE username = ? COLLATE NOCASE", (userName,))

                    rows = cursor.fetchall()
                    if not rows:
                        return []

                    records = []
                    for row in rows:
                        record = dict(zip(columns, row))

                        # Recalculate age from dob if relevant
                        if table == "Medical":
                            username_val = record.get("username") or userName
                            if username_val:
                                cursor.execute("SELECT dob FROM Personal WHERE username = ? COLLATE NOCASE", (username_val,))
                                dob_row = cursor.fetchone()
                                if dob_row:
                                    dob = dob_row[0]
                                    if dob and dob != "NA":
                                        try:
                                            age_calculator = AgeCalculator(dob)
                                            record["age"] = age_calculator.calAge()
                                        except Exception:
                                            pass

                        if table == "Personal" and "dob" in record:
                            dob = record.get("dob")
                            if dob and dob != "NA":
                                try:
                                    age_calculator = AgeCalculator(dob)
                                    record["age"] = age_calculator.calAge()
                                except Exception:
                                    pass

                        records.append(record)
                    return records

                if tableName:
                    return fetchAndFormat(tableName)
                else:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    for table in tables:
                        user_info[table] = fetchAndFormat(table)

                    if not any(user_info.values()):
                        print("No records found in any table.")
                        return None

                    return user_info

        except sqlite3.Error as e:
            print(f"An error occurred while fetching data from table {tableName or 'all tables'}: {e}", file=sys.stderr)
            logger.error(f"Error Fetching Data from {tableName or 'all tables'}:", exc_info=True)
            return None

    def getValidUserNames(self):
        return ", ".join(self.getAllUsernames())

    def hashSecret(self, plainText):
        return bcrypt.hashpw(plainText.upper().encode(), bcrypt.gensalt()).decode()

    def verifySecret(self, plainText, hashedText):
        return bcrypt.checkpw(plainText.upper().encode(), hashedText.encode())

    def verifyLogin(self, userName, secret):
        # userName = self.normalizeUserName(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT password, pinCode FROM Security WHERE username = ? COLLATE NOCASE', (userName,))
                row = cursor.fetchone()
                if row:
                    storedPassword, storedPin = row
                    return (
                        self.verifySecret(secret, storedPassword)
                        or self.verifySecret(secret, storedPin)
                    )
                return False
        except sqlite3.Error as e:
            print(f"Error verifying login for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Verifying Login for {userName}:", exc_info=True)
            return False

    def addPersonalInfo(self, userName, personal: dict):
        # userName = self.normalizeUserName(userName)
        columns = ["username"]
        values  = [userName]
        for col in ["name","maidenName","nickname","dob","birthPlace"]:
            columns.append(col)
            values.append(personal.get(col, ""))
        placeholders = ", ".join("?" for _ in values)
        cols_str     = ", ".join(columns)
        sql = f'INSERT INTO "Personal" ({cols_str}) VALUES ({placeholders})'
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into Personal for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into Personal for {userName}:", exc_info=True)

    def addContactInfo(self, userName, contact: dict):
        # userName = self.normalizeUserName(userName)
        columns = ["username"]
        values  = [userName]
        for col in ["phoneNumber","address","emailAddress1","gmailPassword","emailAddress2","outlookPassword"]:
            columns.append(col)
            values.append(contact.get(col, ""))
        placeholders = ", ".join("?" for _ in values)
        cols_str     = ", ".join(columns)
        sql = f'INSERT INTO "Contact" ({cols_str}) VALUES ({placeholders})'
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into Contact for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into Contact for {userName}:", exc_info=True)

    def addSecurityInfo(self, userName, security: dict):
        # userName = self.normalizeUserName(userName)
        password = self.hashSecret(security.get("password", "")) if security.get("password") else ""
        pinCode = self.hashSecret(security.get("pinCode", "")) if security.get("pinCode") else ""
        values = [
            userName,
            password,
            pinCode,
            security.get("securityQuestion1", ""),
            security.get("securityQuestion2", ""),
            security.get("securityQuestion3", "")
        ]
        sql = '''INSERT INTO "Security"
                    (username, password, pinCode, securityQuestion1, securityQuestion2, securityQuestion3)
                 VALUES (?, ?, ?, ?, ?, ?)'''
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into Security for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into Security for {userName}:", exc_info=True)

    def addMedicalInfo(self, userName, medical: dict):
        # userName = self.normalizeUserName(userName)
        columns = ["username"]
        values  = [userName]
        for col in ["height","weight","bloodType","medications","allergies","allergicReactions"]:
            columns.append(col)
            values.append(medical.get(col, ""))
        placeholders = ", ".join("?" for _ in values)
        cols_str     = ", ".join(columns)
        sql = f'INSERT INTO "Medical" ({cols_str}) VALUES ({placeholders})'
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into Medical for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into Medical for {userName}:", exc_info=True)

    def addFavoritesInfo(self, userName, favorites: dict):
        # userName = self.normalizeUserName(userName)
        columns = ["username"] + list(favorites.keys())
        values  = [userName] + list(favorites.values())
        placeholders = ", ".join("?" for _ in values)
        cols_str     = ", ".join(columns)
        sql = f'INSERT INTO "Favorites" ({cols_str}) VALUES ({placeholders})'
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into Favorites for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into Favorites for {userName}:", exc_info=True)

    def addPetsInfo(self, userName, pets: dict):
        # userName = self.normalizeUserName(userName)
        columns = ["username"] + list(pets.keys())
        values  = [userName] + list(pets.values())
        placeholders = ", ".join("?" for _ in values)
        cols_str     = ", ".join(columns)
        sql = f'INSERT INTO "Pets" ({cols_str}) VALUES ({placeholders})'
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into Pets for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Inserting into Pets for {userName}:", exc_info=True)

    def updatePersonalInfo(self, userName, personal: dict):
        # userName = self.normalizeUserName(userName)
        sql = """
            UPDATE "Personal"
               SET name        = ?,
                   maidenName  = ?,
                   nickname    = ?,
                   dob         = ?,
                   birthPlace  = ?
             WHERE username    = ? COLLATE NOCASE
        """
        try:
            vals = (
                personal.get("name", ""),
                personal.get("maidenName", ""),
                personal.get("nickname", ""),
                personal.get("dob", ""),
                personal.get("birthPlace", ""),
                userName
            )
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, vals)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating Personal for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Updating Personal for {userName}:", exc_info=True)

    def updateContactInfo(self, userName, contact: dict):
        # userName = self.normalizeUserName(userName)
        sql = """
            UPDATE "Contact"
               SET phoneNumber     = ?,
                   address         = ?,
                   emailAddress1   = ?,
                   gmailPassword   = ?,
                   emailAddress2   = ?,
                   outlookPassword = ?
             WHERE username       = ? COLLATE NOCASE
        """
        try:
            vals = (
                contact.get("phoneNumber", ""),
                contact.get("address", ""),
                contact.get("emailAddress1", ""),
                contact.get("gmailPassword", ""),
                contact.get("emailAddress2", ""),
                contact.get("outlookPassword", ""),
                userName
            )
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, vals)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating Contact for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Updating Contact for {userName}:", exc_info=True)

    def updateSecurityInfo(self, userName, security: dict):
        # userName = self.normalizeUserName(userName)
        password = self.hashSecret(security.get("password", "")) if security.get("password") else ""
        pinCode = self.hashSecret(security.get("pinCode", "")) if security.get("pinCode") else ""
        values = [
            password,
            pinCode,
            security.get("securityQuestion1", ""),
            security.get("securityQuestion2", ""),
            security.get("securityQuestion3", ""),
            userName
        ]
        sql = '''
            UPDATE "Security"
               SET password           = ?,
                   pinCode            = ?,
                   securityQuestion1  = ?,
                   securityQuestion2  = ?,
                   securityQuestion3  = ?
             WHERE username           = ? COLLATE NOCASE'''
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating Security for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Updating Security for {userName}:", exc_info=True)

    def updateMedicalInfo(self, userName, medical: dict):
        # userName = self.normalizeUserName(userName)
        sql = """
            UPDATE "Medical"
               SET height             = ?,
                   weight             = ?,
                   bloodType          = ?,
                   medications        = ?,
                   allergies          = ?,
                   allergicReactions  = ?
             WHERE username           = ? COLLATE NOCASE
        """
        try:
            vals = (
                medical.get("height", ""),
                medical.get("weight", ""),
                medical.get("bloodType", ""),
                medical.get("medications", ""),
                medical.get("allergies", ""),
                medical.get("allergicReactions", ""),
                userName
            )
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, vals)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating Medical for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Updating Medical for {userName}:", exc_info=True)

    def updateFavoritesInfo(self, userName, favorites: dict):
        # userName = self.normalizeUserName(userName)
        columns = []
        values  = []
        for col in [
            "color","number","season","holiday","footballTeam","baseballTeam",
            "basketballTeam","hockeyTeam","soccerTeam","collegeTeam","athlete",
            "sport","song","artist","genre","album","band","composer","singer",
            "playlist","musicVideo","movie","movieGenre","movieSeries",
            "movieSeriesGenre","tvShow","tvShowGenre","tvSeries","tvSeriesGenre",
            "book","bookGenre","bookSeries","bookSeriesGenre","game","gameGenre",
            "gameSeries","gameSeriesGenre","food","drink","dessert","snack",
            "candy","breakfast","lunch","dinner","fastFood","restaurant",
            "candyBar","iceCream"
        ]:
            if col in favorites:
                columns.append(f"{col} = ?")
                values.append(favorites[col])

        if not columns:
            return

        sql = f'UPDATE "Favorites" SET {", ".join(columns)} WHERE username = ? COLLATE NOCASE'
        values.append(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating Favorites for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Updating Favorites for {userName}:", exc_info=True)

    def updatePetsInfo(self, userName, pets: dict):
        # userName = self.normalizeUserName(userName)
        columns = []
        values  = []
        for col in ["name","species","dob","gender","breed","color","eyeColor"]:
            if col in pets:
                columns.append(f"{col} = ?")
                values.append(pets[col])

        if not columns:
            return

        sql = f'UPDATE "Pets" SET {", ".join(columns)} WHERE username = ? COLLATE NOCASE'
        values.append(userName)
        try:
            with self.dbLock, sqlite3.connect(self.dbFile) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout = 5000")
                cur.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating Pets for {userName}: {e}", file=sys.stderr)
            logger.error(f"Error Updating Pets for {userName}:", exc_info=True)


# ui = Identity()
# ui.viewDatabase()