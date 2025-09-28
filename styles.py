# styles.py - Updated with readable 1.7x scaling instead of 5x
import os
from font_loader import font_loader

# Dark Pastel Theme Colors - GREY THEME
DARK_PASTEL_GREY = "#3a3a3a"      # Main dark pastel grey  
DARKER_GREY = "#2a2a2a"           # Darker grey for backgrounds
LIGHTER_GREY = "#4a4a4a"          # Slightly lighter grey
MEDIUM_GREY = "#505050"           # Medium grey for hover states
DARK_PASTEL_RED = "#8b4a4a"       # Dark pastel red for accents
LIGHTER_RED = "#a55a5a"           # Slightly lighter red
TEXT_COLOR = "#f5e6c0"            # Light beige text
BORDER_COLOR = "#2a2a2a"          # Dark border
ACTIVE_TAB_COLOR = "#3a3a3a"      # Dark grey for active tab (was green)
INACTIVE_TAB_COLOR = "#4a4a4a"    # Light grey for inactive tabs

def get_font_family_for_stylesheet():
    """Get the font family string for CSS stylesheets"""
    return font_loader.get_font_stylesheet_family()

def get_scaled_size(base_size):
    """Helper to get 1.7x scaled font size for readable text"""
    return int(base_size * 1.7)  # Changed from 5x to 1.7x for readable text

# Generate the main stylesheet with custom font and readable text
def get_main_stylesheet():
    """Generate the main stylesheet with proper font family and 1.7x larger fonts"""
    font_family = get_font_family_for_stylesheet()
    
    return f"""
QMainWindow {{
    color: {TEXT_COLOR};
    background-color: #000000;
}}

/* Set all widgets to black background with custom font - readable 1.7x scaling */
QWidget {{
    background-color: #000000;
    color: {TEXT_COLOR};
    font-family: {font_family};
    font-size: {get_scaled_size(14)}px;  /* 14px * 1.7 = 24px */
}}

/* Force custom font on all text elements - readable scaling */
QLabel, QPushButton, QCheckBox, QGroupBox, QTabWidget, QTabBar {{
    font-family: {font_family};
    font-size: {get_scaled_size(14)}px;  /* 14px * 1.7 = 24px */
}}

/* Tab Widget Styling - Simple and Clean with readable text */
QTabWidget::pane {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
    background-color: #000000;
}}

QTabWidget::tab-bar {{
    font-family: {font_family};
}}

QTabBar::tab {{
    font-family: {font_family};
    font-weight: bold;
    font-size: {get_scaled_size(12)}px;  /* 12px * 1.7 = 20px - readable tab text */
    background-color: {INACTIVE_TAB_COLOR};
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
    padding: 6px 14px;
    margin: 1px;
    min-width: 80px;
    max-height: 32px;
    color: {TEXT_COLOR};
}}

/* Active/Selected Tab - Dark Grey with readable text */
QTabBar::tab:selected {{
    background-color: {ACTIVE_TAB_COLOR};
    border-color: {BORDER_COLOR};
    color: {TEXT_COLOR};
    font-weight: bold;
    font-size: {get_scaled_size(12)}px;  /* 12px * 1.7 = 20px */
}}

QTabBar::tab:hover:!selected {{
    background-color: {LIGHTER_GREY};
    border-color: {DARK_PASTEL_RED};
}}

/* Force readable font on ALL elements */
* {{
    font-family: {font_family};
    font-size: {get_scaled_size(14)}px;  /* 14px * 1.7 = 24px */
}}

QSplitter {{
    background-color: #000000;
}}

QSplitter::handle {{
    background-color: {BORDER_COLOR};
    width: 4px;
}}

QSplitter::handle:hover {{
    background-color: {DARK_PASTEL_RED};
}}

/* Tool Panel Styling - BLACK backgrounds with readable text */
QScrollArea {{
    background-color: #000000;
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
}}

QScrollArea > QWidget {{
    background-color: #000000;
}}

QScrollArea > QWidget > QWidget {{
    background-color: #000000;
}}

QScrollBar:vertical {{
    background-color: {DARKER_GREY};
    width: 16px;
    border: 1px solid {BORDER_COLOR};
    border-radius: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {DARK_PASTEL_RED};
    border: 1px solid {BORDER_COLOR};
    border-radius: 0px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {LIGHTER_RED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background-color: {DARKER_GREY};
    border: 1px solid {BORDER_COLOR};
    height: 16px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background-color: {DARKER_GREY};
}}

/* Default Tool Buttons - SHARP EDGES with readable text */
QPushButton {{
    background-color: {DARK_PASTEL_RED};
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
    padding: 8px 10px;
    color: {TEXT_COLOR};
    font-weight: bold;
    font-size: {get_scaled_size(11)}px;  /* 11px * 1.7 = 19px - readable button text */
    min-height: 40px;
    max-height: 45px;
    text-align: center;
    font-family: {font_family};
}}

QPushButton:hover {{
    background-color: {LIGHTER_RED};
    border-color: {DARK_PASTEL_RED};
}}

QPushButton:pressed {{
    background-color: {DARK_PASTEL_RED};
    border: 2px inset {BORDER_COLOR};
}}

/* Settings Panel - BLACK background with readable text */
QGroupBox {{
    color: {TEXT_COLOR};
    font-weight: bold;
    font-size: {get_scaled_size(13)}px;  /* 13px * 1.7 = 22px - readable group titles */
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
    margin: 8px 0px;
    padding-top: 10px;
    background-color: #000000;
    font-family: {font_family};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 10px 0 10px;
    font-size: {get_scaled_size(13)}px;  /* 13px * 1.7 = 22px */
    background-color: {DARKER_GREY};
    font-family: {font_family};
}}

/* BOTH Checkboxes RED - External and FPS with readable text */
QCheckBox {{
    color: {TEXT_COLOR};
    spacing: 8px;
    font-size: {get_scaled_size(12)}px;  /* 12px * 1.7 = 20px - readable checkbox text */
    background-color: #000000;
    font-family: {font_family};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QCheckBox::indicator:unchecked {{
    background-color: {LIGHTER_GREY};
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
}}

/* ALL checkboxes use RED when checked */
QCheckBox::indicator:checked {{
    background-color: {DARK_PASTEL_RED};
    border: 2px solid {BORDER_COLOR};
    border-radius: 0px;
}}

/* Tool Windows with readable text */
QWebEngineView {{
    border: 2px solid {BORDER_COLOR};
}}

/* Make sure all labels have readable text */
QLabel {{
    font-family: {font_family};
    font-size: {get_scaled_size(14)}px;  /* 14px * 1.7 = 24px */
    color: {TEXT_COLOR};
}}
"""

