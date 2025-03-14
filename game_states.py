import arcade
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PADDLE_COLORS,
    MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE, HOW_TO_PLAY_STATE
)

class MenuManager:
    def __init__(self):
        # Menu items for each state
        self.menu_items = {
            MENU_STATE: ["Start Game", "How To Play", "Settings", "Quit"],
            SETTINGS_STATE: [
                "AI Difficulty", 
                "AI Color", 
                "Player Color", 
                "Max Score", 
                "Game Mode",
                "Time Limit",
                "Power-ups",
                "Power-up Frequency",
                "Back"
            ],
            PAUSE_STATE: ["Resume", "Restart", "Main Menu"],
            GAME_OVER_STATE: ["Play Again", "Main Menu"],
            HOW_TO_PLAY_STATE: ["Back"]
        }
        
        self.selected_item = 0
        self.menu_positions = []
        
    def draw_menu(self, current_state, settings=None, game_over_message=""):
        """Draw the menu for the current game state"""
        # Clear menu positions
        self.menu_positions = []

        # Title - moved higher up
        arcade.draw_text(
            "AIR HOCKEY",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.85,  # Moved from 0.7 to 0.85
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

        # Handle How To Play screen
        if current_state == HOW_TO_PLAY_STATE:
            self.draw_how_to_play()
            return

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
            # Position menus
            if current_state == SETTINGS_STATE:
                # Settings menu - smaller text and more compact spacing
                text_size = 22  # Reduced from 30
                spacing = 35    # Reduced from 50
                y_pos = SCREEN_HEIGHT * 0.7 - i * spacing  # Moved up from 0.6
            else:
                # Main menu and other menus
                text_size = 30
                spacing = 50
                y_pos = SCREEN_HEIGHT * 0.4 - i * spacing
            
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
                        text_size,  # Use the smaller text size
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
                        text_size,  # Use the smaller text size
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
                elif item == "Power-ups":
                    display_item += f": {'On' if settings['power_ups_enabled'] else 'Off'}"
                elif item == "Power-up Frequency":
                    frequency_names = ["Low", "Medium", "High"]
                    display_item += f": {frequency_names[settings['power_up_frequency']]}"

            # Draw text for non-color settings or if it hasn't been drawn yet
            if item not in ["AI Color", "Player Color"] or current_state != SETTINGS_STATE:
                arcade.draw_text(
                    display_item,
                    SCREEN_WIDTH // 2,
                    y_pos,
                    color,
                    text_size,  # Use the appropriate text size
                    anchor_x="center",
                    anchor_y="center"
                )

            # Store menu item positions for click detection
            # Adjust text width calculation based on text size
            text_width = len(display_item) * (text_size // 2)  # Adjusted text width calculation
            text_height = text_size
            self.menu_positions.append({
                'item': i,
                'x': SCREEN_WIDTH // 2 - text_width // 2,
                'y': y_pos - text_height // 2,
                'width': text_width,
                'height': text_height
            })
    
    def draw_how_to_play(self):
        """Draw the How To Play screen"""
        # Title
        arcade.draw_text(
            "HOW TO PLAY",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.75,
            arcade.color.WHITE,
            30,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Controls section
        arcade.draw_text(
            "CONTROLS:",
            SCREEN_WIDTH // 2 - 130,  # Shifted left
            SCREEN_HEIGHT * 0.65,
            arcade.color.YELLOW,
            22,  # Smaller text
            anchor_x="left",  # Left-aligned
            anchor_y="center"
        )
        
        # List of controls
        controls = [
            "- Mouse: Move paddle",
            "- ESC: Pause game",
            "- CTRL+D: Toggle debug view"
        ]
        
        for i, control in enumerate(controls):
            arcade.draw_text(
                control,
                SCREEN_WIDTH // 2 - 130,  # Shifted left
                SCREEN_HEIGHT * 0.58 - i * 26,  # Adjusted spacing
                arcade.color.WHITE,
                16,  # Smaller text
                anchor_x="left",  # Left-aligned
                anchor_y="center"
            )
        
        # Power-ups section
        arcade.draw_text(
            "POWER-UPS:",
            SCREEN_WIDTH // 2 - 130,  # Shifted left
            SCREEN_HEIGHT * 0.45,  # Adjusted position
            arcade.color.YELLOW,
            22,  # Smaller text
            anchor_x="left",  # Left-aligned
            anchor_y="center"
        )
        
        # Draw power-up examples and descriptions
        power_ups = [
            {"color": arcade.color.YELLOW, "icon": "⚡", "name": "Speed", "desc": "Cross midline & faster hits"},
            {"color": arcade.color.GREEN, "icon": "+", "name": "Size", "desc": "Increases paddle size"},
            {"color": arcade.color.CYAN, "icon": "❄", "name": "Freeze", "desc": "Freezes opponent for 3s"},
            {"color": arcade.color.ORANGE, "icon": "◉◉◉", "name": "Multi-Puck", "desc": "Creates 3 paddles"},
            {"color": arcade.color.PURPLE, "icon": "⊏⊐", "name": "Goal Shrink", "desc": "Shrinks your goal by 50%"},
            {"color": arcade.color.RED, "icon": "↗", "name": "Repulsor", "desc": "Pulls puck toward opponent"}
        ]
        
        for i, power_up in enumerate(power_ups):
            # Calculate position
            y_pos = SCREEN_HEIGHT * 0.38 - i * 30  # Reduced spacing between items
            
            # Draw power-up circle
            arcade.draw_circle_filled(
                SCREEN_WIDTH // 2 - 130,  # Shifted left
                y_pos,
                12,  # Slightly smaller circles
                power_up["color"]
            )
            
            # Draw inner circle for visual appeal
            arcade.draw_circle_filled(
                SCREEN_WIDTH // 2 - 130,  # Shifted left
                y_pos,
                8,  # Slightly smaller circles
                (255, 255, 255, 100)
            )
            
            # Draw power-up icon
            text_size = 11 if power_up["icon"] == "◉◉◉" else 16  # Smaller icons
            arcade.draw_text(
                power_up["icon"],
                SCREEN_WIDTH // 2 - 130,  # Shifted left
                y_pos,
                arcade.color.BLACK,
                text_size,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Draw power-up name and description
            arcade.draw_text(
                f"{power_up['name']}: {power_up['desc']}",
                SCREEN_WIDTH // 2 - 105,  # Shifted left with spacing from icon
                y_pos,
                arcade.color.WHITE,
                15,  # Smaller text
                anchor_x="left",
                anchor_y="center"
            )
        
        # Back button
        back_y_pos = SCREEN_HEIGHT * 0.08
        arcade.draw_text(
            "Back",
            SCREEN_WIDTH // 2,
            back_y_pos,
            arcade.color.YELLOW if self.selected_item == 0 else arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Store back button position for click detection
        text_width = len("Back") * 12
        text_height = 24
        self.menu_positions.append({
            'item': 0,
            'x': SCREEN_WIDTH // 2 - text_width // 2,
            'y': back_y_pos - text_height // 2,
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
            elif item_index == 1:  # How To Play
                return HOW_TO_PLAY_STATE
            elif item_index == 2:  # Settings
                return SETTINGS_STATE
            elif item_index == 3:  # Quit
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
            elif item_index == 6:  # Power-ups Toggle
                settings['power_ups_enabled'] = not settings['power_ups_enabled']
            elif item_index == 7:  # Power-up Frequency
                settings['power_up_frequency'] = (settings['power_up_frequency'] + 1) % 3
            elif item_index == 8:  # Back to main menu
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
                
        elif current_state == HOW_TO_PLAY_STATE:
            if item_index == 0:  # Back
                return MENU_STATE
                
        return current_state  # Default: no state change