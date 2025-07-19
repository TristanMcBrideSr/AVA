
import calendar
from datetime import datetime
from dateutil import parser
import logging

logger = logging.getLogger(__name__)


class AgeCalculator:
    def __init__(self, dob):
        self.dob = dob  # Store the date of birth string

    def calAge(self):
        return self._getAgeString(multiplierPerMonth=0)

    def calSelfAge(self):
        return self._getAgeString(multiplierPerMonth=70)

    def _getAgeString(self, multiplierPerMonth):
        try:
            # Validate input
            if not isinstance(self.dob, str) or self.dob.strip().upper() == "NA":
                return None

            # Parse DOB
            try:
                birthDate = parser.parse(self.dob)
            except (ValueError, TypeError):
                return None

            currentDate = datetime.now()

            # Total months difference
            totalMonths = ((currentDate.year - birthDate.year) * 12
                           + (currentDate.month - birthDate.month))
            ageDays = currentDate.day - birthDate.day

            # If day difference is negative, borrow one month
            if ageDays < 0:
                totalMonths -= 1
                # Map for last month and its year instead of if/else
                lastMonth = {True: 12, False: currentDate.month - 1}[currentDate.month == 1]
                lastMonthYear = {True: currentDate.year - 1, False: currentDate.year}[currentDate.month == 1]
                ageDays += calendar.monthrange(lastMonthYear, lastMonth)[1]

            # Compute years and leftover months, applying multiplier where needed
            ageYears = totalMonths // 12 + multiplierPerMonth * totalMonths
            remMonths = totalMonths % 12

            # If today is the birthday, just return years
            if (currentDate.month, currentDate.day) == (birthDate.month, birthDate.day):
                return f"{ageYears} years old"

            # Plural?suffix map
            suffix = {True: "", False: "s"}

            # Build components
            parts = []
            if ageYears > 0:
                parts.append(f"{ageYears} year{suffix[ageYears == 1]}")
            if remMonths > 0:
                parts.append(f"{remMonths} month{suffix[remMonths == 1]}")
            parts.append(f"{ageDays} day{suffix[ageDays == 1]}")

            # Join with commas and 'and'
            if len(parts) > 2:
                main = ", ".join(parts[:-1])
                ageStr = f"{main} and {parts[-1]}"
            elif len(parts) == 2:
                ageStr = f"{parts[0]} and {parts[1]}"
            else:
                ageStr = parts[0]

            return f"{ageStr} old"
        except Exception as e:
            logger.error(f"Error in calculating age:", exc_info=True)
            return None
