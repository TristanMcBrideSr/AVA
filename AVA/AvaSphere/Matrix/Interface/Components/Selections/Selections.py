
import os
from dotenv import load_dotenv

load_dotenv()

# ─── CLWindow Section definitions ────────────────────────────────────────────────────
CLSECTION_FIELDS = {
    "User":     [("username", "Username")],
    "Personal": [
        ("name",       "Name"),
        ("maidenName", "Maiden Name"),
        ("nickname",   "Nickname"),
        ("dob",        "Date of Birth"),
        ("birthPlace", "Birth Place"),
    ],
    "Contact": [
        ("phoneNumber",     "Phone Number"),
        ("address",         "Address"),
        ("emailAddress1",   "Email 1"),
        ("gmailPassword",   "Gmail Password"),
        ("emailAddress2",   "Email 2"),
        ("outlookPassword", "Outlook Password"),
    ],
    "Security": [
        ("password",          "Password"),
        ("pinCode",           "PIN Code"),
        ("securityQuestion1", "Security Question 1"),
        ("securityQuestion2", "Security Question 2"),
        ("securityQuestion3", "Security Question 3"),
    ],
    "Medical": [
        ("height",            "Height"),
        ("weight",            "Weight"),
        ("bloodType",         "Blood Type"),
        ("medications",       "Medications"),
        ("allergies",         "Allergies"),
        ("allergicReactions", "Allergic Reactions"),
    ],
    "Family": [
        ("relationType",    "Relation Type"),
        ("relatedUsername", "Related Username"),
    ],
    "Favorites": [
        ("color",            "Favorite Color"),
        ("number",           "Favorite Number"),
        ("season",           "Favorite Season"),
        ("holiday",          "Favorite Holiday"),
        ("footballTeam",     "Favorite Football Team"),
        ("baseballTeam",     "Favorite Baseball Team"),
        ("basketballTeam",   "Favorite Basketball Team"),
        ("hockeyTeam",       "Favorite Hockey Team"),
        ("soccerTeam",       "Favorite Soccer Team"),
        ("collegeTeam",      "Favorite College Team"),
        ("athlete",          "Favorite Athlete"),
        ("sport",            "Favorite Sport"),
        ("song",             "Favorite Song"),
        ("artist",           "Favorite Artist"),
        ("genre",            "Favorite Genre"),
        ("album",            "Favorite Album"),
        ("band",             "Favorite Band"),
        ("composer",         "Favorite Composer"),
        ("singer",           "Favorite Singer"),
        ("playlist",         "Favorite Playlist"),
        ("musicVideo",       "Favorite Music Video"),
        ("movie",            "Favorite Movie"),
        ("movieGenre",       "Favorite Movie Genre"),
        ("movieSeries",      "Favorite Movie Series"),
        ("movieSeriesGenre", "Favorite Movie Series Genre"),
        ("tvShow",           "Favorite TV Show"),
        ("tvShowGenre",      "Favorite TV Show Genre"),
        ("tvSeries",         "Favorite TV Series"),
        ("tvSeriesGenre",    "Favorite TV Series Genre"),
        ("book",             "Favorite Book"),
        ("bookGenre",        "Favorite Book Genre"),
        ("bookSeries",       "Favorite Book Series"),
        ("bookSeriesGenre",  "Favorite Book Series Genre"),
        ("game",             "Favorite Game"),
        ("gameGenre",        "Favorite Game Genre"),
        ("gameSeries",       "Favorite Game Series"),
        ("gameSeriesGenre",  "Favorite Game Series Genre"),
        ("food",             "Favorite Food"),
        ("drink",            "Favorite Drink"),
        ("dessert",          "Favorite Dessert"),
        ("snack",            "Favorite Snack"),
        ("candy",            "Favorite Candy"),
        ("breakfast",        "Favorite Breakfast"),
        ("lunch",            "Favorite Lunch"),
        ("dinner",           "Favorite Dinner"),
        ("fastFood",         "Favorite Fast Food"),
        ("restaurant",       "Favorite Restaurant"),
        ("candyBar",         "Favorite Candy Bar"),
        ("iceCream",         "Favorite Ice Cream"),
    ],
    "Pets": [
        ("name",     "Pet Name"),
        ("species",  "Species"),
        ("dob",      "DOB"),
        ("gender",   "Gender"),
        ("breed",    "Breed"),
        ("color",    "Color"),
        ("eyeColor", "Eye Color"),
    ],
}

