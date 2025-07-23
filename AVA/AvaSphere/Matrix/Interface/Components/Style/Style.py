
# from AvaSphere.Matrix.Cognition.Attributes.User.Assets.Profile.userProfile import UserIdentity, UserProfiles

# DEFAULT_COLOR = "red"

# def getFavoriteColor() -> str:
#     ui   = UserIdentity()
#     up   = UserProfiles()
#     user = ui.loadCurrentUserName()
#     print("User Name:", user)
    
#     favs = up.getUserProfile(userName=user, tableName="Favorites")

#     if favs and favs[0].get("color"):
#         color = favs[0]["color"].strip().lower()
#         print("Favorite Color:", color)
#         return color

#     print("Favorite Color:", DEFAULT_COLOR)
#     return DEFAULT_COLOR


# # FAVORITE_COLOR = "purple"
# FAVORITE_COLOR = getFavoriteColor()

# # ─── Constants ────────────────────────────────────────────────────────────────
# PRIMARY_BG_OPAQUE     = "rgba(0, 0, 0, 220)"
# PRIMARY_BG1           = "black"
# PRIMARY_BG2           = FAVORITE_COLOR

# BORDER_COLOR          = FAVORITE_COLOR
# BORDER_WIDTH          = "2px"
# BORDER_RADIUS_SMALL   = "5px"
# BORDER_RADIUS_DEFAULT = "10px"
# BORDER_RADIUS_LARGE   = "15px"

# PADDING_SMALL         = "2px"
# PADDING_DEFAULT       = "5px"
# PADDING_LARGE         = "10px"

# FONT_SIZE_DEFAULT     = "9pt"
# FONT_COLOR            = "white"

# TOGGLE_FONT_COLOR1    = "white"
# TOGGLE_FONT_COLOR2    = "black"

# FLASH_COLOR1          = FAVORITE_COLOR
# FLASH_COLOR2          = "white"


# # ─── Style Helpers ──────────────────────────────────────────────────────────
# def windowStyle() -> str:
#     return f"""
#         background-color: {PRIMARY_BG_OPAQUE};
#         border: {BORDER_WIDTH} solid {BORDER_COLOR};
#         border-radius: {BORDER_RADIUS_LARGE};
#     """

# def flashStyle(color):
#     return f"""
#         QLabel {{
#             color: {color};
#             font-size: {FONT_SIZE_DEFAULT};
#             font-weight: bold;
#             background-color: {PRIMARY_BG1};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#         }}
#     """

# def titleLabelStyle() -> str:
#     return f"""
#         QLabel {{
#             color: {FONT_COLOR};
#             font-size: {FONT_SIZE_DEFAULT};
#             font-weight: bold;
#             background-color: {PRIMARY_BG1};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#         }}
#     """


# def titleButtonStyle() -> str:
#     return f"""
#         QPushButton {{
#             background-color: {PRIMARY_BG1};
#             color: {FONT_COLOR};
#             font-weight: bold;
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#             padding: {PADDING_DEFAULT};
#             font-size: {FONT_SIZE_DEFAULT};
#         }}
#         QPushButton:hover {{
#             background-color: {PRIMARY_BG2};
#             color: {PRIMARY_BG1};
#         }}
#     """


# def textEditStyle(fs: int) -> str:
#     return f"""
#         QTextEdit {{
#             background-color: {PRIMARY_BG_OPAQUE};
#             color: {FONT_COLOR};
#             font-size: {fs}pt;
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#             padding: {PADDING_DEFAULT};
#         }}
#     """


# def actionButtonStyle(fs: int) -> str:
#     return f"""
#         QPushButton {{
#             background-color: {PRIMARY_BG1};
#             color: {FONT_COLOR};
#             font-size: {fs}pt;
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#             padding: {PADDING_DEFAULT};
#         }}
#         QPushButton:hover {{
#             background-color: {PRIMARY_BG2};
#             color: {PRIMARY_BG1};
#         }}
#     """


# def lineEditStyle(fs: int) -> str:
#     return f"""
#         QLineEdit {{
#             background-color: {PRIMARY_BG1};
#             color: {FONT_COLOR};
#             font-size: {fs}pt;
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#             padding: {PADDING_DEFAULT};
#         }}
#     """


