import arcade
import math
import random
import os

# Game constants
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 680
SCREEN_TITLE = "Air Hockey"

PADDLE_RADIUS = 30
PUCK_RADIUS = 20
FRICTION = 0.99
WALL_BOUNCE_DAMPING = 0.8

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
GAME_OVER_STATE = "game_over"  # New state for game over screen
PAUSE_STATE = "pause"  # New state for pause screen

# Available paddle colors
PADDLE_COLORS = {
    "Red": arcade.color.RED,
    "Blue": arcade.color.BLUE,
    "Green": arcade.color.GREEN,
    "Yellow": arcade.color.YELLOW,
    "Purple": arcade.color.PURPLE,
    "Orange": arcade.color.ORANGE,
    "Cyan": arcade.color.CYAN,  # Added more color options
    "Pink": arcade.color.PINK
}

class AirHockeyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player1_paddle = None
        self.player2_paddle = None
        self.puck = None
        self.player1_score = 0
        self.player2_score = 0
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Game timer
        self.game_time = 0
        self.timer_active = False
        
        # Particle effects lists
        self.particles = []
        
        # Power-up system
        self.power_ups = []
        self.power_up_timer = 0
        self.player_power_up_active = False
        self.player_power_up_time = 0
        self.ai_power_up_active = False
        self.ai_power_up_time = 0

        # Game settings
        self.settings = {
            'ai_difficulty': 1,  # 0: Easy, 1: Medium, 2: Hard
            'ai_color': "Blue",    # Default AI color
            'player_color': "Red",  # Default player color
            'max_score': 7,
            'game_mode': 0,  # 0: Score-based, 1: Time-based
            'time_limit': 2  # Minutes (only used in time-based mode)
        }

        # Menu states
        self.current_state = MENU_STATE
        self.menu_items = ["Start Game", "Settings", "Quit"]
        self.settings_items = [
            "AI Difficulty", 
            "AI Color", 
            "Player Color", 
            "Max Score", 
            "Game Mode",
            "Time Limit",
            "Back"
        ]
        self.pause_items = ["Resume", "Restart", "Main Menu"]
        self.game_over_message = ""
        self.selected_item = 0
        self.menu_positions = []

        # Create sounds directory if it doesn't exist
        os.makedirs("sounds", exist_ok=True)
        
        # Create default sound files if they don't exist
        self.create_default_sound_files()
        
        # Load Sound Effects
        self.menu_select_sound = arcade.load_sound("sounds/vgmenuselect.wav")
        self.goal_sound = arcade.load_sound("sounds/goal_sound.wav")
        self.paddle_hit_sound = arcade.load_sound("sounds/paddle_hit.wav")
        self.wall_hit_sound = arcade.load_sound("sounds/wall_hit.wav")
        self.power_up_sound = arcade.load_sound("sounds/power_up.wav")

    def create_default_sound_files(self):
        """Create placeholder sound files if they don't exist"""
        # List of sound files that should exist
        sound_files = [
            "sounds/vgmenuselect.wav",
            "sounds/goal_sound.wav",
            "sounds/paddle_hit.wav",
            "sounds/wall_hit.wav",
            "sounds/power_up.wav"
        ]
        
        # Check if each file exists, if not create a placeholder
        for sound_file in sound_files:
            if not os.path.exists(sound_file):
                # Create an empty placeholder WAV file
                try:
                    import wave
                    import struct
                    
                    # Create a simple beep sound
                    sample_rate = 44100
                    duration = 0.2  # seconds
                    frequency = 440.0  # A4 note
                    
                    # Open WAV file for writing
                    with wave.open(sound_file, 'w') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 2 bytes per sample
                        wav_file.setframerate(sample_rate)
                        
                        # Generate sine wave
                        for i in range(int(duration * sample_rate)):
                            value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
                            data = struct.pack('<h', value)
                            wav_file.writeframes(data)
                except Exception as e:
                    print(f"Could not create sound file {sound_file}: {e}")
                    print("You may need to provide your own sound files in the 'sounds' directory.")

    def setup(self):
        # Player paddle
        self.player1_paddle = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 4,
            'dx': 0,
            'dy': 0,
            'radius': PADDLE_RADIUS  # Store radius to allow power-ups to change it
        }
        
        # AI paddle
        self.player2_paddle = {
            'x': SCREEN_WIDTH // 2,
            'y': 3 * SCREEN_HEIGHT // 4,
            'dx': 0,
            'dy': 0,
            'radius': PADDLE_RADIUS,
            'target_x': SCREEN_WIDTH // 2,
            'target_y': 3 * SCREEN_HEIGHT // 4
        }
        
        self.reset_puck()
        self.player1_score = 0
        self.player2_score = 0
        
        # Reset timer
        self.game_time = 0
        self.timer_active = True
        
        # Reset power-ups
        self.power_ups = []
        self.power_up_timer = 0
        self.player_power_up_active = False
        self.ai_power_up_active = False
        
        # Reset particles
        self.particles = []

        # Adjust AI based on difficulty setting
        global AI_SPEED, AI_AGGRESSION
        if self.settings['ai_difficulty'] == 0:  # Easy
            AI_SPEED = 5
            AI_AGGRESSION = 0.5
        elif self.settings['ai_difficulty'] == 1:  # Medium
            AI_SPEED = 8
            AI_AGGRESSION = 0.7
        else:  # Hard
            AI_SPEED = 10
            AI_AGGRESSION = 0.9

    def get_next_color(self, current_color):
        """Get the next color in the PADDLE_COLORS dictionary."""
        color_names = list(PADDLE_COLORS.keys())
        current_index = color_names.index(current_color)
        next_index = (current_index + 1) % len(color_names)
        return color_names[next_index]

    def draw_menu(self):
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

        # Draw menu items based on current state
        if self.current_state == MENU_STATE:
            menu_items = self.menu_items
        elif self.current_state == SETTINGS_STATE:
            menu_items = self.settings_items
        elif self.current_state == PAUSE_STATE:
            menu_items = self.pause_items
        elif self.current_state == GAME_OVER_STATE:
            # Draw game over message
            arcade.draw_text(
                self.game_over_message,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT * 0.5,
                arcade.color.WHITE,
                30,
                anchor_x="center",
                anchor_y="center"
            )
            menu_items = ["Play Again", "Main Menu"]

        for i, item in enumerate(menu_items):
            y_pos = SCREEN_HEIGHT * 0.4 - i * 50
            
            # Determine item color
            if self.selected_item == i:
                color = arcade.color.YELLOW
            else:
                color = arcade.color.WHITE

            # Add special handling for settings items
            display_item = item
            if self.current_state == SETTINGS_STATE:
                if item == "AI Difficulty":
                    difficulty_names = ["Easy", "Medium", "Hard"]
                    display_item += f": {difficulty_names[self.settings['ai_difficulty']]}"
                elif item == "AI Color":
                    selected_color = self.settings['ai_color']
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
                    selected_color = self.settings['player_color']
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
                    display_item += f": {self.settings['max_score']}"
                elif item == "Game Mode":
                    modes = ["Score", "Time"]
                    display_item += f": {modes[self.settings['game_mode']]}"
                elif item == "Time Limit":
                    display_item += f": {self.settings['time_limit']} min"

            # Draw text for non-color settings or if it hasn't been drawn yet
            if item not in ["AI Color", "Player Color"] or self.current_state != SETTINGS_STATE:
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
        for pos in self.menu_positions:
            if (pos['x'] <= x <= pos['x'] + pos['width'] and
                pos['y'] <= y <= pos['y'] + pos['height']):
                return pos['item']
        return None

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y
        
        if self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
            # Update selected item based on mouse position
            hovered_item = self.check_mouse_over_menu(x, y)
            if hovered_item is not None and hovered_item != self.selected_item:
                self.selected_item = hovered_item

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            clicked_item = self.check_mouse_over_menu(x, y)
            
            if clicked_item is not None:
                arcade.play_sound(self.menu_select_sound)
                
                if self.current_state == MENU_STATE:
                    if clicked_item == 0:  # Start Game
                        self.current_state = GAME_STATE
                        self.setup()
                    elif clicked_item == 1:  # Settings
                        self.current_state = SETTINGS_STATE
                        self.selected_item = 0
                    elif clicked_item == 2:  # Quit
                        arcade.close_window()
                
                elif self.current_state == SETTINGS_STATE:
                    if clicked_item == 0:  # AI Difficulty
                        self.settings['ai_difficulty'] = (
                            self.settings['ai_difficulty'] + 1
                        ) % 3
                    elif clicked_item == 1:  # AI Color
                        self.settings['ai_color'] = self.get_next_color(
                            self.settings['ai_color']
                        )
                    elif clicked_item == 2:  # Player Color
                        self.settings['player_color'] = self.get_next_color(
                            self.settings['player_color']
                        )
                    elif clicked_item == 3:  # Max Score
                        max_scores = [5, 7, 10, 15]
                        current_index = max_scores.index(
                            self.settings['max_score']
                        ) if self.settings['max_score'] in max_scores else 0
                        self.settings['max_score'] = max_scores[
                            (current_index + 1) % len(max_scores)
                        ]
                    elif clicked_item == 4:  # Game Mode
                        self.settings['game_mode'] = (self.settings['game_mode'] + 1) % 2
                    elif clicked_item == 5:  # Time Limit
                        time_limits = [1, 2, 3, 5]
                        current_index = time_limits.index(
                            self.settings['time_limit']
                        ) if self.settings['time_limit'] in time_limits else 0
                        self.settings['time_limit'] = time_limits[
                            (current_index + 1) % len(time_limits)
                        ]
                    elif clicked_item == 6:  # Back to main menu
                        self.current_state = MENU_STATE
                        self.selected_item = 0
                
                elif self.current_state == PAUSE_STATE:
                    if clicked_item == 0:  # Resume
                        self.current_state = GAME_STATE
                        self.timer_active = True
                    elif clicked_item == 1:  # Restart
                        self.current_state = GAME_STATE
                        self.setup()
                    elif clicked_item == 2:  # Main Menu
                        self.current_state = MENU_STATE
                        self.selected_item = 0
                
                elif self.current_state == GAME_OVER_STATE:
                    if clicked_item == 0:  # Play Again
                        self.current_state = GAME_STATE
                        self.setup()
                    elif clicked_item == 1:  # Main Menu
                        self.current_state = MENU_STATE
                        self.selected_item = 0

    def on_key_press(self, key, modifiers):
        if self.current_state == GAME_STATE:
            if key == arcade.key.ESCAPE:
                self.current_state = PAUSE_STATE
                self.timer_active = False
                self.selected_item = 0
        elif self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
            if key == arcade.key.UP:
                if self.selected_item is None:
                    self.selected_item = 0
                else:
                    if self.current_state == MENU_STATE:
                        self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                    elif self.current_state == SETTINGS_STATE:
                        self.selected_item = (self.selected_item - 1) % len(self.settings_items)
                    elif self.current_state == PAUSE_STATE:
                        self.selected_item = (self.selected_item - 1) % len(self.pause_items)
                    elif self.current_state == GAME_OVER_STATE:
                        self.selected_item = (self.selected_item - 1) % 2
                arcade.play_sound(self.menu_select_sound)
            elif key == arcade.key.DOWN:
                if self.selected_item is None:
                    self.selected_item = 0
                else:
                    if self.current_state == MENU_STATE:
                        self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                    elif self.current_state == SETTINGS_STATE:
                        self.selected_item = (self.selected_item + 1) % len(self.settings_items)
                    elif self.current_state == PAUSE_STATE:
                        self.selected_item = (self.selected_item + 1) % len(self.pause_items)
                    elif self.current_state == GAME_OVER_STATE:
                        self.selected_item = (self.selected_item + 1) % 2
                arcade.play_sound(self.menu_select_sound)
            elif key == arcade.key.ENTER:
                if self.selected_item is not None:
                    # Simulate clicking the selected item
                    self.on_mouse_press(
                        self.menu_positions[self.selected_item]['x'] + 10,
                        self.menu_positions[self.selected_item]['y'] + 10,
                        arcade.MOUSE_BUTTON_LEFT, 0
                    )

    def on_draw(self):
        self.clear()
        
        if self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
            self.draw_menu()
        elif self.current_state == GAME_STATE:
            # Draw game board
            self.draw_game_board()
            
            # Draw power-ups
            self.draw_power_ups()
            
            # Draw particles
            self.draw_particles()

    def draw_game_board(self):
        # Original game drawing code with updated paddle colors
        arcade.draw_lrbt_rectangle_outline(
            left=0, 
            right=SCREEN_WIDTH, 
            top=SCREEN_HEIGHT, 
            bottom=0, 
            color=arcade.color.WHITE, 
            border_width=4
        )
        
        # Draw center line
        arcade.draw_line(
            0,
            SCREEN_HEIGHT // 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            2
        )
        
        # Draw center circle
        arcade.draw_circle_outline(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            100,
            arcade.color.WHITE,
            2
        )
        
        # Draw goals with player colors
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
            right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
            top=GOAL_HEIGHT,
            bottom=0,
            color=PADDLE_COLORS[self.settings['player_color']],
            border_width=4
        )
        
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
            right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
            top=SCREEN_HEIGHT,
            bottom=SCREEN_HEIGHT - GOAL_HEIGHT,
            color=PADDLE_COLORS[self.settings['ai_color']],
            border_width=4
        )
        
        # Draw paddles with selected colors and possible power-up effects
        player_color = PADDLE_COLORS[self.settings['player_color']]
        ai_color = PADDLE_COLORS[self.settings['ai_color']]
        
        # Add glow effect if power-up is active
        if self.player_power_up_active:
            # Draw glow
            for i in range(3):
                size_multiplier = 1.1 + (i * 0.1)
                alpha = 100 - (i * 30)
                glow_color = (player_color[0], player_color[1], player_color[2], alpha)
                arcade.draw_circle_filled(
                    self.player1_paddle['x'],
                    self.player1_paddle['y'],
                    self.player1_paddle['radius'] * size_multiplier,
                    glow_color
                )
        
        if self.ai_power_up_active:
            # Draw glow
            for i in range(3):
                size_multiplier = 1.1 + (i * 0.1)
                alpha = 100 - (i * 30)
                glow_color = (ai_color[0], ai_color[1], ai_color[2], alpha)
                arcade.draw_circle_filled(
                    self.player2_paddle['x'],
                    self.player2_paddle['y'],
                    self.player2_paddle['radius'] * size_multiplier,
                    glow_color
                )
        
        # Draw actual paddles
        arcade.draw_circle_filled(
            self.player1_paddle['x'],
            self.player1_paddle['y'],
            self.player1_paddle['radius'],
            player_color
        )
        
        arcade.draw_circle_filled(
            self.player2_paddle['x'],
            self.player2_paddle['y'],
            self.player2_paddle['radius'],
            ai_color
        )
        
        # Draw puck
        arcade.draw_circle_filled(
            self.puck['x'],
            self.puck['y'],
            PUCK_RADIUS,
            arcade.color.GRAY
        )
        
        # Draw puck trail (visual effect)
        for i, trail in enumerate(self.puck.get('trail', [])):
            # Fade out as the trail gets older
            alpha = 150 - (i * 20)
            if alpha > 0:
                trail_color = (200, 200, 200, alpha)
                arcade.draw_circle_filled(
                    trail['x'],
                    trail['y'],
                    PUCK_RADIUS * (1 - (i * 0.15)),
                    trail_color
                )
        
        # Draw scores
        arcade.draw_text(
            f"Player: {self.player1_score}",
            10,
            10,
            PADDLE_COLORS[self.settings['player_color']],
            20
        )
        
        arcade.draw_text(
            f"AI: {self.player2_score}",
            10,
            SCREEN_HEIGHT - 30,
            PADDLE_COLORS[self.settings['ai_color']],
            20
        )
        
        # Draw timer if in time-based mode
        if self.settings['game_mode'] == 1:  # Time-based mode
            minutes = int(self.settings['time_limit'] * 60 - self.game_time) // 60
            seconds = int(self.settings['time_limit'] * 60 - self.game_time) % 60
            arcade.draw_text(
                f"Time: {minutes}:{seconds:02d}",
                SCREEN_WIDTH - 120,
                SCREEN_HEIGHT - 30,
                arcade.color.WHITE,
                20
            )

    def draw_power_ups(self):
        # Draw each power-up on the board
        for power_up in self.power_ups:
            # Draw the power-up icon
            if power_up['type'] == 'speed':
                color = arcade.color.YELLOW
                arcade.draw_circle_filled(
                    power_up['x'],
                    power_up['y'],
                    15,
                    color
                )
                # Draw lightning bolt icon
                arcade.draw_text(
                    "⚡",
                    power_up['x'],
                    power_up['y'],
                    arcade.color.BLACK,
                    20,
                    anchor_x="center",
                    anchor_y="center"
                )
            elif power_up['type'] == 'size':
                color = arcade.color.GREEN
                arcade.draw_circle_filled(
                    power_up['x'],
                    power_up['y'],
                    15,
                    color
                )
                # Draw plus icon
                arcade.draw_text(
                    "+",
                    power_up['x'],
                    power_up['y'],
                    arcade.color.BLACK,
                    20,
                    anchor_x="center",
                    anchor_y="center"
                )
            elif power_up['type'] == 'freeze':
                color = arcade.color.CYAN
                arcade.draw_circle_filled(
                    power_up['x'],
                    power_up['y'],
                    15,
                    color
                )
                # Draw snowflake icon
                arcade.draw_text(
                    "❄",
                    power_up['x'],
                    power_up['y'],
                    arcade.color.BLACK,
                    20,
                    anchor_x="center",
                    anchor_y="center"
                )

    def draw_particles(self):
        for particle in self.particles:
            arcade.draw_circle_filled(
                particle['x'],
                particle['y'],
                particle['radius'],
                particle['color']
            )

    def on_update(self, delta_time):
        if self.current_state == GAME_STATE:
            # Update game timer
            if self.timer_active:
                self.game_time += delta_time
                
                # Check for time-based game end
                if self.settings['game_mode'] == 1 and self.game_time >= self.settings['time_limit'] * 60:
                    # Time's up, determine winner
                    if self.player1_score > self.player2_score:
                        self.game_over_message = "You Win!"
                    elif self.player2_score > self.player1_score:
                        self.game_over_message = "AI Wins!"
                    else:
                        self.game_over_message = "It's a Tie!"
                    
                    self.current_state = GAME_OVER_STATE
                    self.selected_item = 0
                    return
            
            # Update player paddles
            self.update_player_paddle()
            self.update_ai()
            
            # Update puck trail
            if not hasattr(self.puck, 'trail'):
                self.puck['trail'] = []
                
            if len(self.puck.get('trail', [])) > 0 and random.random() < 0.3:
                self.puck['trail'].insert(0, {'x': self.puck['x'], 'y': self.puck['y']})
                if len(self.puck['trail']) > 5:
                    self.puck['trail'].pop()
            
            # Move puck
            self.puck['x'] += self.puck['dx']
            self.puck['y'] += self.puck['dy']
            
            # Apply friction to puck
            self.puck['dx'] *= FRICTION
            self.puck['dy'] *= FRICTION

            # Handle collisions
            self.handle_puck_boundary_collision()
            self.check_goals()
            self.handle_paddle_puck_collision(self.player1_paddle, self.player2_paddle)
            
            # Update particles
            self.update_particles(delta_time)
            
            # Handle power-ups
            self.update_power_ups(delta_time)
            self.check_power_up_collisions()

    def update_ai(self):
        # If AI is frozen by power-up, don't move
        if self.ai_power_up_active and self.puck.get('freeze_opponent', False):
            return
            
        # Default defensive position
        target_x = SCREEN_WIDTH // 2
        target_y = SCREEN_HEIGHT * AI_DEFENSE_POSITION

        # Apply size power-up effect
        paddle_radius = self.player2_paddle['radius']

        # Predict where puck will intersect AI's y-position
        if self.puck['dy'] > 0:  # Puck moving upward
            time_to_intersect = (target_y - self.puck['y']) / self.puck['dy'] if self.puck['dy'] != 0 else 0
            predicted_x = self.puck['x'] + self.puck['dx'] * time_to_intersect

            # Keep prediction within bounds
            predicted_x = max(paddle_radius, 
                            min(SCREEN_WIDTH - paddle_radius, predicted_x))

            # Move towards predicted position
            if abs(self.puck['dy']) > 1:  # Only if puck moving with significant speed
                target_x = predicted_x

        # If puck is in AI's half, move to intercept
        if self.puck['y'] > SCREEN_HEIGHT // 2:
            dx = self.puck['x'] - self.player2_paddle['x']
            dy = self.puck['y'] - self.player2_paddle['y']
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                target_x = self.puck['x']
                target_y = self.puck['y'] - paddle_radius
                
                # Adjust aggression based on puck position
                if self.puck['y'] > SCREEN_HEIGHT * 0.75:
                    # More aggressive when puck is close to AI's goal
                    target_x = self.puck['x'] + self.puck['dx'] * AI_AGGRESSION
                    target_y = self.puck['y'] + self.puck['dy'] * AI_AGGRESSION
