import arcade

# Game window constants
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 680
SCREEN_TITLE = "Air Hockey"

# Game objects dimensions
PADDLE_RADIUS = 30
PUCK_RADIUS = 20
FRICTION = 0.99
WALL_BOUNCE_DAMPING = 0.8

# Goal dimensions
GOAL_WIDTH = 170
GOAL_HEIGHT = 10

# AI constants
AI_SPEED = 8
AI_AGGRESSION = 0.7  # How aggressively AI moves to hit puck (0-1)
AI_DEFENSE_POSITION = 0.75  # Default position (percentage of screen height)

# Game states
MENU_STATE = "menu"
GAME_STATE = "game"
SETTINGS_STATE = "settings"
GAME_OVER_STATE = "game_over"
PAUSE_STATE = "pause"

# Rink constants
CORNER_RADIUS = 70  # Radius of the rounded corners

# Available paddle colors
PADDLE_COLORS = {
    "Red": arcade.color.RED,
    "Blue": arcade.color.BLUE,
    "Green": arcade.color.GREEN,
    "Yellow": arcade.color.YELLOW,
    "Purple": arcade.color.PURPLE,
    "Orange": arcade.color.ORANGE,
    "Cyan": arcade.color.CYAN,
    "Pink": arcade.color.PINK
}

# Sound file paths
SOUND_FILES = [
    "sounds/vgmenuselect.wav",
    "sounds/goal_sound.wav",
    "sounds/paddle_hit.wav",
    "sounds/wall_hit.wav",
    "sounds/power_up.wav"
]