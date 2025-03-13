import os
import math
import random
import arcade

# Import game modules
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, GOAL_WIDTH, GOAL_HEIGHT,
    MENU_STATE, GAME_STATE, SETTINGS_STATE, GAME_OVER_STATE, PAUSE_STATE,
    PADDLE_COLORS, PADDLE_RADIUS
)
import utils
from game_objects import Puck, Paddle, PowerUp
from game_states import MenuManager

class AirHockeyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        
        # Set update rate for performance (60 FPS cap)
        self.set_update_rate(1/60)

        # Game objects
        self.player1_paddle = None
        self.player2_paddle = None
        self.puck = None
        self.power_ups = []
        
        # Game state
        self.current_state = MENU_STATE
        self.menu_manager = MenuManager()
        self.player1_score = 0
        self.player2_score = 0
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Game timer
        self.game_time = 0
        self.timer_active = False
        
        # Particle effects
        self.particles = []
        self.max_particles = 30  # Limit maximum particles for performance
        
        # Power-up system
        self.power_up_timer = 0
        
        # Stuck detection
        self.stuck_timer = 0
        self.last_puck_pos = (0, 0)
        
        # Game settings
        self.settings = {
            'ai_difficulty': 1,  # 0: Easy, 1: Medium, 2: Hard
            'ai_color': "Blue",    # Default AI color
            'player_color': "Red",  # Default player color
            'max_score': 7,
            'game_mode': 0,  # 0: Score-based, 1: Time-based
            'time_limit': 2,  # Minutes (only used in time-based mode)
            'power_ups_enabled': True,  # Enable/disable power-ups
            'power_up_frequency': 1  # 0: Low, 1: Medium, 2: High
        }
        
        # Game over message
        self.game_over_message = ""
        
        # Debug mode for visualizing boundaries
        self.debug_mode = False

        # Create and load sound effects
        utils.create_default_sound_files()
        self.load_sounds()

    def load_sounds(self):
        """Load all game sound effects"""
        self.menu_select_sound = arcade.load_sound("sounds/vgmenuselect.wav")
        self.goal_sound = arcade.load_sound("sounds/goal_sound.wav")
        self.paddle_hit_sound = arcade.load_sound("sounds/paddle_hit.wav")
        self.wall_hit_sound = arcade.load_sound("sounds/wall_hit.wav")
        self.power_up_sound = arcade.load_sound("sounds/power_up.wav")

    def setup(self):
        """Set up the game and initialize the variables"""
        # Create game objects
        self.player1_paddle = Paddle(is_ai=False)
        self.player2_paddle = Paddle(is_ai=True)
        self.puck = Puck()
        
        # Connect paddles to each other for freeze power-up
        self.player1_paddle.opponent_paddle = self.player2_paddle
        self.player2_paddle.opponent_paddle = self.player1_paddle
        self.puck.opponent_paddle = self.player2_paddle  # For freeze power-up
        
        # Reset scores
        self.player1_score = 0
        self.player2_score = 0
        
        # Reset timer
        self.game_time = 0
        self.timer_active = True
        
        # Reset power-ups
        self.power_ups = []
        self.power_up_timer = 0
        
        # Reset particles
        self.particles = []
        
        # Reset stuck detection
        self.stuck_timer = 0
        self.last_puck_pos = (self.puck.x, self.puck.y)

    def on_draw(self):
        """Render the screen"""
        self.clear()
        
        if self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
            self.menu_manager.draw_menu(
                self.current_state,
                self.settings,
                self.game_over_message
            )
        elif self.current_state == GAME_STATE:
            # Draw game board with rounded corners
            utils.draw_rounded_hockey_rink()
            
            # Draw goals
            # Player goal (bottom)
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
                right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
                bottom=0,
                top=GOAL_HEIGHT,
                color=PADDLE_COLORS[self.settings['player_color']]
            )
            # Add outline in the same color
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
                right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
                bottom=0,
                top=GOAL_HEIGHT,
                color=PADDLE_COLORS[self.settings['player_color']],
                border_width=2
            )
            
            # AI goal (top)
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
                right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
                bottom=SCREEN_HEIGHT - GOAL_HEIGHT,
                top=SCREEN_HEIGHT,
                color=PADDLE_COLORS[self.settings['ai_color']]
            )
            # Add outline in the same color
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
                right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
                bottom=SCREEN_HEIGHT - GOAL_HEIGHT,
                top=SCREEN_HEIGHT,
                color=PADDLE_COLORS[self.settings['ai_color']],
                border_width=2
            )
            
            # Draw paddles
            self.player1_paddle.draw(
                PADDLE_COLORS[self.settings['player_color']],
                self.player1_paddle.power_up_active
            )
            
            self.player2_paddle.draw(
                PADDLE_COLORS[self.settings['ai_color']],
                self.player2_paddle.power_up_active
            )
            
            # Draw puck
            self.puck.draw()
            
            # Draw power-ups
            for power_up in self.power_ups:
                power_up.draw()
            
            # Draw particles
            for particle in self.particles:
                arcade.draw_circle_filled(
                    particle['x'],
                    particle['y'],
                    particle['radius'],
                    particle['color']
                )
            
            # Draw scores - simple version for better performance
            # Player score
            arcade.draw_text(
                f"PLAYER: {self.player1_score}",
                20,
                20,
                PADDLE_COLORS[self.settings['player_color']],
                20,
                bold=True
            )
            
            # AI score
            arcade.draw_text(
                f"AI: {self.player2_score}",
                20,
                SCREEN_HEIGHT - 40,
                PADDLE_COLORS[self.settings['ai_color']],
                20,
                bold=True
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
            
            # Debug visualization of boundaries
            if self.debug_mode:
                self.draw_debug_boundaries()

    def draw_debug_boundaries(self):
        """Draw debug visualization for boundary detection"""
        # Get corner positions
        corner_positions = utils.get_rink_corner_positions()
        
        # Draw corner detection regions
        for corner_x, corner_y in corner_positions:
            # Draw corner valid area
            arcade.draw_circle_outline(
                corner_x, corner_y, 
                utils.CORNER_RADIUS - self.puck.radius, 
                arcade.color.RED, 1
            )
            
            # Draw corner region bounds
            if corner_x < SCREEN_WIDTH // 2:  # Left side
                arcade.draw_line(
                    utils.CORNER_RADIUS, corner_y,
                    0, corner_y,
                    arcade.color.YELLOW, 1
                )
            else:  # Right side
                arcade.draw_line(
                    SCREEN_WIDTH - utils.CORNER_RADIUS, corner_y,
                    SCREEN_WIDTH, corner_y,
                    arcade.color.YELLOW, 1
                )
                
            if corner_y < SCREEN_HEIGHT // 2:  # Bottom side
                arcade.draw_line(
                    corner_x, utils.CORNER_RADIUS,
                    corner_x, 0,
                    arcade.color.YELLOW, 1
                )
            else:  # Top side
                arcade.draw_line(
                    corner_x, SCREEN_HEIGHT - utils.CORNER_RADIUS,
                    corner_x, SCREEN_HEIGHT,
                    arcade.color.YELLOW, 1
                )
                
        # Draw paddle valid boundary for player
        y_boundary = SCREEN_HEIGHT // 2 - self.player1_paddle.radius
        arcade.draw_line(
            0, y_boundary,
            SCREEN_WIDTH, y_boundary,
            arcade.color.GREEN, 1
        )

    def on_update(self, delta_time):
        """Movement and game logic"""
        if self.current_state == GAME_STATE:
            # Performance optimization: Limit particles
            if len(self.particles) > self.max_particles:
                # If we have too many particles, remove the oldest ones
                self.particles = self.particles[-self.max_particles:]
            
            # Update paddle freeze states
            self.player1_paddle.on_update(delta_time)
            self.player2_paddle.on_update(delta_time)
            
            # Update game timer if active
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
                    self.menu_manager.selected_item = 0
                    return
            
            # Check for stuck puck
            self.last_puck_pos, self.stuck_timer, was_stuck = self.puck.check_stuck(
                delta_time, self.last_puck_pos, self.stuck_timer
            )
            
            # Try to unstick from corners
            was_stuck_in_corner, corner_particles = self.puck.check_for_stuck_in_corner()
            if corner_particles and len(self.particles) < self.max_particles:
                self.particles.extend(corner_particles[:self.max_particles - len(self.particles)])
            
            # Update player paddle
            self.player1_paddle.update_player(self.mouse_x, self.mouse_y)
            
            # Update AI paddle
            ai_particles = self.player2_paddle.update_ai(self.puck, self.settings['ai_difficulty'])
            if ai_particles and len(self.particles) < self.max_particles:
                self.particles.extend(ai_particles[:self.max_particles - len(self.particles)])
            
            # Update puck
            self.puck.update()
            
            # Handle puck-wall collisions with rounded corners
            collision, wall_particles = self.puck.handle_boundary_collision(self.wall_hit_sound)
            if wall_particles and len(self.particles) < self.max_particles:
                self.particles.extend(wall_particles[:self.max_particles - len(self.particles)])
            
            # Handle paddle-puck collisions with reduced particles for performance
            collision, player_particles = self.player1_paddle.check_collision_with_puck(
                self.puck, 
                self.paddle_hit_sound,
                PADDLE_COLORS[self.settings['player_color']]
            )
            if player_particles and len(self.particles) < self.max_particles:
                # Use only 5 particles instead of 10 for better performance
                self.particles.extend(player_particles[:min(5, self.max_particles - len(self.particles))])
                
            collision, ai_particles = self.player2_paddle.check_collision_with_puck(
                self.puck, 
                self.paddle_hit_sound,
                PADDLE_COLORS[self.settings['ai_color']]
            )
            if ai_particles and len(self.particles) < self.max_particles:
                # Use only 5 particles instead of 10 for better performance
                self.particles.extend(ai_particles[:min(5, self.max_particles - len(self.particles))])
            
            # Check for goals
            goal_scorer = self.puck.is_in_goal()
            if goal_scorer:
                arcade.play_sound(self.goal_sound)
                
                if goal_scorer == "PLAYER":
                    self.player1_score += 1
                    # Create goal celebration particles
                    goal_particles = utils.spawn_particles(
                        SCREEN_WIDTH // 2, 
                        SCREEN_HEIGHT - GOAL_HEIGHT // 2, 
                        PADDLE_COLORS[self.settings['player_color']], 
                        15  # Reduced from 30 for performance
                    )
                    if len(self.particles) < self.max_particles:
                        self.particles.extend(goal_particles[:self.max_particles - len(self.particles)])
                    
                    # Check for score-based game end
                    if self.settings['game_mode'] == 0 and self.player1_score >= self.settings['max_score']:
                        self.game_over_message = "You Win!"
                        self.current_state = GAME_OVER_STATE
                        self.menu_manager.selected_item = 0
                        return
                        
                elif goal_scorer == "AI":
                    self.player2_score += 1
                    # Create goal celebration particles
                    goal_particles = utils.spawn_particles(
                        SCREEN_WIDTH // 2, 
                        GOAL_HEIGHT // 2, 
                        PADDLE_COLORS[self.settings['ai_color']], 
                        15  # Reduced from 30 for performance
                    )
                    if len(self.particles) < self.max_particles:
                        self.particles.extend(goal_particles[:self.max_particles - len(self.particles)])
                    
                    # Check for score-based game end
                    if self.settings['game_mode'] == 0 and self.player2_score >= self.settings['max_score']:
                        self.game_over_message = "AI Wins!"
                        self.current_state = GAME_OVER_STATE
                        self.menu_manager.selected_item = 0
                        return
                
                # Reset puck after goal
                self.puck.reset()
                self.last_puck_pos = (self.puck.x, self.puck.y)
            
            # Update particles
            self.particles = utils.update_particles(self.particles, delta_time)
            
            # Update power-ups
            self.update_power_ups(delta_time)
            
    def update_power_ups(self, delta_time):
        """Update power-ups and handle power-up collisions"""
        # If power-ups are disabled, clear any existing ones and return
        if not self.settings['power_ups_enabled']:
            self.power_ups = []
            return
        
        # Spawn new power-ups periodically based on frequency setting
        self.power_up_timer += delta_time
        
        # Determine spawn time based on frequency setting
        spawn_times = [15, 10, 5]  # Low, Medium, High (in seconds)
        spawn_time = spawn_times[self.settings['power_up_frequency']]
        
        # Determine maximum number of power-ups based on frequency
        max_power_ups = [1, 2, 3]  # Low, Medium, High
        max_count = max_power_ups[self.settings['power_up_frequency']]
        
        if self.power_up_timer > spawn_time and len(self.power_ups) < max_count:
            self.power_ups.append(PowerUp())
            self.power_up_timer = 0
        
        # Update power-up lifetimes
        for i in range(len(self.power_ups) - 1, -1, -1):
            if self.power_ups[i].update(delta_time):
                self.power_ups.pop(i)
        
        # Update player paddle power-up timer
        if self.player1_paddle.power_up_active:
            self.player1_paddle.power_up_time -= delta_time
            if self.player1_paddle.power_up_time <= 0:
                self.player1_paddle.power_up_active = False
                # Reset player paddle
                self.player1_paddle.radius = PADDLE_RADIUS
                self.player1_paddle.can_cross_midline = False
                if hasattr(self.puck, 'speed_boost'):
                    self.puck.speed_boost = False
                if hasattr(self.puck, 'freeze_opponent'):
                    self.puck.freeze_opponent = False
        
        # Update AI paddle power-up timer
        if self.player2_paddle.power_up_active:
            self.player2_paddle.power_up_time -= delta_time
            if self.player2_paddle.power_up_time <= 0:
                self.player2_paddle.power_up_active = False
                # Reset AI paddle
                self.player2_paddle.radius = PADDLE_RADIUS
                self.player2_paddle.can_cross_midline = False
                if hasattr(self.puck, 'speed_boost'):
                    self.puck.speed_boost = False
                if hasattr(self.puck, 'freeze_opponent'):
                    self.puck.freeze_opponent = False
                        
        # Check for power-up collisions
        for i in range(len(self.power_ups) - 1, -1, -1):
            # Check player paddle collision
            if self.power_ups[i].check_collision(self.player1_paddle):
                self.power_ups[i].apply(self.player1_paddle, self.puck)
                arcade.play_sound(self.power_up_sound)
                self.power_ups.pop(i)
                continue
                
            # Check AI paddle collision
            if self.power_ups[i].check_collision(self.player2_paddle):
                self.power_ups[i].apply(self.player2_paddle, self.puck)
                arcade.play_sound(self.power_up_sound)
                self.power_ups.pop(i)

    def on_mouse_motion(self, x, y, dx, dy):
        """Called whenever the mouse moves"""
        self.mouse_x = x
        self.mouse_y = y
        
        if self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
            # Update selected menu item based on mouse position
            hovered_item = self.menu_manager.check_mouse_over_menu(x, y)
            if hovered_item is not None and hovered_item != self.menu_manager.selected_item:
                self.menu_manager.selected_item = hovered_item

    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the mouse buttons are pressed"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
                clicked_item = self.menu_manager.check_mouse_over_menu(x, y)
                
                if clicked_item is not None:
                    result = self.menu_manager.handle_menu_click(
                        clicked_item,
                        self.current_state,
                        self.settings,
                        self.menu_select_sound
                    )
                    
                    # Handle state changes
                    if result == "start_game" or result == "restart_game":
                        self.current_state = GAME_STATE
                        self.setup()
                    elif result == "resume_game":
                        self.current_state = GAME_STATE
                        self.timer_active = True
                    elif result == "quit":
                        arcade.close_window()
                    else:
                        self.current_state = result  # For direct state changes

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed"""
        if key == arcade.key.D and modifiers & arcade.key.MOD_CTRL:
            # Toggle debug mode with Ctrl+D
            self.debug_mode = not self.debug_mode
            
        if self.current_state == GAME_STATE:
            if key == arcade.key.ESCAPE:
                self.current_state = PAUSE_STATE
                self.timer_active = False
                self.menu_manager.selected_item = 0
        elif self.current_state in [MENU_STATE, SETTINGS_STATE, PAUSE_STATE, GAME_OVER_STATE]:
            if key == arcade.key.UP:
                if self.menu_manager.selected_item is None:
                    self.menu_manager.selected_item = 0
                else:
                    # Get length of current menu
                    menu_length = len(self.menu_manager.menu_items.get(self.current_state, []))
                    if menu_length > 0:
                        self.menu_manager.selected_item = (self.menu_manager.selected_item - 1) % menu_length
                        arcade.play_sound(self.menu_select_sound)
                    
            elif key == arcade.key.DOWN:
                if self.menu_manager.selected_item is None:
                    self.menu_manager.selected_item = 0
                else:
                    # Get length of current menu
                    menu_length = len(self.menu_manager.menu_items.get(self.current_state, []))
                    if menu_length > 0:
                        self.menu_manager.selected_item = (self.menu_manager.selected_item + 1) % menu_length
                        arcade.play_sound(self.menu_select_sound)
                        
            elif key == arcade.key.ENTER:
                if self.menu_manager.selected_item is not None:
                    # Simulate clicking the selected item
                    if self.menu_manager.selected_item < len(self.menu_manager.menu_positions):
                        pos = self.menu_manager.menu_positions[self.menu_manager.selected_item]
                        self.on_mouse_press(
                            pos['x'] + 10,
                            pos['y'] + 10,
                            arcade.MOUSE_BUTTON_LEFT, 0
                        )

def main():
    """Main function to start the game"""
    window = AirHockeyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()