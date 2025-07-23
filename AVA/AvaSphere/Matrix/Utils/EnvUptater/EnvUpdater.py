from dotenv import load_dotenv
import os

class EnvUpdater:

    def updateEnvValue(self, key, newValue, filename=".env"):
        key, newValue = self._setEnvValue(key, newValue)
        if not os.path.exists(filename):
            return
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
        updated = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
                lines[i] = f"{key}={newValue}\n"
                updated = True
                break
        if not updated:
            lines.append(f"{key}={newValue}\n")
        with open(filename, "w", encoding="utf-8") as file:
            file.writelines(lines)
        load_dotenv(filename, override=True)

    def _setEnvValue(self, key, value):
        # If value contains comma, wrap in quotes (unless already quoted)
        if "," in value and not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        return key, value
    # def _setEnvValue(self, key, value):
    #     # Always wrap in quotes, unless already quoted
    #     if not (value.startswith('"') and value.endswith('"')):
    #         value = f'"{value}"'
    #     return key, value