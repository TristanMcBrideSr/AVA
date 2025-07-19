
from datetime import date, datetime, timedelta

#from AvaSphere.Matrix.Cognition.Attributes.User.Assets.SpecialOccasions.SpecialOccasions import SpecialOccasions

class TintManager:
    EMOTION_KEYS = ("Neutral", "Happy", "Excited", "Ecstatic")

    def __init__(self):
        # self.specialOccasions = SpecialOccasions()
        self.override = False
        self.holiday = "SaintPatricks"
        self._initBaseTints()
        # self._initHolidayTints()
        #self.activeHoliday = self._detectTodayHoliday()

    def _initBaseTints(self):
        self._baseTints = {
            "Ecstatic":  (100, 0, 0, 45),     # deep red
            "Excited":   (100, 0, 0, 35),     # deep red
            "Happy":     (100, 0, 0, 25),     # deep red
            # "Ecstatic":  (30, 60, 160, 45),   # soft blue
            # "Excited":   (30, 60, 160, 35),   # soft blue
            # "Happy":     (30, 60, 160, 25),   # soft blue
            "Annoyed":   (0, 0, 0, 30),       # soft gray
            "Frustrated":(0, 0, 0, 75),       # soft gray
            "Angry":     (0, 0, 0, 105),      # soft gray
            "Pissed Off":(0, 0, 0, 150),      # soft gray
            "Neutral":   (255, 255, 255, 10), # soft white
            #"Neutral":   (30, 60, 160, 10),   # soft blue
            #"Lonely":    (30, 60, 160, 45),   # soft blue
            "Custom1": (0, 0, 139, 115),
            "Blue": (32, 0, 225, 125),    # darkest blue
            "Purple": (32, 0, 225, 175),     # darkest purple
            "Red": (100, 0, 0, 175),     # darkest red


        }

    def _initHolidayTints(self):
        self._holidayTints = {
            "SaintPatricks": {
                "Neutral":  (30, 60, 30, 15),    # soft green
                "Happy":    (50, 100, 50, 25),   # deep green
                "Excited":  (70, 140, 70, 35),   # deep green
                "Ecstatic": (90, 180, 90, 45),   # deep green
            },
            "Christmas": {
                "Neutral":  (220, 220, 220, 10), # soft gray
                "Happy":    (0, 120, 0, 25),     # deep green
                "Excited":  (180, 0, 0, 35),     # deep red
                "Ecstatic": (0, 180, 0, 45),     # deep green
            },
            "Easter": {
                "Neutral":  (250, 240, 220, 10),   # soft beige
                "Happy":    (255, 182, 193, 20),   # light pink
                "Excited":  (230, 210, 255, 30),   # light purple
                "Ecstatic": (255, 200, 230, 40),   # light pink
            },
            "Halloween": {
                "Neutral":  (255, 140, 0, 35),    # bright orange
                "Happy":    (255, 120, 0, 25),    # orange
                "Excited":  (180, 80, 0, 35),     # deep orange
                "Ecstatic": (100, 0, 100, 45),    # purple
            },
            "Thanksgiving": {
                "Neutral":  (210, 180, 140, 15),  # tan/brown
                "Happy":    (255, 204, 102, 25),  # light brown
                "Excited":  (255, 153, 51, 35),   # orange
                "Ecstatic": (204, 102, 0, 45),    # deep orange
            },
            "MothersDay": {
                "Neutral":  (255, 228, 225, 10),  # soft pink
                "Happy":    (255, 182, 193, 20),  # light pink
                "Excited":  (255, 105, 180, 30),  # bright pink
                "Ecstatic": (255, 20, 147, 40),   # deep pink
            },
            "FathersDay": {
                "Neutral":  (210, 225, 255, 10),  # soft blue
                "Happy":    (135, 206, 250, 20),  # light blue
                "Excited":  (70, 130, 180, 30),   # bold blue
                "Ecstatic": (25, 25, 112, 40),    # deep blue
            },
            "NewYear": {
                "Neutral":  (192, 192, 192, 10),  # silver
                "Happy":    (200, 200, 200, 20),  # light gray
                "Excited":  (180, 180, 180, 30),  # gray
                "Ecstatic": (160, 160, 160, 40),  # dark gray
            },
            "Valentines": {
                "Neutral":  (255, 240, 245, 10),  # soft pink
                "Happy":    (255, 182, 193, 25),  # light pink
                "Excited":  (255, 105, 180, 35),  # bright pink
                "Ecstatic": (255, 20, 147, 45),   # deep pink
            },
            "AprilFools": {
                "Neutral":  (180, 160, 200, 10),  # soft lavender
                "Happy":    (200, 140, 255, 20),  # playful violet
                "Excited":  (160, 90, 220, 30),   # bold purple
                "Ecstatic": (120, 60, 200, 40),   # deep royal purple
            },
            "Independence": {
                "Neutral":  (200, 200, 255, 10),  # soft blue
                "Happy":    (70, 130, 180, 25),   # bold blue
                "Excited":  (220, 20, 60, 35),    # bright red
                "Ecstatic": (255, 0, 0, 45),      # vibrant red
            },
        }

    def _detectTodayHoliday(self):
        if self.override:
            return self.holiday
        return self.specialOccasions.getTodayHoliday()

    def getTint(self, emotion):
        # if self.activeHoliday and emotion in self.EMOTION_KEYS:
        #     tint = self._holidayTints.get(self.activeHoliday, {}).get(emotion)
        #     if tint: return tint
        return self._baseTints.get(emotion)
