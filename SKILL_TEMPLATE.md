
---

# **Skills Creation Guide**

## **Overview**

This framework enables you to write **skills**—modular logic units for controlling apps, services, or automation, with:

* **No decorators required**
* **No fragile schemas**
* **No accidental exposure:**
  Only what you make public is callable—**period**.

---

## **Skill Visibility & Exposure**

* **Anything public is exposed. Anything private (starting with `_`) is hidden.**
* Applies to:

  * Methods on a class
  * Standalone functions in a module
* No need for decorators, schemas, or wrappers.

---

## **Action Maps and Dispatchers**

* If you use an `actionMap` / `ACTION_MAP` / `action_map` and a dispatcher (like `appSkill`):

  * The framework **exposes the dispatcher** as the **Skill**.
  * It **auto-documents every mapped Action** (reading signatures for required/optional params).
* The actual private logic methods (like `_openApp`) are **never exposed directly**—they’re only called through your dispatcher/action map.

---

## **Direct Functions**

* Any **standalone public function** (not starting with `_`) is directly callable as a **Skill**.
* **Private helpers** (with `_`) are never exposed.

---

## **How It’s Parsed**

* **Every public method/function** is parsed as a **Skill**.
* **Dispatcher + Action Map:**

  * Only the **dispatcher** is exposed (e.g., `appSkill`).
  * All valid **Actions** and argument details are extracted from the map using **real Python signature inspection**.
* **No decorators, no fragile JSON, no vendor lock.**
  Just real Python, as flexible as you want.

---

# **How To Create Skills**

## **1. Singleton Class With Action Map**
Preferred way to create skills, as it allows for a clean structure and easy management of actions.

If you put `_openApp` and `_closeApp` in `actionMap` / `action_map`, they are callable. If not, they aren’t.

> **NOTE:**
> You do **not** have to use an action map—**any public method** is exposed as a skill/action automatically!

**What The Framework Outputs:**
For a singleton class with an action map and a public dispatcher:
It exposes only the dispatcher (like `appSkill`), but dynamically documents all **Actions** found in the action map, including each Action’s required/optional arguments.
But you can also make a class with public methods, and they will be exposed as skills/actions (no action map required).

```python
import logging
import subprocess
import os
import threading
import inspect

from SkillsManager import SkillsManager

logger = logging.getLogger(__name__)

NAME_REPLACEMENTS = {
    "vs code":     "code",
    "vs studio":   "devenv",
    "vs insiders": "code - insiders",
    "word":        "winword",
    "powerpoint":  "powerpnt",
    "explorer":    "iexplore",
}


## Singleton class for managing application actions
class Apps:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Apps, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.skillsManager    = SkillsManager()
        self.nameReplacements = NAME_REPLACEMENTS.copy()  # Copy to avoid modifying the original
        self.actionMap = {
            "open-app":  self._openApp,
            "close-app": self._closeApp
        }

    def appSkill(self, action: str, *args):
        self.skillsManager.argParser.printArgs(self, locals())
        name = inspect.currentframe().f_code.co_name
        return self.skillsManager.executeSkill('system', name, self.actionMap, action, *args)

    def _normalizeAppName(self, appName: str) -> str:
        app = appName.lower()
        return next(
            (replacement for key, replacement in self.nameReplacements.items() if key in app),
            appName
        )

    def _openApp(self, appName: str) -> str:
        app = self._normalizeAppName(appName)
        try:
            os.startfile(app)
            return f"Opened {app}"
        except Exception as e:
            logger.error(f"Error opening {app}:", exc_info=True)
            return f"An error occurred while trying to open {app}: {e}"

    def _closeApp(self, appName: str) -> str:
        app = self._normalizeAppName(appName)
        if not app.lower().endswith('.exe'):
            app += '.exe'
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", app],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return f"Closed {app}"
        except Exception as e:
            logger.error(f"Error closing {app}:", exc_info=True)
            return f"An error occurred while trying to close {app}: {e}"

    def publicFunction(self, ...):
        pass  # This function is callable as an action even if it's not in the action map (Not recommended for clarity if using action map)

    def _privateHelper(self, ...):
        pass  # This function is private and will not be exposed as an action
```

---

## **2. Standalone Functions With Action Map**

If you put `_openApp` and `_closeApp` in `ACTION_MAP`, they are callable. If not, they aren’t.
Only the dispatcher is exposed as the **Skill/Action**;
all valid **Actions** and argument info are read out of the `ACTION_MAP`.