# def comboBoxStyle() -> str:
#     return f"""
#         QComboBox {{
#             background-color: {PRIMARY_BG1};
#             color: {FONT_COLOR};
#             font-size: {FONT_SIZE_DEFAULT};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#             padding: {PADDING_DEFAULT};
#         }}
#         QComboBox::drop-down {{ border: none; }}
#         QComboBox QAbstractItemView {{
#             background-color: {PRIMARY_BG1};
#             color: {FONT_COLOR};
#             selection-background-color: {PRIMARY_BG2};
#         }}
#     """


# def toolButtonStyle() -> str:
#     return f"""
#         QToolButton {{
#             background-color: {PRIMARY_BG_OPAQUE};
#             color: {FONT_COLOR};
#             font-size: {FONT_SIZE_DEFAULT};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#             padding: {PADDING_DEFAULT};
#         }}
#         QToolButton::menu-indicator {{
#             image: none;
#             width: 0px;
#         }}
#     """


# def menuStyle() -> str:
#     return f"""
#         QMenu {{
#             background-color: {PRIMARY_BG1};
#             color: {FONT_COLOR};
#             font-size: {FONT_SIZE_DEFAULT};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_SMALL};
#             min-width: 350px;
#             max-height: 400px;
#         }}
#         QMenu::item:selected {{
#             background-color: {PRIMARY_BG2};
#             color: {PRIMARY_BG1};
#         }}
#         QMenu QScrollBar:vertical {{
#             border: 1px solid {PRIMARY_BG2};
#             background: {PRIMARY_BG1};
#             width: 16px;
#         }}
#         QMenu QScrollBar::handle:vertical {{
#             background: {PRIMARY_BG2};
#         }}
#     """


# def groupStyle() -> str:
#     return f"""
#         QGroupBox {{
#             background-color: {PRIMARY_BG_OPAQUE};
#             color: {FONT_COLOR};
#             font-size: {FONT_SIZE_DEFAULT};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_SMALL};
#             margin-top: 10px;
#         }}
#         QGroupBox::title {{
#             subcontrol-origin: margin;
#             subcontrol-position: top center;
#             padding: 2px 5px;
#         }}
#     """


# def toggleNormalStyle() -> str:
#     return f"""
#         QPushButton {{
#             background-color: {PRIMARY_BG1};
#             color: {TOGGLE_FONT_COLOR1};
#             font-size: {FONT_SIZE_DEFAULT};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#         }}
#     """


# def toggleSelectedStyle() -> str:
#     return f"""
#         QPushButton {{
#             background-color: {PRIMARY_BG2};
#             color: {TOGGLE_FONT_COLOR2};
#             font-size: {FONT_SIZE_DEFAULT};
#             border: {BORDER_WIDTH} solid {BORDER_COLOR};
#             border-radius: {BORDER_RADIUS_DEFAULT};
#         }}
#     """

from AvaSphere.Matrix.Cognition.Attributes.UserAtts.Assets.Profile.UserProfile import UserProfile

DEFAULT_COLOR = "blue"

# ─── Runtime Lookup ────────────────────────────────────────────────────────────
def getFavoriteColor() -> str:
    # up   = UserProfile()
    # user = up.identity.loadCurrentUserName()
    # favs = up.profiles.getUserProfile(userName=user, tableName="Favorites")

    # if favs and favs[0].get("color"):
    #     # strip any extra whitespace and lowercase
    #     return favs[0]["color"].strip().lower()

    return DEFAULT_COLOR



# ─── Constants ────────────────────────────────────────────────────────────────
PRIMARY_BG_OPAQUE     = "rgba(0, 0, 0, 220)"
PRIMARY_BG1           = "black"

BORDER_WIDTH          = "2px"
BORDER_RADIUS_SMALL   = "5px"
BORDER_RADIUS_DEFAULT = "10px"
BORDER_RADIUS_LARGE   = "15px"

PADDING_SMALL         = "2px"
PADDING_DEFAULT       = "5px"
PADDING_LARGE         = "10px"

FONT_SIZE_DEFAULT     = "9pt"
FONT_COLOR            = "white"

TOGGLE_FONT_COLOR1    = "white"
TOGGLE_FONT_COLOR2    = "black"

FLASH_COLOR2          = "white"