# Move AI paddle towards target
        dx = target_x - self.player2_paddle['x']
        dy = target_y - self.player2_paddle['y']
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Apply speed boost if power-up is active
            speed_multiplier = 1.5 if (self.ai_power_up_active and self.puck.get('speed_boost', False)) else 1.0
            
            self.player2_paddle['dx'] = (dx / distance) * AI_SPEED * speed_multiplier
            self.player2_paddle['dy'] = (dy / distance) * AI_SPEED * speed_multiplier
            
            # Update position
            new_x = self.player2_paddle['x'] + self.player2_paddle['dx']
            new_y = self.player2_paddle['y'] + self.player2_paddle['dy']
            
            # Constrain to top half of screen
            self.player2_paddle['x'] = max(paddle_radius, 
                min(SCREEN_WIDTH - paddle_radius, new_x))
            self.player2_paddle['y'] = max(SCREEN_HEIGHT // 2 + paddle_radius, 
                min(SCREEN_HEIGHT - paddle_radius, new_y))

    def update_player_paddle(self):
        # Calculate movement deltas
        dx = self.mouse_x - self.player1_paddle['x']
        dy = self.mouse_y - self.player1_paddle['y']
        
        # Update paddle position
        self.player1_paddle['x'] = self.mouse_x
        self.player1_paddle['y'] = self.mouse_y
        
        # Update velocity for collision physics
        self.player1_paddle['dx'] = dx
        self.player1_paddle['dy'] = dy
        
        # Constrain paddle to bottom half of screen and within boundaries
        paddle_radius = self.player1_paddle['radius']
        self.player1_paddle['x'] = max(paddle_radius, 
            min(SCREEN_WIDTH - paddle_radius, self.player1_paddle['x']))
        self.player1_paddle['y'] = max(paddle_radius, 
            min(SCREEN_HEIGHT // 2 - paddle_radius, self.player1_paddle['y']))

    def reset_puck(self):
        # Reset puck to center with random initial velocity
        self.puck = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3),
            'trail': []  # Initialize empty trail
        }

    def handle_puck_boundary_collision(self):
        # Check and handle horizontal wall collisions
        collision_happened = False
        
        if self.puck['x'] - PUCK_RADIUS <= 0:
            self.puck['x'] = PUCK_RADIUS
            self.puck['dx'] *= -WALL_BOUNCE_DAMPING
            collision_happened = True
        elif self.puck['x'] + PUCK_RADIUS >= SCREEN_WIDTH:
            self.puck['x'] = SCREEN_WIDTH - PUCK_RADIUS
            self.puck['dx'] *= -WALL_BOUNCE_DAMPING
            collision_happened = True

        # Check and handle vertical wall collisions
        # Don't bounce if within goal area
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2

        if self.puck['y'] - PUCK_RADIUS <= 0:
            if not (GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
                self.puck['y'] = PUCK_RADIUS
                self.puck['dy'] *= -WALL_BOUNCE_DAMPING
                collision_happened = True
        elif self.puck['y'] + PUCK_RADIUS >= SCREEN_HEIGHT:
            if not (GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
                self.puck['y'] = SCREEN_HEIGHT - PUCK_RADIUS
                self.puck['dy'] *= -WALL_BOUNCE_DAMPING
                collision_happened = True

        # Play wall hit sound and create particles if collision happened
        if collision_happened:
            arcade.play_sound(self.wall_hit_sound)
            # Create particles at collision point
            self.spawn_particles(self.puck['x'], self.puck['y'], arcade.color.WHITE, 5)

        # Add minimum speed threshold to prevent extremely slow movement
        total_speed = math.sqrt(self.puck['dx']**2 + self.puck['dy']**2)
        if total_speed < 0.1:
            self.puck['dx'] = 0
            self.puck['dy'] = 0

    def check_goals(self):
        # Modify goal checking to use max_score setting
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2
        
        # Check if puck is completely past the goal line
        if (self.puck['y'] + PUCK_RADIUS <= 0 and 
            GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
            # Player 2 scores
            self.player2_score += 1
            self.reset_puck()
            arcade.play_sound(self.goal_sound)
            
            # Create goal celebration particles
            self.spawn_particles(
                SCREEN_WIDTH // 2, 
                GOAL_HEIGHT // 2, 
                PADDLE_COLORS[self.settings['ai_color']], 
                30
            )
            
            # Check for game end (if in score-based mode)
            if self.settings['game_mode'] == 0 and self.player2_score >= self.settings['max_score']:
                self.game_over_message = "AI Wins!"
                self.current_state = GAME_OVER_STATE
                self.selected_item = 0
        
        elif (self.puck['y'] - PUCK_RADIUS >= SCREEN_HEIGHT and 
              GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
            # Player 1 scores
            self.player1_score += 1
            self.reset_puck()
            arcade.play_sound(self.goal_sound)
            
            # Create goal celebration particles
            self.spawn_particles(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT - GOAL_HEIGHT // 2, 
                PADDLE_COLORS[self.settings['player_color']], 
                30
            )
            
            # Check for game end (if in score-based mode)
            if self.settings['game_mode'] == 0 and self.player1_score >= self.settings['max_score']:
                self.game_over_message = "You Win!"
                self.current_state = GAME_OVER_STATE
                self.selected_item = 0

    def handle_paddle_puck_collision(self, *paddles):
        for paddle in paddles:
            dx = self.puck['x'] - paddle['x']
            dy = self.puck['y'] - paddle['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            # Use the paddle's actual radius for collision
            paddle_radius = paddle['radius']
            
            if distance <= paddle_radius + PUCK_RADIUS:
                # Calculate collision angle and normalize the direction
                angle = math.atan2(dy, dx)
                
                # Move puck outside of paddle to prevent sticking
                overlap = paddle_radius + PUCK_RADIUS - distance
                self.puck['x'] += math.cos(angle) * overlap
                self.puck['y'] += math.sin(angle) * overlap
                
                # Calculate new velocity
                speed = math.sqrt(self.puck['dx']**2 + self.puck['dy']**2)
                speed = max(speed, 5)  # Minimum speed after collision
                
                # Combine paddle and puck momentum
                momentum_factor = 0.5
                
                # Apply power-up effects to collision
                if paddle == self.player1_paddle and self.player_power_up_active:
                    if self.puck.get('speed_boost', False):
                        speed *= 1.5  # Boost speed for player
                        momentum_factor = 0.8  # More paddle momentum transfer
                
                if paddle == self.player2_paddle and self.ai_power_up_active:
                    if self.puck.get('speed_boost', False):
                        speed *= 1.5  # Boost speed for AI
                        momentum_factor = 0.8  # More paddle momentum transfer
                
                self.puck['dx'] = (math.cos(angle) * speed * 1.2 + 
                                 paddle['dx'] * momentum_factor)
                self.puck['dy'] = (math.sin(angle) * speed * 1.2 + 
                                 paddle['dy'] * momentum_factor)
                
                # Play sound and create particles for collision
                arcade.play_sound(self.paddle_hit_sound)
                
                # Determine color based on which paddle
                if paddle == self.player1_paddle:
                    color = PADDLE_COLORS[self.settings['player_color']]
                else:
                    color = PADDLE_COLORS[self.settings['ai_color']]
                
                # Spawn particles at collision point
                collision_x = self.puck['x'] - math.cos(angle) * PUCK_RADIUS
                collision_y = self.puck['y'] - math.sin(angle) * PUCK_RADIUS
                self.spawn_particles(collision_x, collision_y, color, 10)

    def update_particles(self, delta_time):
        # Update each particle
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            
            # Move particle
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Reduce lifetime
            particle['lifetime'] -= delta_time
            
            # Remove particle if lifetime is up
            if particle['lifetime'] <= 0:
                self.particles.pop(i)
            else:
                # Shrink particle as it ages
                particle['radius'] = particle['original_radius'] * (particle['lifetime'] / particle['max_lifetime'])

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            lifetime = random.uniform(0.2, 0.5)
            radius = random.uniform(2, 5)
            
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'radius': radius,
                'original_radius': radius,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color
            })

    # Power-up related methods
    def spawn_power_up(self):
        """Spawn a random power-up on the field"""
        power_up_types = ['speed', 'size', 'freeze']
        power_up_type = random.choice(power_up_types)
        
        # Place in center area
        x = random.randint(SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4)
        y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        
        self.power_ups.append({
            'x': x,
            'y': y,
            'type': power_up_type,
            'radius': 15,
            'lifetime': 10  # Power-up disappears after 10 seconds if not collected
        })

    def update_power_ups(self, delta_time):
        """Update power-ups and active power-up effects"""
        # Spawn new power-ups periodically
        self.power_up_timer += delta_time
        if self.power_up_timer > 15 and len(self.power_ups) < 2:  # Max 2 power-ups at once
            self.spawn_power_up()
            self.power_up_timer = 0
        
        # Update power-up lifetimes
        for i in range(len(self.power_ups) - 1, -1, -1):
            self.power_ups[i]['lifetime'] -= delta_time
            if self.power_ups[i]['lifetime'] <= 0:
                self.power_ups.pop(i)
        
        # Update active power-up timers
        if self.player_power_up_active:
            self.player_power_up_time -= delta_time
            if self.player_power_up_time <= 0:
                self.player_power_up_active = False
                # Reset any power-up effects
                self.player1_paddle['radius'] = PADDLE_RADIUS
                if 'speed_boost' in self.puck:
                    self.puck['speed_boost'] = False
                if 'freeze_opponent' in self.puck:
                    self.puck['freeze_opponent'] = False
        
        if self.ai_power_up_active:
            self.ai_power_up_time -= delta_time
            if self.ai_power_up_time <= 0:
                self.ai_power_up_active = False
                # Reset any power-up effects
                self.player2_paddle['radius'] = PADDLE_RADIUS
                if 'speed_boost' in self.puck:
                    self.puck['speed_boost'] = False
                if 'freeze_opponent' in self.puck:
                    self.puck['freeze_opponent'] = False

    def check_power_up_collisions(self):
        """Check if paddles collect power-ups"""
        # Check player paddle
        for i in range(len(self.power_ups) - 1, -1, -1):
            power_up = self.power_ups[i]
            
            # Check player paddle collision
            dx = power_up['x'] - self.player1_paddle['x']
            dy = power_up['y'] - self.player1_paddle['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.player1_paddle['radius'] + power_up['radius']:
                # Player collected power-up
                self.apply_power_up(power_up, is_player=True)
                self.power_ups.pop(i)
                arcade.play_sound(self.power_up_sound)
                continue
            
            # Check AI paddle collision
            dx = power_up['x'] - self.player2_paddle['x']
            dy = power_up['y'] - self.player2_paddle['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.player2_paddle['radius'] + power_up['radius']:
                # AI collected power-up
                self.apply_power_up(power_up, is_player=False)
                self.power_ups.pop(i)
                arcade.play_sound(self.power_up_sound)

    def apply_power_up(self, power_up, is_player):
        """Apply power-up effects"""
        power_up_duration = 10  # seconds
        
        if is_player:
            self.player_power_up_active = True
            self.player_power_up_time = power_up_duration
            
            if power_up['type'] == 'speed':
                # Speed boost affects puck when hit by this player
                self.puck['speed_boost'] = True
            elif power_up['type'] == 'size':
                # Increase paddle size
                self.player1_paddle['radius'] = PADDLE_RADIUS * 1.5
            elif power_up['type'] == 'freeze':
                # Freeze opponent briefly
                self.puck['freeze_opponent'] = True
        else:
            # AI power-up
            self.ai_power_up_active = True
            self.ai_power_up_time = power_up_duration
            
            if power_up['type'] == 'speed':
                # Speed boost affects puck when hit by AI
                self.puck['speed_boost'] = True
            elif power_up['type'] == 'size':
                # Increase paddle size
                self.player2_paddle['radius'] = PADDLE_RADIUS * 1.5
            elif power_up['type'] == 'freeze':
                # Freeze opponent briefly
                self.puck['freeze_opponent'] = True


def main():
    window = AirHockeyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()