```python
import os
import subprocess
import inspect
from SkillsManager import ArgumentParser

NAME_REPLACEMENTS = {
    "vs code":     "code",
    "vs studio":   "devenv",
    "vs insiders": "code - insiders",
    "word":        "winword",
    "powerpoint":  "powerpnt",
    "explorer":    "iexplore",
}

def _privateHelper(...):
    pass  # This function is private and will not be exposed as an action

def _openApp(appName: str) -> str:
    for key, value in NAME_REPLACEMENTS.items():
        if key in appName.lower():
            appName = value
            break
    try:
        os.startfile(appName)
        return f"Opened {appName}"
    except Exception as e:
        return f"An error occurred while trying to open {appName}: {e}"

def _closeApp(appName: str) -> str:
    for key, value in NAME_REPLACEMENTS.items():
        if key in appName.lower():
            appName = value
            break
    if not appName.lower().endswith('.exe'):
        appName += '.exe'
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", appName],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return f"Closed {appName}"
    except Exception as e:
        return f"An error occurred while trying to close {appName}: {e}"

ACTION_MAP = {
    "open-app": _openApp,
    "close-app": _closeApp,
}

argParser = ArgumentParser()

def appSkill(action: str, *args):
    argParser.printArgs("appSkill", locals())
    action = action.lower()
    actionKey = ACTION_MAP.get(action)
    if not actionKey:
        return f"Invalid appUtilAction provided: {action}"
    try:
        paramCount = len(inspect.signature(actionKey).parameters)
        return actionKey(*args[:paramCount]) if paramCount else actionKey()
    except Exception as e:
        return f"An error occurred while executing '{action}': {e}"
```

---

## **3. Standalone Public Functions (No Class, No Action Map Required)**

Whatever you put in the file is callable, as long as it’s not private (starts with `_`).
Each public function is exposed directly as a skill/action.
Private (underscore-prefixed) helpers are ignored.

```python
import os
import subprocess
from SkillsManager import ArgumentParser

NAME_REPLACEMENTS = {
    "vs code":     "code",
    "vs studio":   "devenv",
    "vs insiders": "code - insiders",
    "word":        "winword",
    "powerpoint":  "powerpnt",
    "explorer":    "iexplore",
}

argParser = ArgumentParser()

def openApp(appName: str) -> str:
    argParser.printArgs("openApp", locals())
    for key, value in NAME_REPLACEMENTS.items():
        if key in appName.lower():
            appName = value
            break
    try:
        os.startfile(appName)
        return f"Opened {appName}"
    except Exception as e:
        return f"An error occurred while trying to open {appName}: {e}"

def closeApp(appName: str) -> str:
    argParser.printArgs("closeApp", locals())
    for key, value in NAME_REPLACEMENTS.items():
        if key in appName.lower():
            appName = value
            break
    if not appName.lower().endswith('.exe'):
        appName += '.exe'
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", appName],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return f"Closed {appName}"
    except Exception as e:
        return f"An error occurred while trying to close {appName}: {e}"

def _privateHelper(...):
    pass  # This function is private and will not be exposed as an action
```

---

## **What’s a “Skill” vs. an “Action”?**

* **Skill:**
  The main public entry point for a capability, typically a dispatcher function/method.
  *Example: `appSkill` is the Skill that handles app-related actions.*

* **Actions:**
  The set of operations the Skill can perform—these are mapped in your `actionMap` / `ACTION_MAP` / `action_map`.
  *Example: `"open-app"`, `"close-app"`, etc.—each mapped to their own (often private) function.*

#### **Quick Example:**

```python
class Apps:
    def __init__(self):
        self.actionMap = {
            "open-app":  self._openApp,
            "close-app": self._closeApp
        }

    def appSkill(self, action: str, *args):
        # SKILL: Exposed as callable
        actionKey = self.actionMap.get(action.lower())
        if actionKey is None:
            return f"Invalid action"
        return actionKey(*args)

    def _openApp(self, appName: str):
        # ACTION: Only accessible via appSkill dispatcher, not directly exposed
        pass

    def _closeApp(self, appName: str):
        # ACTION: Only accessible via appSkill dispatcher, not directly exposed
        pass

```

* `appSkill` is the **Skill**.
* `"open-app"` and `"close-app"` are **Actions** that the Skill can perform.

---

