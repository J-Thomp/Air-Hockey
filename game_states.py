import arcade
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PADDLE_COLORS,
    MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE
)

class MenuManager:
    def __init__(self):
        # Menu items for each state
        self.menu_items = {
            MENU_STATE: ["Start Game", "Settings", "Quit"],
            SETTINGS_STATE: [
                "AI Difficulty", 
                "AI Color", 
                "Player Color", 
                "Max Score", 
                "Game Mode",
                "Time Limit",
                "Back"
            ],
            PAUSE_STATE: ["Resume", "Restart", "Main Menu"],
            GAME_OVER_STATE: ["Play Again", "Main Menu"]
        }
        
        self.selected_item = 0
        self.menu_positions = []
        
    def draw_menu(self, current_state, settings=None, game_over_message=""):
        """Draw the menu for the current game state"""
        # Clear menu positions
        self.menu_positions = []

        # Title
        arcade.draw_text(
            "AIR HOCKEY",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.7,
            arcade.color.BALL_BLUE,
            44,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            "Created by J-Thomp",
            SCREEN_WIDTH // 1.2,
            SCREEN_HEIGHT * 0.02,
            arcade.color.ORANGE_PEEL,
            10,
            anchor_x="center",
            anchor_y="center"
        )

        # Get menu items for current state
        menu_items = self.menu_items.get(current_state, [])
        
        # Draw game over message if in game over state
        if current_state == GAME_OVER_STATE:
            arcade.draw_text(
                game_over_message,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT * 0.5,
                arcade.color.WHITE,
                30,
                anchor_x="center",
                anchor_y="center"
            )

        # Draw each menu item
        for i, item in enumerate(menu_items):
            # Position settings menu higher
            if current_state == SETTINGS_STATE:
                y_pos = SCREEN_HEIGHT * 0.6 - i * 50
            else:
                y_pos = SCREEN_HEIGHT * 0.4 - i * 50
            
            # Determine item color
            if self.selected_item == i:
                color = arcade.color.YELLOW
            else:
                color = arcade.color.WHITE

            # Add special handling for settings items
            display_item = item
            if current_state == SETTINGS_STATE and settings:
                if item == "AI Difficulty":
                    difficulty_names = ["Easy", "Medium", "Hard"]
                    display_item += f": {difficulty_names[settings['ai_difficulty']]}"
                elif item == "AI Color":
                    selected_color = settings['ai_color']
                    display_item += f": {selected_color}"
                    # Draw the color name in its actual color
                    arcade.draw_text(
                        display_item,
                        SCREEN_WIDTH // 2,
                        y_pos,
                        PADDLE_COLORS[selected_color],
                        30,
                        anchor_x="center",
                        anchor_y="center"
                    )
                elif item == "Player Color":
                    selected_color = settings['player_color']
                    display_item += f": {selected_color}"
                    # Draw the color name in its actual color
                    arcade.draw_text(
                        display_item,
                        SCREEN_WIDTH // 2,
                        y_pos,
                        PADDLE_COLORS[selected_color],
                        30,
                        anchor_x="center",
                        anchor_y="center"
                    )
                elif item == "Max Score":
                    display_item += f": {settings['max_score']}"
                elif item == "Game Mode":
                    modes = ["Score", "Time"]
                    display_item += f": {modes[settings['game_mode']]}"
                elif item == "Time Limit":
                    display_item += f": {settings['time_limit']} min"

            # Draw text for non-color settings or if it hasn't been drawn yet
            if item not in ["AI Color", "Player Color"] or current_state != SETTINGS_STATE:
                arcade.draw_text(
                    display_item,
                    SCREEN_WIDTH // 2,
                    y_pos,
                    color,
                    30,
                    anchor_x="center",
                    anchor_y="center"
                )

            # Store menu item positions for click detection
            text_width = len(display_item) * 15  # Account for the full text width
            text_height = 30
            self.menu_positions.append({
                'item': i,
                'x': SCREEN_WIDTH // 2 - text_width // 2,
                'y': y_pos - text_height // 2,
                'width': text_width,
                'height': text_height
            })
            
    def check_mouse_over_menu(self, x, y):
        """Check if mouse is over a menu item and return its index"""
        for pos in self.menu_positions:
            if (pos['x'] <= x <= pos['x'] + pos['width'] and
                pos['y'] <= y <= pos['y'] + pos['height']):
                return pos['item']
        return None
    
    def handle_menu_click(self, item_index, current_state, settings=None, sound=None):
        """Handle menu item click and return new state if changed"""
        if sound:
            arcade.play_sound(sound)
            
        if current_state == MENU_STATE:
            if item_index == 0:  # Start Game
                return "start_game"
            elif item_index == 1:  # Settings
                return SETTINGS_STATE
            elif item_index == 2:  # Quit
                return "quit"
                
        elif current_state == SETTINGS_STATE and settings:
            if item_index == 0:  # AI Difficulty
                settings['ai_difficulty'] = (settings['ai_difficulty'] + 1) % 3
            elif item_index == 1:  # AI Color
                color_names = list(PADDLE_COLORS.keys())
                current_index = color_names.index(settings['ai_color'])
                next_index = (current_index + 1) % len(color_names)
                settings['ai_color'] = color_names[next_index]
            elif item_index == 2:  # Player Color
                color_names = list(PADDLE_COLORS.keys())
                current_index = color_names.index(settings['player_color'])
                next_index = (current_index + 1) % len(color_names)
                settings['player_color'] = color_names[next_index]
            elif item_index == 3:  # Max Score
                max_scores = [5, 7, 10, 15]
                current_index = max_scores.index(settings['max_score']) if settings['max_score'] in max_scores else 0
                settings['max_score'] = max_scores[(current_index + 1) % len(max_scores)]
            elif item_index == 4:  # Game Mode
                settings['game_mode'] = (settings['game_mode'] + 1) % 2
            elif item_index == 5:  # Time Limit
                time_limits = [1, 2, 3, 5]
                current_index = time_limits.index(settings['time_limit']) if settings['time_limit'] in time_limits else 0
                settings['time_limit'] = time_limits[(current_index + 1) % len(time_limits)]
            elif item_index == 6:  # Back to main menu
                return MENU_STATE
                
        elif current_state == PAUSE_STATE:
            if item_index == 0:  # Resume
                return "resume_game"
            elif item_index == 1:  # Restart
                return "restart_game"
            elif item_index == 2:  # Main Menu
                return MENU_STATE
                
        elif current_state == GAME_OVER_STATE:
            if item_index == 0:  # Play Again
                return "restart_game"
            elif item_index == 1:  # Main Menu
                return MENU_STATE
                
        return current_state  # Default: no state change