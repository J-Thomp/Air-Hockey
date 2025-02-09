import arcade
import math
import random

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

# Available paddle colors
PADDLE_COLORS = {
    "Red": arcade.color.RED,
    "Blue": arcade.color.BLUE,
    "Green": arcade.color.GREEN,
    "Yellow": arcade.color.YELLOW,
    "Purple": arcade.color.PURPLE,
    "Orange": arcade.color.ORANGE
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

        # Game settings
        self.settings = {
            'ai_difficulty': 1,  # 0: Easy, 1: Medium, 2: Hard
            'ai_color': "Blue",    # Default AI color
            'player_color': "Red",  # Default player color
            'max_score': 7
        }

        # Menu states
        self.current_state = MENU_STATE
        self.menu_items = ["Start Game", "Settings", "Quit"]
        self.settings_items = [
            "AI Difficulty", 
            "AI Color", 
            "Player Color", 
            "Max Score", 
            "Back"
        ]
        self.selected_item = None
        self.menu_positions = []

        # Load Sound Effects
        self.menu_select_sound = arcade.load_sound("sounds/vgmenuselect.wav")

    def setup(self):
        # Player paddle
        self.player1_paddle = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 4,
            'dx': 0,
            'dy': 0,
        }
        
        # AI paddle
        self.player2_paddle = {
            'x': SCREEN_WIDTH // 2,
            'y': 3 * SCREEN_HEIGHT // 4,
            'dx': 0,
            'dy': 0,
            'target_x': SCREEN_WIDTH // 2,
            'target_y': 3 * SCREEN_HEIGHT // 4
        }
        
        self.reset_puck()
        self.player1_score = 0
        self.player2_score = 0

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

            # Draw text for non-color settings or if it hasn't been drawn yet
            if item not in ["AI Color", "Player Color"]:
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
        
        if self.current_state in [MENU_STATE, SETTINGS_STATE]:
            # Update selected item based on mouse position
            self.selected_item = self.check_mouse_over_menu(x, y)

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
                        self.selected_item = None
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
                        )
                        self.settings['max_score'] = max_scores[
                            (current_index + 1) % len(max_scores)
                        ]
                    
                    elif clicked_item == 4:  # Back to main menu
                        self.current_state = MENU_STATE
                        self.selected_item = None

    def on_key_press(self, key, modifiers):
        if self.current_state == GAME_STATE and key == arcade.key.ESCAPE:
            self.current_state = MENU_STATE

    def on_draw(self):
        self.clear()
        
        if self.current_state in [MENU_STATE, SETTINGS_STATE]:
            self.draw_menu()
        else:
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
            
            # Draw paddles with selected colors
            arcade.draw_circle_filled(
                self.player1_paddle['x'],
                self.player1_paddle['y'],
                PADDLE_RADIUS,
                PADDLE_COLORS[self.settings['player_color']]
            )
            
            arcade.draw_circle_filled(
                self.player2_paddle['x'],
                self.player2_paddle['y'],
                PADDLE_RADIUS,
                PADDLE_COLORS[self.settings['ai_color']]
            )
            
            # Draw puck
            arcade.draw_circle_filled(
                self.puck['x'],
                self.puck['y'],
                PUCK_RADIUS,
                arcade.color.GRAY
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

    def update_ai(self):
        # Default defensive position
        target_x = SCREEN_WIDTH // 2
        target_y = SCREEN_HEIGHT * AI_DEFENSE_POSITION

        # Predict where puck will intersect AI's y-position
        if self.puck['dy'] > 0:  # Puck moving upward
            time_to_intersect = (target_y - self.puck['y']) / self.puck['dy']
            predicted_x = self.puck['x'] + self.puck['dx'] * time_to_intersect

            # Keep prediction within bounds
            predicted_x = max(PADDLE_RADIUS, 
                            min(SCREEN_WIDTH - PADDLE_RADIUS, predicted_x))

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
                target_y = self.puck['y'] - PADDLE_RADIUS
                
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
            self.player2_paddle['dx'] = (dx / distance) * AI_SPEED
            self.player2_paddle['dy'] = (dy / distance) * AI_SPEED
            
            # Update position
            new_x = self.player2_paddle['x'] + self.player2_paddle['dx']
            new_y = self.player2_paddle['y'] + self.player2_paddle['dy']
            
            # Constrain to top half of screen
            self.player2_paddle['x'] = max(PADDLE_RADIUS, 
                min(SCREEN_WIDTH - PADDLE_RADIUS, new_x))
            self.player2_paddle['y'] = max(SCREEN_HEIGHT // 2 + PADDLE_RADIUS, 
                min(SCREEN_HEIGHT - PADDLE_RADIUS, new_y))

    def update_paddle_position(self, paddle, holding):
        if holding:
            # Calculate distance to target
            dx = paddle['target_x'] - paddle['x']
            dy = paddle['target_y'] - paddle['y']
            
            # Direct movement to target position
            paddle['x'] = paddle['target_x']
            paddle['y'] = paddle['target_y']
            
            # Update velocity for collision physics
            paddle['dx'] = dx
            paddle['dy'] = dy
        else:
            # When not held, gradually slow down
            paddle['dx'] *= 0.8
            paddle['dy'] *= 0.8

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
        self.player1_paddle['x'] = max(PADDLE_RADIUS, 
            min(SCREEN_WIDTH - PADDLE_RADIUS, self.player1_paddle['x']))
        self.player1_paddle['y'] = max(PADDLE_RADIUS, 
            min(SCREEN_HEIGHT // 2 - PADDLE_RADIUS, self.player1_paddle['y']))

    def on_update(self, delta_time):
        if self.current_state == GAME_STATE:
            # Existing game update logic
            self.update_player_paddle()
            self.update_ai()
            
            # Move puck
            self.puck['x'] += self.puck['dx']
            self.puck['y'] += self.puck['dy']
            
            # Apply friction to puck
            self.puck['dx'] *= FRICTION
            self.puck['dy'] *= FRICTION

            # Handle collisions
            self.handle_puck_boundary_collision()
            self.check_goals()
            self.handle_paddle_puck_collision(
                self.player1_paddle, self.player2_paddle
            )

    def on_key_press(self, key, modifiers):
        if self.current_state == MENU_STATE:
            if key == arcade.key.UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                arcade.play_sound(self.menu_select_sound)
            elif key == arcade.key.DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                arcade.play_sound(self.menu_select_sound)
            elif key == arcade.key.ENTER:
                if self.selected_item == 0:  # Start Game
                    self.current_state = GAME_STATE
                    self.setup()
                    arcade.play_sound(self.menu_select_sound)
                elif self.selected_item == 1:  # Quit
                    arcade.close_window()
        elif self.current_state == GAME_STATE:
            if key == arcade.key.ESCAPE:
                self.current_state = MENU_STATE
                self.selected_item = 0

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
            arcade.play_sound(self.menu_select_sound)
            
            # Check for game end
            if self.player2_score >= self.settings['max_score']:
                self.current_state = MENU_STATE
        
        elif (self.puck['y'] - PUCK_RADIUS >= SCREEN_HEIGHT and 
              GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
            # Player 1 scores
            self.player1_score += 1
            self.reset_puck()
            arcade.play_sound(self.menu_select_sound)
            
            # Check for game end
            if self.player1_score >= self.settings['max_score']:
                self.current_state = MENU_STATE

    def reset_puck(self):
        # Reset puck to center with random initial velocity
        self.puck = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3)
        }

    # Mouse control methods remain the same
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def handle_puck_boundary_collision(self):
        # Check and handle horizontal wall collisions
        if self.puck['x'] - PUCK_RADIUS <= 0:
            self.puck['x'] = PUCK_RADIUS
            self.puck['dx'] *= -WALL_BOUNCE_DAMPING
        elif self.puck['x'] + PUCK_RADIUS >= SCREEN_WIDTH:
            self.puck['x'] = SCREEN_WIDTH - PUCK_RADIUS
            self.puck['dx'] *= -WALL_BOUNCE_DAMPING

        # Check and handle vertical wall collisions
        # Don't bounce if within goal area
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2

        if self.puck['y'] - PUCK_RADIUS <= 0:
            if not (GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
                self.puck['y'] = PUCK_RADIUS
                self.puck['dy'] *= -WALL_BOUNCE_DAMPING
        elif self.puck['y'] + PUCK_RADIUS >= SCREEN_HEIGHT:
            if not (GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
                self.puck['y'] = SCREEN_HEIGHT - PUCK_RADIUS
                self.puck['dy'] *= -WALL_BOUNCE_DAMPING

        # Add minimum speed threshold to prevent extremely slow movement
        total_speed = math.sqrt(self.puck['dx']**2 + self.puck['dy']**2)
        if total_speed < 0.1:
            self.puck['dx'] = 0
            self.puck['dy'] = 0

    def handle_paddle_puck_collision(self, *paddles):
        for paddle in paddles:
            dx = self.puck['x'] - paddle['x']
            dy = self.puck['y'] - paddle['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= PADDLE_RADIUS + PUCK_RADIUS:
                # Calculate collision angle and normalize the direction
                angle = math.atan2(dy, dx)
                
                # Move puck outside of paddle to prevent sticking
                overlap = PADDLE_RADIUS + PUCK_RADIUS - distance
                self.puck['x'] += math.cos(angle) * overlap
                self.puck['y'] += math.sin(angle) * overlap
                
                # Calculate new velocity
                speed = math.sqrt(self.puck['dx']**2 + self.puck['dy']**2)
                speed = max(speed, 5)  # Minimum speed after collision
                
                # Combine paddle and puck momentum
                self.puck['dx'] = (math.cos(angle) * speed * 1.2 + 
                                 paddle['dx'] * 0.5)
                self.puck['dy'] = (math.sin(angle) * speed * 1.2 + 
                                 paddle['dy'] * 0.5)

def main():
    window = AirHockeyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()