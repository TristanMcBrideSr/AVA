
import os
import re
import time
from pathlib import Path
import logging
from MediaCapture import MediaCapture

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Rec:
    def __init__(self, parent=None):
        self._initComponents(parent)

    def _initComponents(self, parent):
        self.parent              = parent
        self.db                  = self.parent.db
        self.mediaCapture        = MediaCapture()
        #self.router              = self.parent.router
        # self.echoMatrix          = self.parent.echoMatrix
        # self.neuralLink          = self.parent.neuralLink
        # self.getLink             = self.neuralLink.getLink("opticLink")
        # self.getCore             = self.neuralLink.getCore("opticCore")
        # self.baseFaceDir         = self.parent.db.userFaceDir
        # self.userCapturedFace    = self._getDir(self.baseFaceDir, "Captured", "CapturedImage.png")
        # self.forgetUserFaces     = self._getDir(self.baseFaceDir, "Forget")
        # self.rememberedUserFaces = self._getDir(self.baseFaceDir, "Remembered")

        self.baseInputDir        = self.db.opticInputDir
        self.capturedMediaFile   = self._getDir(self.baseInputDir, "CapturedImage.png")
        self.recordedMediaFile   = self._getDir(self.baseInputDir, "CapturedVideo.mp4")

        self.actionMap = {
            # Vision / Capture
            "look-ahead":              self.lookAhead,
            "look-behind":             self.lookBehind,
            "capture-screen":          self.captureScreen,

            # Recording
            "record-screen":           self.recordScreen,
            "record-front-webcam":     self.recordAhead,
            "record-rear-webcam":      self.recordRear,
            "view-surroundings":       self.recordSurroundings,

            # Description
            # "describe-self":           self.describeSelf,
            # "describe-brain":          self.describeBrain,
            "describe-media":          self.describeMedia,
            "compare-media":           self.compareMedia,
            "describe-created-media":  self.describeCreatedMedia,
            "describe-screenshot":     self.describeScreenShot,

            # Recognition
            # "recognize-user-frontcam": self.recognizeUserFrontCam,
            # "recognize-user-rearcam":  self.recognizeUserRearCam,
        }


    # def recognizeUserFrontCam(self) -> str:
    #     return self._recognizeUser(0)

    # def recognizeUserRearCam(self) -> str:
    #     return self._recognizeUser(1)

    def lookAhead(self, ctx: str) -> str:
        self.mediaCapture.captureMedia(self.capturedMediaFile, 0, normalize=True)
        return self.process(ctx, "lookAhead")

    def lookBehind(self, ctx: str) -> str:
        self.mediaCapture.captureMedia(self.capturedMediaFile, 1, normalize=True)
        return self.process(ctx, "lookBehind")

    def captureScreen(self, ctx: str) -> str:
        self.mediaCapture.captureScreen(self.capturedMediaFile)
        return self.process(ctx, "captureScreen")

    def recordScreen(self, ctx: str, duration: int = 10) -> str:
        self.mediaCapture.recordScreen(self.recordedMediaFile, duration)
        return self.process(ctx, "recordScreen")

    def recordAhead(self, ctx: str, duration: int = 10) -> str:
        self.mediaCapture.recordMedia(self.recordedMediaFile, 0, duration, normalize=True)
        return self.process(ctx, "recordFrontWebcam")

    def recordRear(self, ctx: str, duration: int = 10) -> str:
        self.mediaCapture.recordMedia(self.recordedMediaFile, 1, duration, normalize=True)
        return self.process(ctx, "recordRearWebcam")

    def captureSurroundings(self, ctx: str, camera1: int = 0, camera2: int = 1, duration: int = 10) -> str:
        self.mediaCapture.captureMedia(self.capturedMediaFile, camera1, camera2, duration, normalize=True)
        return self.process(ctx, "captureSurroundings")

    def recordSurroundings(self, ctx: str, camera1: int = 0, camera2: int = 1, duration: int = 10) -> str:
        self.mediaCapture.recordMedia(self.recordedMediaFile, camera1, camera2, duration, normalize=True)
        return self.process(ctx, "recordSurroundings")

    # def describeSelf(self, ctx: str) -> str:
    #     return self.process(ctx, "describeSelf")

    # def describeBrain(self, ctx: str) -> str:
    #     return self.process(ctx, "describeBrain")

    def describeMedia(self, ctx: str) -> str:
        return self.process(ctx, "describeMedia")

    def compareMedia(self, ctx: str) -> str:
        return self.process(ctx, "compareMedia")

    def describeCreatedMedia(self, ctx: str) -> str:
        return self.process(ctx, "describeCreatedMedia")

    def describeScreenShot(self, ctx: str) -> str:
        return self.process(ctx, "describeScreenShot")
        
    def process(self, ctx: str, mediaType: str) -> str:
        task = self._getMediaTasks().get(mediaType)
        if not task:
            raise ValueError(f"Unsupported media type: {mediaType}")

        message = task["message"]
        media   = task["media"]()

        return self._processMedia(message, *media) if isinstance(media, tuple) else self._processMedia(message, media)

    def _processMedia(self, ctx: str, media1: str, media2: str = None) -> str:
        mediaList = [m for m in [media1, media2] if m]
        if not mediaList:
            raise ValueError("No valid media files found.")
        #print(f"Processing media: {media1}")
        try:
            from AvaSphere.Matrix.Cognition.Router.Router import Router
            router = Router()
            # uploadedFiles = [self.getLink.files.upload(file=media1)]
            # if media2:
            #     uploadedFiles.append(self.getLink.files.upload(file=media2))

            # contentList = []
            # contentList.extend(uploadedFiles)
            # contentList.append("\n\n")
            # contentList.append(self._getInstructions().get("vision") + ":\n" + ctx)

            # completion = self.neuralLink.runNeuralProcess("optics", self.getLink, self.getCore, contentList)
            instructions=self._getInstructions().get("vision")
            completion = router.getVision(
                system=instructions,
                ctx=ctx,
                paths=mediaList
                )
            return completion
        except Exception as e:
            print(f"Error occurred while processing media: {e}")
            logger.error(f"Error processing media:", exc_info=True)
            return f"Media Processing Error: {e}"
        finally:
            self._removeFiles()

    def _getInstructions(self) -> dict:
        return {
            "vision": (
                f"Extract semantic meaning from the images "
                "and provide objective, concise data. Do not use JSON format. Maintain a light-hearted tone and be a smartass."
            ),
            "recognition": """
            f"Extract semantic meaning from the images "
                "and provide objective, concise data. Do not use JSON format. Maintain a light-hearted tone and be a smartass."
            """
        }

    def _getMediaTasks(self) -> dict:
        return {
            # "describeSelf": {
            #     "message":    "This is your self image. Describe yourself in the first person.",
            #     "media":      lambda: self._getSelf()
            # },
            # "describeBrain": {
            #     "message":    "This is your brain. Describe your brain in the first person.",
            #     "media":      lambda: self._getBrain()
            # },
            "describeCreatedMedia": {
                "message":    "This is the image or video you created.",
                "media":      lambda: self._getCreatedMedia()
            },
            "describeScreenShot": {
                "message":    "This is the screenshot you took.",
                "media":      lambda: self.capturedMediaFile
            },
            "captureScreen": {
                "message":    "This is what you see on the screen.",
                "media":      lambda: self.capturedMediaFile
            },
            "recordScreen": {
                "message":    "This is what you see on the screen.",
                "media":      lambda: self.recordedMediaFile
            },
            "lookAhead": {
                "message":    "This is what you see in front of you.",
                "media":      lambda: self.capturedMediaFile
            },
            "lookBehind": {
                "message":    "This is what you see behind you.",
                "media":      lambda: self.capturedMediaFile
            },
            "recordFrontWebcam": {
                "message":    "This is what you see in front of you.",
                "media":      lambda: self.recordedMediaFile
            },
            "recordRearWebcam": {
                "message":    "This is what you see behind you.",
                "media":      lambda: self.recordedMediaFile
            },
            "captureSurroundings": {
                "message":    "This is what you see around you. Describe what you see in front and behind.",
                "media":      lambda: self.capturedMediaFile
            },
            "describeMedia": {
                "message":    "This is the media you need to describe.",
                "media":      lambda: self._getMedia1()
            },
            "compareMedia": {
                "message":    "These are the images or videos to compare.",
                "media":      lambda: (self._getMedia1(), self._getMedia2())
            }
        }

    # def _getSelf(self) -> str:
    #     return self._getDir(self.db.selfImages, "Self.gif")

    # def _getBrain(self) -> str:
    #     return self._getDir(self.db.selfImages, "Brain.gif")

    def _getMedia1(self) -> str:
        return self._getNewestFile(self.db.opticMedia1InputDir)

    def _getMedia2(self) -> str:
        return self._getNewestFile(self.db.opticMedia2InputDir)

    def _getCreatedMedia(self) -> str:
        return self._getNewestFile(self.db.createdImages)

    def _getDir(self, *paths: str) -> str:
        return str(Path(*paths).resolve())

    def _getNewestFile(self, dirPath: str) -> str:
        dirPath = Path(dirPath)
        try:
            newestFile = max(
                (file for file in dirPath.rglob("*") if file.is_file()),
                key=lambda file: file.stat().st_mtime,
                default=None
            )
            return str(newestFile) if newestFile else None
        except Exception:
            return None

    def _removeFiles(self) -> None:
        mediaFiles = {
            #self.userCapturedFace, self.capturedMediaFile, self.recordedMediaFile
            self.capturedMediaFile, self.recordedMediaFile,
        }
        for file in mediaFiles:
            if file and os.path.exists(file):
                try:
                    os.remove(file)
                    #print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")
