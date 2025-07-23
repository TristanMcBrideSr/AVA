from pathlib import Path
import shutil
import os
import threading
import sys
from dotenv import load_dotenv

def detectProjectLayout() -> tuple[Path, str]:
    """
    1. Take the entry‐point script (__main__.__file__), whose stem is your project name.
    2. Find the folder whose name matches that stem—that's your source folder.
    3. Its parent is the true project root (where assets live).
    Fallback: use cwd.
    """
    mainMod = sys.modules.get("__main__")
    if mainMod and hasattr(mainMod, "__file__"):
        entryPath     = Path(mainMod.__file__).resolve()
        projectName   = entryPath.stem
        # find the ancestor folder named like the script
        for ancestor in entryPath.parents:
            if ancestor.name == projectName:
                return ancestor.parent, projectName
    # fallback
    cwd = Path.cwd().resolve()
    return cwd, cwd.name

# — one‐time at import —
PROJECT_ROOT, PROJECT_NAME = detectProjectLayout()
# print(PROJECT_NAME)

# print(f"Detected project root: {PROJECT_ROOT}, project name: {PROJECT_NAME}")

load_dotenv(override=True)

MARKER_FILE = f".{PROJECT_NAME}"

class Database:
    _instance = None
    _lock = threading.Lock()

    _dbMap = {
        "restrictedDir":              ["Restricted"],
        "attsDir":                    ["Attributes"],
        "userFaceDir":                ["Attributes", "User", "Faces"],
        "capturedUserFace":           ["Attributes", "User", "Faces", "Captured"],
        "forgetUserFaces":            ["Attributes", "User", "Faces", "Forget"],
        "rememberedUserFaces":        ["Attributes", "User", "Faces", "Remembered"],
        "userIdentityDir":            ["Attributes", "User", "Identity"],
        "userProfilesDir":            ["Attributes", "User", "Profiles"],
        "userPreferencesDir":         ["Attributes", "User", "Preferences"],
        "userVoiceDir":               ["Attributes", "User", "Voices"],
        "userCapturedVoice":          ["Attributes", "User", "Voices", "Captured"],
        "forgetUserVoices":           ["Attributes", "User", "Voices", "Forget"],
        "rememberedUserVoices":       ["Attributes", "User", "Voices", "Remembered"],

        "avaActivations":             ["Attributes", "Ava", "Activations"],
        "avaFamily":                  ["Attributes", "Ava", "Family"],
        "avaProfile":                 ["Attributes", "Ava", "Profile"],
        "avaImages":                  ["Attributes", "Ava", "Images"],

        "memoryDir":                  ["Memory"],
        "senDir":                     ["Memory", "SEN"],

        "stmUserConversationDetails": ["Memory", "STM", "Interactions"],
        "stmInteractionDetailsDir":   ["Memory", "STM", "Details"],
        "stmUserInteractionDetails":  ["Memory", "STM", "Details", "Interactions"],
        "stmCreatedImageDetails":     ["Memory", "STM", "Details", "Media", "Images"],
        "stmCreatedVideosDetails":    ["Memory", "STM", "Details", "Media", "Videos"],


        "ltmUserConversationDetails": ["Memory", "LTM", "Interactions"],
        "ltmInteractionDetailsDir":   ["Memory", "LTM", "Details"],
        "ltmUserInteractionDetails":  ["Memory", "LTM", "Details", "Interactions"],
        "ltmCreatedImageDetails":     ["Memory", "LTM", "Details", "Media", "Images"],
        "ltmCreatedVideosDetails":    ["Memory", "LTM", "Details", "Media", "Videos"],

        "musicDir":                   ["Music"],
        "playlistDir":                ["Music", "Playlists"],
        "whistlesDir":                ["Whistles"],
        "specialOccasionsDir":        ["SpecialOccasions"],
        "learningDir":                ["Learned"],
        "alertsDir":                  ["Alerts"],
        "echoSoundDir":               ["Sounds"],

    }

    _rootMap = {
        "echoDir":           ["AvaSphere", "Echo"],
        "echoInputDir":      ["AvaSphere", "Echo", "Components", "Dirs", "Input"],
        "echoModeDir":       ["AvaSphere", "Echo", "Components", "Dirs", "Mode"],
        "echoOutputDir":     ["AvaSphere", "Echo", "Components", "Dirs", "Output"],
        "opticDir":          ["AvaSphere", "Optic"],
        "opticInputDir":     ["AvaSphere", "Optic", "Components", "Dirs", "Input"],
        "opticModeDir":      ["AvaSphere", "Optic", "Components", "Dirs", "Mode"],
        "opticOutputDir":    ["AvaSphere", "Optic", "Components", "Dirs", "Output"],
        "skillGraphDir":     ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills"],
        "skillTemplateDir":  ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Components", "Templates"],

        "userSkillsDir":     ["AvaSphere", "Matrix", "Skills", "User"],
        "avaSkillsDir":      ["AvaSphere", "Matrix", "Skills", "Ava"],

        "userDynamicDir":    ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "User", "Dynamic"],
        "avaDynamicDir":     ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "Ava", "Dynamic"],
        "userStaticDir":     ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "User", "Static"],
        "avaStaticDir":      ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "Ava", "Static"],
        
        "userRestrictedDir": ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "User", "Restricted"],
        "avaRestrictedDir":  ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "Ava", "Restricted"],

        "forgedSkillsDir":   ["AvaSphere", "Matrix", "Cognition", "Knowledge", "SkillGraph", "Skills", "Ava", "Forged"],
        "repertoireDir":     ["AvaSphere", "Matrix", "Cognition", "Attributes", "AvaAtts", "Assets", "Repertoire"],

        "knowledgeBaseDir":  ["AvaSphere", "Matrix", "Cognition", "Knowledge", "Learning", "KnowledgeBase"],
    }

    _docMap = {
        "textDir": ["Text"],
        "pdfDir":  ["Pdf"],
        "docxDir": ["Word"],
        "excDir":  ["Excel"],
    }

    _mediaMap = {
        "opticMedia1InputDir": ["Input", "Media1"],
        "opticMedia2InputDir": ["Input", "Media2"],
        "stmCreatedImages":    ["Output", "Images", "STM"],
        "ltmCreatedImages":    ["Output", "Images", "LTM"],
        "stmCreatedVideos":    ["Output", "Videos", "STM"],
        "ltmCreatedVideos":    ["Output", "Videos", "LTM"],
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._initializeLocalDirectories()
        self._initializeCloudDirectories()
        self._initializeBaseDirectories()
        self._assignComponentDirectories()
        self._loadRestrictedComponents()
        self._migrateLocalToCloud()
        self._ensureAllDirectories()

        self._initialized = True

    @staticmethod
    def _findLocalDir(markerFile=MARKER_FILE) -> Path | None:
        current = Path(__file__).resolve()

        # Step 1: Look for existing marker file
        for parent in current.parents:
            if (parent / markerFile).exists():
                return parent

        # Step 2: Fallback — use detectProjectLayout()'s output
        if (PROJECT_ROOT / markerFile).exists():
            return PROJECT_ROOT

        # Step 3: Last resort — create marker file at detected root
        markerPath = PROJECT_ROOT / markerFile
        markerPath.touch(exist_ok=True)
        return PROJECT_ROOT

    @staticmethod
    def _findCloudDir() -> Path | None:
        home    = Path.home()
        cloudCandidates = [
            "OneDrive", "Google Drive", "Google Drive File Stream",
            "Dropbox", "iCloudDrive", "Box", "pCloudDrive"
        ]
        for folder in home.iterdir():
            if folder.is_dir() and any(cloud.lower() in folder.name.lower() for cloud in cloudCandidates):
                return folder
        return None

    def _storageOption(self) -> str:
        load_dotenv(override=True)
        return os.getenv("STORAGE_OPTION", "Local").lower()

    def _initializeLocalDirectories(self) -> None:
        self.projectRoot = self._findLocalDir()
        if not self.projectRoot:
            raise RuntimeError(f"Could not locate {PROJECT_NAME}'s root file — make sure {MARKER_FILE} exists in the main folder.")

        self.startDir           = self.projectRoot
        self.sourceDir          = self.startDir / PROJECT_NAME
        self.localBackupDir     = self.startDir / "X BACKUPS X"
        self.localDatabaseDir   = self.startDir / "X DATABASE X"
        self.localDocumentsDir  = self.startDir / "X DOCUMENTS X"
        self.localProjectEnvDir = self.startDir / "X ENVS X"
        self.localLogsDir       = self.startDir / "X LOGS X"
        self.localMediaDir      = self.startDir / "X MEDIA X"
        self.localRecycleBinDir = self.startDir / "X RECYCLEBIN X"
        self.localVersionDir    = self.startDir / "X VERSION CONTROL X"

    def _initializeCloudDirectories(self) -> None:
        cloudParent = self._findCloudDir() or (self.startDir / "CloudFallback")
        self.cloudDir = cloudParent / PROJECT_NAME

        self.cloudBackupDir     = self.cloudDir / "X BACKUPS X"
        self.cloudDatabaseDir   = self.cloudDir / "X DATABASE X"
        self.cloudDocumentsDir  = self.cloudDir / "X DOCUMENTS X"
        self.cloudProjectEnvDir = self.cloudDir / "X ENVS X"
        self.cloudLogsDir       = self.cloudDir / "X LOGS X"
        self.cloudMediaDir      = self.cloudDir / "X MEDIA X"
        self.cloudRecycleBinDir = self.cloudDir / "X RECYCLEBIN X"
        self.cloudVersionDir    = self.cloudDir / "X VERSION CONTROL X"

    def _initializeBaseDirectories(self) -> None:
        storageOption = self._storageOption()

        dirMap = {
            "backupDir":     ("cloudBackupDir",     "localBackupDir"),
            "databaseDir":   ("cloudDatabaseDir",   "localDatabaseDir"),
            "documentsDir":  ("cloudDocumentsDir",  "localDocumentsDir"),
            "logsDir":       ("cloudLogsDir",       "localLogsDir"),
            "mediaDir":      ("cloudMediaDir",      "localMediaDir"),
            "recycleBinDir": ("cloudRecycleBinDir", "localRecycleBinDir"),
            "projectEnvDir": ("cloudProjectEnvDir", "localProjectEnvDir"),
            "versionDir":    ("cloudVersionDir",    "localVersionDir"),
        }

        for attr, (cloudAttr, localAttr) in dirMap.items():
            setattr(self, attr, getattr(self, cloudAttr if storageOption == "cloud" else localAttr))

    def _assignComponentDirectories(self) -> None:
        def assignFromMap(baseDir: Path, mapping: dict[str, list[str]]) -> None:
            for name, parts in mapping.items():
                setattr(self, name, baseDir.joinpath(*parts))

        assignFromMap(self.databaseDir,       self._dbMap)
        assignFromMap(self.documentsDir,      self._docMap)
        assignFromMap(self.mediaDir,          self._mediaMap)
        assignFromMap(Path(".").resolve(),    self._rootMap)

        self.songsDir = Path.home() / "Music"

    def _loadRestrictedComponents(self) -> None:
        self.excludeDirs = ['.vs', 'bin', 'obj', '__pycache__', '.git']

    def _ensureAllDirectories(self) -> None:
        for attr in dir(self):
            val = getattr(self, attr)
            if isinstance(val, Path):
                val.mkdir(parents=True, exist_ok=True)

    def _migrateLocalToCloud(self) -> None:
        if self._storageOption() != "cloud":
            return
        print("Migrating local directories to cloud storage...")
        migrations = [
            (self.localDatabaseDir,   self.cloudDatabaseDir),
            (self.localVersionDir,    self.cloudVersionDir),
            (self.localBackupDir,     self.cloudBackupDir),
            (self.localDocumentsDir,  self.cloudDocumentsDir),
            (self.localLogsDir,       self.cloudLogsDir),
            (self.localMediaDir,      self.cloudMediaDir),
            (self.localProjectEnvDir, self.cloudProjectEnvDir),
            (self.localRecycleBinDir, self.cloudRecycleBinDir),
        ]

        for src, dst in migrations:
            if src.exists():
                self._copyDirectory(src, dst)

    def _copyDirectory(self, source: Path, target: Path) -> int:
        target.mkdir(parents=True, exist_ok=True)
        count = 0
        for item in source.rglob("*"):
            dest = target / item.relative_to(source)
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            elif not dest.exists():
                shutil.copy2(item, dest)
                count += 1
        return count

    def getDir(self, name: str) -> Path | None:
        return getattr(self, name, None)