# For backward compatibility, also provide the constant
MAIN_STYLESHEET = get_main_stylesheet()

def get_icon_path(tool_name):
    """Return the path to PNG icon for a tool, with fallback to emoji"""
    # Map tool names to their corresponding PNG file names
    icon_file_map = {
        "Clue Coordinates": "coordinates.png",
        "Clue Scroll Help": "cluehelp.png", 
        "World Map": "worldmap.png",
        "Highscores": "highscores.png",
        "Market Prices": "market.png",
        "Quest Help": "quests.png",
        "Skill Guides": "skillsguides.png",
        "Forums": "forums.png",
        "Skills Calculator": "skillscalculator.png",
        "Bestiary": "bestiary.png",
        "Lost City": "LostCity.png"  # Added Lost City icon mapping
    }
    
    # Get the PNG file name for this tool
    filename = icon_file_map.get(tool_name)
    if filename:
        # Check if the icons folder and file exist
        icon_path = os.path.join("icons", filename)
        if os.path.exists(icon_path):
            return icon_path
    
    # Fallback to emoji if PNG not found
    emoji_map = {
        "Clue Coordinates": "🗺",
        "Clue Scroll Help": "📜", 
        "World Map": "🗺️",
        "Highscores": "🏆",
        "Market Prices": "💰",
        "Quest Help": "🛡️",
        "Skill Guides": "📚",
        "Forums": "💬",
        "Skills Calculator": "🧮",
        "Bestiary": "🐉",
        "Lost City": "⚔️"  # Updated emoji for Lost City
    }
    return emoji_map.get(tool_name, "🔧")

def get_tool_urls():
    """Return mapping of tool names to their URLs"""
    return {
        "Forums": "https://lostcity.rs",
        "Clue Coordinates": "https://razgals.github.io/2004-Coordinates/",
        "Clue Scroll Help": "https://razgals.github.io/Treasure/",
        "World Map": "https://2004.lostcity.rs/worldmap", 
        "Highscores": "https://2004.lostcity.rs/hiscores",
        "Market Prices": "https://lostcity.markets",
        "Quest Help": "https://2004.losthq.rs/?p=questguides",
        "Skill Guides": "https://2004.losthq.rs/?p=skillguides",
        "Skills Calculator": "https://2004.losthq.rs/?p=calculators",
        "Bestiary": "https://2004.losthq.rs/?p=droptables"
    }
