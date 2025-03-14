import math
import random
import arcade
from constants import PADDLE_RADIUS, PUCK_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT, GOAL_WIDTH

class PowerUp:
    def __init__(self, x=None, y=None, power_type=None):
        # Define radius first so it can be used in position calculations
        self.radius = 15
        
        # If coordinates or type not specified, generate random ones
        if x is None or y is None:
            # Place ONLY on the center line with some horizontal variation
            self.x = random.randint(self.radius + 20, SCREEN_WIDTH - self.radius - 20)
            
            # Fix power-ups to spawn only on the center line
            self.y = SCREEN_HEIGHT // 2
        else:
            self.x = x
            self.y = y
            
        if power_type is None:
            power_up_types = ['speed', 'size', 'freeze', 'multi_puck', 'goal_shrink', 'repulsor']
            self.type = random.choice(power_up_types)
        else:
            self.type = power_type
            
        self.lifetime = 10  # Power-up disappears after 10 seconds if not collected
        self.pulse_time = 0  # Time counter for pulsing effect
        
    def update(self, delta_time):
        """Update power-up lifetime and pulse time"""
        self.lifetime -= delta_time
        self.pulse_time += delta_time  # Increment the pulse time counter
        return self.lifetime <= 0  # Return True if should be removed
        
    def check_collision(self, paddle):
        """Check if paddle collects this power-up"""
        dx = self.x - paddle.x
        dy = self.y - paddle.y
        distance = math.sqrt(dx**2 + dy**2)
        
        return distance <= paddle.radius + self.radius
        
    def apply(self, paddle, puck, duration=10.0):
        """Apply power-up effects to paddle"""
        paddle.power_up_active = True
        
        # Default power-up duration of 5 seconds for new power-ups
        power_up_duration = 5.0
        
        # Set different durations based on power-up type
        if self.type == 'freeze':
            # Freeze is always 3 seconds for balance
            freeze_duration = 3.0
            paddle.power_up_time = power_up_duration
            
            # Freeze opponent paddle
            if paddle.opponent_paddle:
                paddle.opponent_paddle.is_frozen = True
                paddle.opponent_paddle.freeze_timer = freeze_duration
                puck.freeze_opponent = True  # Mark that freeze is active
        
        elif self.type == 'multi_puck':
            paddle.multi_puck_active = True
            paddle.power_up_time = power_up_duration
        
        elif self.type == 'goal_shrink':
            # Shrink the player's OWN goal, not the opponent's
            paddle.goal_shrink_active = True
            paddle.goal_shrink_timer = power_up_duration
            paddle.power_up_time = power_up_duration
        
        elif self.type == 'repulsor':
            puck.repulsor_active = True
            puck.repulsor_owner = paddle
            paddle.power_up_time = power_up_duration
        
        else:
            # Regular power-up duration for original power-ups
            paddle.power_up_time = duration
            
            if self.type == 'speed':
                # Speed boost affects puck when hit by this paddle
                puck.speed_boost = True
                # Allow paddle to cross midline with speed power-up
                paddle.can_cross_midline = True
                
            elif self.type == 'size':
                # Increase paddle size
                paddle.radius = PADDLE_RADIUS * 1.5
            
    def draw(self):
        """Draw the power-up with pulsing effect"""
        # Set color and icon based on type
        if self.type == 'speed':
            color = arcade.color.YELLOW
            icon = "⚡"
        elif self.type == 'size':
            color = arcade.color.GREEN
            icon = "+"
        elif self.type == 'freeze':
            color = arcade.color.CYAN
            icon = "❄"
        elif self.type == 'multi_puck':
            color = arcade.color.ORANGE
            icon = "◉◉◉"
        elif self.type == 'goal_shrink':
            color = arcade.color.PURPLE
            icon = "⊏⊐"
        elif self.type == 'repulsor':
            color = arcade.color.RED
            icon = "↗"
        else:
            color = arcade.color.WHITE
            icon = "?"
        
        # Calculate pulse effect based on pulse_time
        pulse = math.sin(self.pulse_time * 5) * 0.2 + 1.0  # Pulse between 0.8 and 1.2 scale
        
        # Draw background circle with pulse effect
        arcade.draw_circle_filled(
            self.x,
            self.y,
            self.radius * pulse,
            color
        )
        
        # Draw inner circle for more visual appeal
        arcade.draw_circle_filled(
            self.x,
            self.y,
            self.radius * 0.7 * pulse,
            (255, 255, 255, 100)  # Semi-transparent white
        )
        
        # Draw icon
        text_size = 14 if self.type == 'multi_puck' else 20
        arcade.draw_text(
            icon,
            self.x,
            self.y,
            arcade.color.BLACK,
            text_size,
            anchor_x="center",
            anchor_y="center"
        )