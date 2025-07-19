import inspect
import importlib
from pathlib import Path
import logging

from AvaSphere.Matrix.Cognition.Database.Database import Database

logger = logging.getLogger(__name__)

class Repertoire:
    def __init__(self, filename: str, attr_name: str):
        self.components = {}
        self._filename = filename
        self._attr_name = attr_name
        self._load()

    def _load(self):
        try:
            db = Database()
            # get the Path to Jokes.py or Puns.py
            file_path: Path = Path(db.repertoireDir, self._filename).resolve()
            module_path = self._pathToModule(file_path)

            module = importlib.import_module(module_path)
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module_path:
                    continue
                inst = cls()
                if not hasattr(inst, self._attr_name):
                    continue
                key = self._normalizeKey(name)
                self.components[key] = getattr(inst, self._attr_name)

            #print(f"✅ Loaded {self._attr_name} classes: {list(self.components.keys())}")
        except Exception as e:
            logger.error(f"Error loading {self._attr_name} classes:", exc_info=True)

    def _pathToModule(self, path: Path) -> str:
        for parent in path.parents:
            if parent.name == "QuantumSphere":
                rel = path.relative_to(parent.parent)
                # strip “.py” suffix
                rel_no_ext = rel.with_suffix("")
                return ".".join(rel_no_ext.parts)
        raise RuntimeError("Could not determine module path — 'QuantumSphere' not found")

    # these two get overridden in subclasses
    def _normalizeKey(self, className: str) -> str:
        raise NotImplementedError


    def _splitCamelCase(self, s: str) -> list[str]:
        result, word = [], ""
        for c in s:
            if c.isupper() and word:
                result.append(word)
                word = c
            else:
                word += c
        result.append(word)
        return result


class Jokes(Repertoire):
    def __init__(self):
        super().__init__("Jokes.py", "jokes")

    def _normalizeKey(self, className: str) -> str:
        name = className.replace("Jokes", "")
        return " ".join(filter(None, map(str.lower, self._splitCamelCase(name))))


class Puns(Repertoire):
    def __init__(self):
        super().__init__("Puns.py", "puns")

    def _normalizeKey(self, className: str) -> str:
        name = className.replace("Puns", "")
        return " ".join(filter(None, map(str.lower, self._splitCamelCase(name))))