ADD_VARARGS_SECTIONS = {"Personal", "Contact", "Security", "Medical"}
ADD_DICT_SECTIONS    = {"Favorites", "Pets"}
UPDATE_SECTIONS      = list(ADD_VARARGS_SECTIONS | ADD_DICT_SECTIONS)



# ─── CRWindow Section definitions ────────────────────────────────────────────────────
# ─── Mappings for Self-Profile sections ─────────────────────────────────────
SELF_SECTIONS = [
    ("Name",       "Name"),
    ("Gender",     "Gender"),
    ("Type",       "Type"),
    ("Accent",     "Accent"),
    ("Language",   "Language"),
    ("Motto",      "Motto"),
    ("Persona",    "Persona"),
    ("Personality","Personality"),
]

LOAD_DEFAULTS = {
    "Name":        ("current", os.getenv("ASSISTANT_NAME", "AVA")),
    "Gender":      ("current", "Not Specified"),
    "Type":        ("current", "Self"),
    "Accent":      ("current", ""),
    "Language":    ("current", "English"),
    "Motto":       ("current", ""),
    "Persona":     ("current", "Default"),
    "Personality": ("current", "Default"),
}

# ─── Mappings for Family and Pet sub-forms ──────────────────────────────────
FAMILY_FIELDS = ["Relationship", "Name", "Nickname"]
PET_FIELDS    = ["Name", "Nickname", "Gender", "Breed"]


# ─── BCWindow Section definitions ────────────────────────────────────────────────────
BCSECTION_FIELDS = {
    "Production-Inputs": [
        ("Default User",               "DEFAULT_USER_NAME"),
        ("Default Assistant Name",     "ASSISTANT_NAME"),
        ("Default Standby Words",      "STANDBY"),
        ("Default Deactivation Words", "DEACTIVATION"),

        ("OpenAI Key",                 "OPENAI_API_KEY"),
        ("Google Key",                 "GOOGLE_API_KEY"),

        ("OpenAI Chat Model",          "OPENAI_RESPONSE_MODEL"),
        ("Google Chat Model",          "GOOGLE_RESPONSE_MODEL"),

        ("OpenAI Vision Model",        "OPENAI_VISION_MODEL"),
        ("Google Vision Model",        "GOOGLE_VISION_MODEL"),
    ],
    "Production-Toggles": [
        ("Cloud Storage",         "STORAGE_OPTION", "Cloud", "Local"),
        ("Activate Skill Sync",   "ACTIVATE_SKILL_SYNC"),
        ("Activate Memory",       "ACTIVATE_MEMORY"),
        ("Activate Learning",     "ACTIVATE_LEARNING"),
        ("Activate Freewill",     "ACTIVATE_FREEWILL"),
        # ("Activate Emotions",     "ACTIVATE_EMOTIONS"),
        # ("Activate Feelings",     "ACTIVATE_FEELINGS"),
        # ("Activate Politics",     "ACTIVATE_POLITICS"),
        # ("Activate Filler Words", "ACTIVATE_FILLERWORDS"),
        # ("Activate Profanity",    "ACTIVATE_PROFANITY"),

        ("Dev Toggles",           "DEV_TOGGLES"),
    ],
    "Dev-Toggles": [
        ("Dev Override",                    "DEV_OVERRIDE"),

        ("Show Skills",                     "SHOW_SKILLS"),
        ("Show Metadata",                   "SHOW_METADATA"),
        ("Show Called Actions",             "SHOW_CALLED_ACTIONS"),
        ("Show Learning Process",           "SHOW_LEARNING_PROCESS"),

        ("Show Tokens Usage",               "SHOW_TOKENS"),
        ("Clear Caches (Restart Required)", "CLEAR_CACHES"),
    ],
}