# ─── Style Helpers ──────────────────────────────────────────────────────────
def windowStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        background-color: {PRIMARY_BG_OPAQUE};
        border: {BORDER_WIDTH} solid {fav};
        border-radius: {BORDER_RADIUS_LARGE};
    """

def flashStyle(color):
    fav = getFavoriteColor()
    return f"""
        QLabel {{
            color: {color};
            font-size: {FONT_SIZE_DEFAULT};
            font-weight: bold;
            background-color: {PRIMARY_BG1};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
        }}
    """

def flashColor1():
    return getFavoriteColor()

def flashColor2():
    return FLASH_COLOR2

def titleLabelStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QLabel {{
            color: {FONT_COLOR};
            font-size: {FONT_SIZE_DEFAULT};
            font-weight: bold;
            background-color: {PRIMARY_BG1};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
        }}
    """

def titleButtonStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QPushButton {{
            background-color: {PRIMARY_BG1};
            color: {FONT_COLOR};
            font-weight: bold;
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
            padding: {PADDING_DEFAULT};
            font-size: {FONT_SIZE_DEFAULT};
        }}
        QPushButton:hover {{
            background-color: {fav};
            color: {PRIMARY_BG1};
        }}
    """

def textEditStyle(fs: int) -> str:
    fav = getFavoriteColor()
    return f"""
        QTextEdit {{
            background-color: {PRIMARY_BG_OPAQUE};
            color: {FONT_COLOR};
            font-size: {fs}pt;
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
            padding: {PADDING_DEFAULT};
        }}
    """

def actionButtonStyle(fs: int) -> str:
    fav = getFavoriteColor()
    return f"""
        QPushButton {{
            background-color: {PRIMARY_BG1};
            color: {FONT_COLOR};
            font-size: {fs}pt;
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
            padding: {PADDING_DEFAULT};
        }}
        QPushButton:hover {{
            background-color: {fav};
            color: {PRIMARY_BG1};
        }}
    """

def lineEditStyle(fs: int) -> str:
    fav = getFavoriteColor()
    return f"""
        QLineEdit {{
            background-color: {PRIMARY_BG1};
            color: {FONT_COLOR};
            font-size: {fs}pt;
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
            padding: {PADDING_DEFAULT};
        }}
    """

def comboBoxStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QComboBox {{
            background-color: {PRIMARY_BG1};
            color: {FONT_COLOR};
            font-size: {FONT_SIZE_DEFAULT};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
            padding: {PADDING_DEFAULT};
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{
            background-color: {PRIMARY_BG1};
            color: {FONT_COLOR};
            selection-background-color: {fav};
        }}
    """

def toolButtonStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QToolButton {{
            background-color: {PRIMARY_BG_OPAQUE};
            color: {FONT_COLOR};
            font-size: {FONT_SIZE_DEFAULT};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
            padding: {PADDING_DEFAULT};
        }}
        QToolButton::menu-indicator {{
            image: none;
            width: 0px;
        }}
    """

def menuStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QMenu {{
            background-color: {PRIMARY_BG1};
            color: {FONT_COLOR};
            font-size: {FONT_SIZE_DEFAULT};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_SMALL};
            min-width: 350px;
            max-height: 400px;
        }}
        QMenu::item:selected {{
            background-color: {fav};
            color: {PRIMARY_BG1};
        }}
        QMenu QScrollBar:vertical {{
            border: 1px solid {fav};
            background: {PRIMARY_BG1};
            width: 16px;
        }}
        QMenu QScrollBar::handle:vertical {{
            background: {fav};
        }}
    """

def groupStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QGroupBox {{
            background-color: {PRIMARY_BG_OPAQUE};
            color: {FONT_COLOR};
            font-size: {FONT_SIZE_DEFAULT};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_SMALL};
            margin-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 5px;
        }}
    """

def toggleNormalStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QPushButton {{
            background-color: {PRIMARY_BG1};
            color: {TOGGLE_FONT_COLOR1};
            font-size: {FONT_SIZE_DEFAULT};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
        }}
    """

def toggleSelectedStyle() -> str:
    fav = getFavoriteColor()
    return f"""
        QPushButton {{
            background-color: {fav};
            color: {TOGGLE_FONT_COLOR2};
            font-size: {FONT_SIZE_DEFAULT};
            border: {BORDER_WIDTH} solid {fav};
            border-radius: {BORDER_RADIUS_DEFAULT};
        }}
    """

