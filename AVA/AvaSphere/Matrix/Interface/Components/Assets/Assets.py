
import os
from pathlib import Path

from AvaSphere.Matrix.Cognition.Database.Database import Database

BASE_DIR      = Path(Database().startDir)
UI_ASSETS_DIR = BASE_DIR / "X UI ASSETS X"

def assetsPath(*parts: str) -> str:
    return str((UI_ASSETS_DIR.joinpath(*parts)).resolve())

SOUNDS = {
    # 'online':   assetsPath("Media", "Wavs", "Open.wav"),
    # 'offline':  assetsPath("Media", "Wavs", "Open.wav"),
    # 'shutdown': assetsPath("Media", "Wavs", "Open.wav"),
    'hide':     assetsPath("Media", "Wavs", "Hide.wav"),
    'show':     assetsPath("Media", "Wavs", "Show.wav"),
    'exit':     assetsPath("Media", "Wavs", "Exit.wav"),
}

REGION_SOUNDS = {
    "region-1": [assetsPath("Media", "Mp3", "Alert.mp3")],
    "region-2": [assetsPath("Media", "Mp3", "Alert.mp3")],
    "region-3": [assetsPath("Media", "Mp3", "Alert.mp3")],
}

# GIFS = {
#     'open':        assetsPath("Graphics", "Gifs", "Open.gif"),
#     'close':       assetsPath("Graphics", "Gifs", "Close.gif"),
#     'recognize':   assetsPath("Graphics", "Gifs", "Recognize.gif"),
#     'processing':  assetsPath("Graphics", "Gifs", "Processing.gif"),
#     'synthesize':  assetsPath("Graphics", "Gifs", "Synthesize.gif"),
#     'show-brain':  assetsPath("Graphics", "Gifs", "ShowBrain.gif"),
#     'brain':       assetsPath("Graphics", "Gifs", "Brain.gif"),
#     'hide-brain':  assetsPath("Graphics", "Gifs", "HideBrain.gif"),
#     'still':       assetsPath("Graphics", "Gifs", "Still.gif"),
#     'activate':    assetsPath("Graphics", "Gifs", "Open.gif"),
#     'deactivate':  assetsPath("Graphics", "Gifs", "Close.gif"),
#     'online':      assetsPath("Graphics", "Gifs", "Still.gif"),
#     'offline':     assetsPath("Graphics", "Gifs", "Still.gif"),
# }

GIFS = {
    'open':        assetsPath("Graphics", "Gifs", "orb1.gif"),
    'close':       assetsPath("Graphics", "Gifs", "orb1.gif"),
    'recognize':   assetsPath("Graphics", "Gifs", "orb1.gif"),
    'processing':  assetsPath("Graphics", "Gifs", "orb1.gif"),
    'synthesize':  assetsPath("Graphics", "Gifs", "orb1.gif"),
    'show-brain':  assetsPath("Graphics", "Gifs", "orb1.gif"),
    'brain':       assetsPath("Graphics", "Gifs", "orb1.gif"),
    'hide-brain':  assetsPath("Graphics", "Gifs", "orb1.gif"),
    'still':       assetsPath("Graphics", "Gifs", "orb1.gif"),
    'activate':    assetsPath("Graphics", "Gifs", "orb1.gif"),
    'deactivate':  assetsPath("Graphics", "Gifs", "orb1.gif"),
    'online':      assetsPath("Graphics", "Gifs", "orb1.gif"),
    'offline':     assetsPath("Graphics", "Gifs", "orb1.gif"),
}


class AssetManager:
    @staticmethod
    def getSound(key: str) -> str:
        path = SOUNDS.get(key)
        return path if path and os.path.exists(path) else None

    @staticmethod
    def getRegionSounds(region: str) -> list[str]:
        return REGION_SOUNDS.get(region, [])

    @staticmethod
    def getRegionKeys() -> list[str]:
        return list(REGION_SOUNDS.keys())


    @staticmethod
    def getGif(state: str) -> str:
        return GIFS.get(state.lower())
