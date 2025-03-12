import math
import random
import arcade
import utils
from constants import (
    PADDLE_RADIUS, PUCK_RADIUS, FRICTION, WALL_BOUNCE_DAMPING,
    SCREEN_WIDTH, SCREEN_HEIGHT, GOAL_WIDTH, GOAL_HEIGHT,
    AI_SPEED, AI_AGGRESSION, AI_DEFENSE_POSITION, CORNER_RADIUS
)

class Puck:
    def __init__(self):
        self.reset()
        self.opponent_paddle = None  # Reference to opponent paddle for freeze power-up
        
    def reset(self):
        """Reset puck to center with random initial velocity"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.trail = []  # Keep this for compatibility but won't use it
        self.speed_boost = False
        self.freeze_opponent = False
        
    def update(self):
        """Update puck position and apply friction"""
        # Calculate new position
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        
        # Apply friction
        self.dx *= FRICTION
        self.dy *= FRICTION
        
        # Apply maximum speed limit
        MAX_SPEED = 75  # Maximum speed for puck (increased from 15 to 75)
        current_speed = math.sqrt(self.dx**2 + self.dy**2)
        
        if current_speed > MAX_SPEED:
            # Scale down the velocity to the maximum speed
            speed_factor = MAX_SPEED / current_speed
            self.dx *= speed_factor
            self.dy *= speed_factor
        
        # Apply a minimum velocity threshold to completely stop the puck
        # when it's barely moving to prevent drift
        total_speed = math.sqrt(self.dx**2 + self.dy**2)
        if total_speed < 0.1:
            self.dx = 0
            self.dy = 0
        
        # Update position if valid (handled by collision detection)
        self.x = new_x
        self.y = new_y
        
        # Trail is disabled
                
    def handle_boundary_collision(self, sound=None):
        """Handle collision with the rounded rink boundaries"""
        collision_happened = False
        particles = []
        
        # Get goal boundaries for collision checking
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2
        
        # Store original position and velocity
        original_x, original_y = self.x, self.y
        
        # Check for corner collisions
        corner_positions = utils.get_rink_corner_positions()
        
        # Check if puck is in any corner region
        corner_index = utils.is_point_in_corner_region(self.x, self.y)
        
        if corner_index >= 0:
            # Get corner center coordinates
            corner_x, corner_y = corner_positions[corner_index]
            
            # Calculate distance from corner center to puck
            dx = self.x - corner_x
            dy = self.y - corner_y
            distance = math.sqrt(dx**2 + dy**2)
            
            # If puck is outside the rounded boundary
            if distance > CORNER_RADIUS - PUCK_RADIUS:
                # Calculate normal vector from corner center to puck
                if distance > 0:
                    normal_x = dx / distance
                    normal_y = dy / distance
                else:
                    normal_x, normal_y = 0, 0
                
                # Position puck on the boundary
                self.x = corner_x + normal_x * (CORNER_RADIUS - PUCK_RADIUS)
                self.y = corner_y + normal_y * (CORNER_RADIUS - PUCK_RADIUS)
                
                # Calculate reflection vector
                dot_product = self.dx * normal_x + self.dy * normal_y
                self.dx = (self.dx - 2 * dot_product * normal_x) * WALL_BOUNCE_DAMPING
                self.dy = (self.dy - 2 * dot_product * normal_y) * WALL_BOUNCE_DAMPING
                
                collision_happened = True
        
        # Check straight boundaries (only if not in corner)
        if corner_index < 0:
            # Left boundary
            if self.x - PUCK_RADIUS < 0:
                self.x = PUCK_RADIUS
                self.dx *= -WALL_BOUNCE_DAMPING
                collision_happened = True
                    
            # Right boundary
            elif self.x + PUCK_RADIUS > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - PUCK_RADIUS
                self.dx *= -WALL_BOUNCE_DAMPING
                collision_happened = True
                    
            # Bottom boundary (check if not in goal)
            if self.y - PUCK_RADIUS < 0:
                if not (GOAL_LEFT <= self.x <= GOAL_RIGHT):
                    self.y = PUCK_RADIUS
                    self.dy *= -WALL_BOUNCE_DAMPING
                    collision_happened = True
                        
            # Top boundary (check if not in goal)
            elif self.y + PUCK_RADIUS > SCREEN_HEIGHT:
                if not (GOAL_LEFT <= self.x <= GOAL_RIGHT):
                    self.y = SCREEN_HEIGHT - PUCK_RADIUS
                    self.dy *= -WALL_BOUNCE_DAMPING
                    collision_happened = True
        
        # Play sound and create particles if collision happened
        if collision_happened:
            if sound:
                arcade.play_sound(sound)
            particles = utils.spawn_particles(self.x, self.y, arcade.color.WHITE, 5)
            
        # Add minimum speed threshold to prevent extremely slow movement
        total_speed = math.sqrt(self.dx**2 + self.dy**2)
        if total_speed < 0.1:
            self.dx = 0
            self.dy = 0
            
        return collision_happened, particles
    
    def is_in_goal(self):
        """Check if puck is in either goal"""
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2
        
        # Check if puck is completely past the goal line
        if (self.y + PUCK_RADIUS <= 0 and 
            GOAL_LEFT <= self.x <= GOAL_RIGHT):
            return "AI"  # AI scored
        elif (self.y - PUCK_RADIUS >= SCREEN_HEIGHT and 
              GOAL_LEFT <= self.x <= GOAL_RIGHT):
            return "PLAYER"  # Player scored
        return None  # No goal
    
    def check_stuck(self, delta_time, last_pos, stuck_timer):
        """Check if puck is stuck and apply escape velocity if needed"""
        # We're disabling automatic escape velocity to prevent random movement
        current_pos = (self.x, self.y)
        return current_pos, 0, False
    
    def check_for_stuck_in_corner(self):
        """Explicitly check and fix if puck is stuck in corners"""
        # We're disabling this function as it can cause unexpected movement
        return False, []
    
    def draw(self):
        """Draw the puck without trail"""
        # Draw puck only (no trail)
        arcade.draw_circle_filled(
            self.x,
            self.y,
            PUCK_RADIUS,
            arcade.color.GRAY
        )

class Paddle:
    def __init__(self, is_ai=False):
        self.is_ai = is_ai
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT * (3/4 if is_ai else 1/4)
        self.dx = 0
        self.dy = 0
        self.radius = PADDLE_RADIUS
        self.target_x = SCREEN_WIDTH // 2
        self.target_y = self.y
        self.power_up_active = False
        self.power_up_time = 0
        self.can_cross_midline = False  # New property for speed power-up
        self.is_frozen = False  # New property for freeze power-up
        self.freeze_timer = 0   # Timer for freeze duration
        self.opponent_paddle = None  # Reference to opponent paddle
        
    def on_update(self, delta_time):
        """Update paddle's status effects"""
        # Handle freeze timer
        if self.is_frozen:
            self.freeze_timer -= delta_time
            if self.freeze_timer <= 0:
                self.is_frozen = False
                self.freeze_timer = 0
        
    def update_player(self, mouse_x, mouse_y):
        """Update player paddle based on mouse position"""
        # Calculate movement deltas
        self.dx = mouse_x - self.x
        self.dy = mouse_y - self.y
        
        # Skip movement if frozen
        if self.is_frozen:
            return
            
        # Update paddle position with constraint
        if self.can_cross_midline:
            # Can go anywhere in rink
            self.x, self.y = utils.constrain_to_rink(mouse_x, mouse_y, self.radius)
        else:
            # Constrained to bottom half
            self.x, self.y = utils.constrain_to_rink(mouse_x, mouse_y, self.radius, 'bottom')
    
    def update_ai(self, puck, ai_difficulty):
        """Update AI paddle movement"""
        # If AI is frozen by power-up, don't move
        if self.is_frozen:
            return []
            
        # Default defensive position
        target_x = SCREEN_WIDTH // 2
        target_y = SCREEN_HEIGHT * AI_DEFENSE_POSITION
        
        # Enhanced corner handling
        corner_index = utils.is_point_in_corner_region(puck.x, puck.y)
        is_in_corner = corner_index >= 0 and puck.y > SCREEN_HEIGHT / 2
        
        if is_in_corner:
            # For corner situations, move more directly toward the puck
            corner_angle = math.atan2(puck.y - self.y, puck.x - self.x)
            
            # Calculate a position slightly offset from the puck to hit it toward center
            offset_distance = self.radius + PUCK_RADIUS + 5
            
            if puck.x < SCREEN_WIDTH // 2:
                # Left corner - approach from right
                target_x = puck.x + offset_distance * 0.5
            else:
                # Right corner - approach from left
                target_x = puck.x - offset_distance * 0.5
                
            target_y = puck.y - 5  # Slightly above the puck
            
            # Increase AI speed for corner retrieval
            ai_speed = AI_SPEED * 1.5
            
            # Move directly toward the calculated position
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                self.dx = (dx / distance) * ai_speed
                self.dy = (dy / distance) * ai_speed
                
                # Update position with constraint
                new_x = self.x + self.dx
                new_y = self.y + self.dy
                
                # Check if we can cross midline
                if self.can_cross_midline:
                    # Constrain to full rink
                    self.x, self.y = utils.constrain_to_rink(new_x, new_y, self.radius)
                else:
                    # Constrain to top half
                    self.x, self.y = utils.constrain_to_rink(new_x, new_y, self.radius, 'top')
                
            # Skip the rest of the AI logic if in corner mode
            return []
        
        # Predict where puck will intersect AI's y-position
        if puck.dy > 0:  # Puck moving upward
            time_to_intersect = (target_y - puck.y) / puck.dy if puck.dy != 0 else 0
            predicted_x = puck.x + puck.dx * time_to_intersect

            # Keep prediction within bounds
            predicted_x = max(self.radius, 
                            min(SCREEN_WIDTH - self.radius, predicted_x))

            # Move towards predicted position
            if abs(puck.dy) > 1:  # Only if puck moving with significant speed
                target_x = predicted_x

        # If puck is in AI's half, move to intercept
        if puck.y > SCREEN_HEIGHT // 2 or self.can_cross_midline:  # Allow crossing midline with power-up
            dx = puck.x - self.x
            dy = puck.y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                target_x = puck.x
                target_y = puck.y - self.radius
                
                # Adjust aggression based on puck position
                if puck.y > SCREEN_HEIGHT * 0.75:
                    # More aggressive when puck is close to AI's goal
                    target_x = puck.x + puck.dx * AI_AGGRESSION
                    target_y = puck.y + puck.dy * AI_AGGRESSION

        # Move AI paddle towards target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Apply speed boost if power-up is active
            speed_multiplier = 1.5 if (self.power_up_active and puck.speed_boost) else 1.0
            
            # Adjust base speed by difficulty
            base_speed = AI_SPEED
            if ai_difficulty == 0:  # Easy
                base_speed = 5
            elif ai_difficulty == 2:  # Hard
                base_speed = 10
            
            speed = base_speed * speed_multiplier
            
            # Normalize movement vector
            move_x = (dx / distance) * speed
            move_y = (dy / distance) * speed
            
            # Update position
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            # Check if we can cross midline
            if self.can_cross_midline:
                # Constrain to full rink
                self.x, self.y = utils.constrain_to_rink(new_x, new_y, self.radius)
            else:
                # Constrain to top half
                self.x, self.y = utils.constrain_to_rink(new_x, new_y, self.radius, 'top')
            
            # Update velocity for collision physics
            self.dx = move_x
            self.dy = move_y
        
        return []
        
    def draw(self, color, power_up_active=False):
        """Draw the paddle with optional power-up effects"""
        # Add glow effect if power-up is active
        if power_up_active:
            # Draw glow
            for i in range(3):
                size_multiplier = 1.1 + (i * 0.1)
                alpha = 100 - (i * 30)
                glow_color = (color[0], color[1], color[2], alpha)
                arcade.draw_circle_filled(
                    self.x,
                    self.y,
                    self.radius * size_multiplier,
                    glow_color
                )
        
        # Draw the paddle
        arcade.draw_circle_filled(
            self.x,
            self.y,
            self.radius,
            color
        )
        
        # Draw freeze visual indicator if frozen
        if self.is_frozen:
            # Draw freeze indicator (snowflake symbol or ice effect)
            arcade.draw_text(
                "❄",
                self.x,
                self.y,
                arcade.color.CYAN,
                20,
                anchor_x="center",
                anchor_y="center"
            )
        
    def check_collision_with_puck(self, puck, sound=None, paddle_color=arcade.color.WHITE):
        """Check and handle collision with puck"""
        dx = puck.x - self.x
        dy = puck.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        particles = []
        
        if distance <= self.radius + PUCK_RADIUS:
            # Calculate collision angle and normalize the direction
            angle = math.atan2(dy, dx)
            
            # Move puck outside of paddle to prevent sticking
            overlap = self.radius + PUCK_RADIUS - distance
            puck.x += math.cos(angle) * overlap
            puck.y += math.sin(angle) * overlap
            
            # Calculate new velocity
            speed = math.sqrt(puck.dx**2 + puck.dy**2)
            speed = max(speed, 5)  # Minimum speed after collision
            
            # Combine paddle and puck momentum
            momentum_factor = 0.5
            
            # Apply power-up effects to collision
            if self.power_up_active and puck.speed_boost:
                speed *= 1.5  # Boost speed
                momentum_factor = 0.8  # More paddle momentum transfer
            
            puck.dx = (math.cos(angle) * speed * 1.2 + self.dx * momentum_factor)
            puck.dy = (math.sin(angle) * speed * 1.2 + self.dy * momentum_factor)
            
            # Play sound effect
            if sound:
                arcade.play_sound(sound)
            
            # Spawn particles at collision point with paddle color
            collision_x = puck.x - math.cos(angle) * PUCK_RADIUS
            collision_y = puck.y - math.sin(angle) * PUCK_RADIUS
            particles = utils.spawn_particles(collision_x, collision_y, paddle_color, 10)
            
            return True, particles
            
        return False, particles
        
