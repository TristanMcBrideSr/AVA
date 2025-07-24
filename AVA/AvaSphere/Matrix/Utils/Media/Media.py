
import os
import base64
import cv2
import io
from PIL import Image

class Media:

    @staticmethod
    def getFrames(path, collect=5, defaultMime="jpeg"):
        ext = os.path.splitext(path)[1].lower()
        if ext in [".gif", ".webp"]:
            return Media.extractFramesPIL(path, collect)
        elif ext in [".mp4", ".webm"]:
            return Media.extractFramesVideo(path, collect)
        else:
            b64, mimeType = Media.encodeImageFile(path, defaultMime)
            return [(b64, mimeType, 0)]

    @staticmethod
    def encodeImageFile(path, mimeType="jpeg"):
        with open(path, "rb") as imgFile:
            data = imgFile.read()
            return base64.b64encode(data).decode("utf-8"), mimeType

    @staticmethod
    def extractFramesPIL(path, collect=5):
        with Image.open(path) as img:
            frame_count = getattr(img, "n_frames", 1)
            indices = list({0, frame_count - 1} | set(range(0, frame_count, collect)))
            indices = sorted(idx for idx in indices if idx < frame_count)
            frames = []
            for idx in indices:
                try:
                    img.seek(idx)
                except EOFError:
                    continue
                with io.BytesIO() as buffer:
                    img.convert("RGB").save(buffer, format="PNG")
                    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    frames.append((b64, "png", idx))
            return frames

    @staticmethod
    def extractFramesVideo(path, collect=5):
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        indices = list({0, total - 1} | set(range(0, total, collect)))
        indices = sorted(idx for idx in indices if idx < total)
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            success, image = cap.read()
            if not success:
                continue
            success, buffer = cv2.imencode(".jpg", image)
            if not success:
                continue
            b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
            frames.append((b64, "jpeg", idx))
        cap.release()
        return frames

    @staticmethod
    def unsupportedFormat(ext):
        raise ValueError(f"File format '{ext}' is not supported for Vision frame extraction")