class PowerUp:
    def __init__(self, x=None, y=None, power_type=None):
        # Define radius first so it can be used in position calculations
        self.radius = 15
        
        # If coordinates or type not specified, generate random ones
        if x is None or y is None:
            # Place on center line
            self.x = random.randint(self.radius + 10, SCREEN_WIDTH - self.radius - 10)
            self.y = SCREEN_HEIGHT // 2  # Exactly on the center line
        else:
            self.x = x
            self.y = y
            
        if power_type is None:
            power_up_types = ['speed', 'size', 'freeze']
            self.type = random.choice(power_up_types)
        else:
            self.type = power_type
            
        self.lifetime = 10  # Power-up disappears after 10 seconds if not collected
        
    def update(self, delta_time):
        """Update power-up lifetime"""
        self.lifetime -= delta_time
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
        paddle.power_up_time = duration
        
        if self.type == 'speed':
            # Speed boost affects puck when hit by this paddle
            puck.speed_boost = True
            # Allow paddle to cross midline with speed power-up
            paddle.can_cross_midline = True
            
        elif self.type == 'size':
            # Increase paddle size
            paddle.radius = PADDLE_RADIUS * 1.5
            
        elif self.type == 'freeze':
            # Freeze opponent paddle for 3 seconds
            if paddle.opponent_paddle:
                paddle.opponent_paddle.is_frozen = True
                paddle.opponent_paddle.freeze_timer = 3.0  # 3 seconds freeze duration
                puck.freeze_opponent = True  # Mark that freeze is active
            
    def draw(self):
        """Draw the power-up"""
        if self.type == 'speed':
            color = arcade.color.YELLOW
            icon = "⚡"
        elif self.type == 'size':
            color = arcade.color.GREEN
            icon = "+"
        elif self.type == 'freeze':
            color = arcade.color.CYAN
            icon = "❄"
        else:
            color = arcade.color.WHITE
            icon = "?"
            
        # Draw background circle
        arcade.draw_circle_filled(
            self.x,
            self.y,
            self.radius,
            color
        )
        
        # Draw icon
        arcade.draw_text(
            icon,
            self.x,
            self.y,
            arcade.color.BLACK,
            20,
            anchor_x="center",
            anchor_y="center"
        )