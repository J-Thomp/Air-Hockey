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
        
        # For repulsor power-up
        self.repulsor_active = False
        self.repulsor_owner = None  # Reference to the paddle that activated repulsor
        self.repulsor_strength = 0.5  # Strength of the repulsion effect

    # Update the update method to handle the repulsor power-up
    def update(self):
        """Update puck position and apply friction"""
        # Calculate new position
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        
        # Apply friction
        self.dx *= FRICTION
        self.dy *= FRICTION
        
        # Apply repulsor effect if active
        if self.repulsor_active and self.repulsor_owner:
            # Determine which goal to attract towards based on owner
            target_y = 0 if self.repulsor_owner.is_ai else SCREEN_HEIGHT
            
            # Vector towards target goal
            attract_dx = 0  # No horizontal attraction
            attract_dy = target_y - self.y
            
            # Normalize and apply attraction
            attract_distance = math.sqrt(attract_dx**2 + attract_dy**2)
            if attract_distance > 0:
                self.dx += (attract_dx / attract_distance) * self.repulsor_strength
                self.dy += (attract_dy / attract_distance) * self.repulsor_strength
        
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

    # Add visualizations for the repulsor in the draw method
    def draw(self):
        """Draw the puck with power-up effects"""
        # Draw repulsor effect if active
        if self.repulsor_active and self.repulsor_owner:
            # Determine which goal to attract towards
            target_y = 0 if self.repulsor_owner.is_ai else SCREEN_HEIGHT
            
            # Calculate direction (up or down)
            direction = 1 if target_y > self.y else -1
            
            # Draw an arrow showing the force direction
            arrow_length = 40
            end_y = self.y + direction * arrow_length
            
            # Use a standard RGB color - RED is (255, 0, 0)
            arrow_color = (255, 0, 0)  # Explicit RGB values for red
            
            # Draw the arrow line
            arcade.draw_line(
                self.x, self.y,
                self.x, end_y,
                arrow_color,
                3  # Line width
            )
            
            # Draw arrowhead
            arrowhead_size = 10
            point1 = (self.x, end_y)
            point2 = (self.x - arrowhead_size/2, end_y - direction * arrowhead_size)
            point3 = (self.x + arrowhead_size/2, end_y - direction * arrowhead_size)
            
            arcade.draw_triangle_filled(
                point1[0], point1[1],
                point2[0], point2[1],
                point3[0], point3[1],
                arrow_color
            )
        
        # Draw puck
        arcade.draw_circle_filled(
            self.x,
            self.y,
            PUCK_RADIUS,
            arcade.color.GRAY
        )
                
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
        """Check if puck is in either goal, accounting for shrunk goals"""
        # Get references to the paddles (if available)
        player_paddle = None
        ai_paddle = None
        
        if hasattr(self, 'opponent_paddle') and self.opponent_paddle:
            player_paddle = self.opponent_paddle.opponent_paddle  # This is the human player's paddle
            ai_paddle = self.opponent_paddle  # This is the AI paddle
        
        # Adjust goal width if goal shrink is active on the respective paddle
        player_goal_width = GOAL_WIDTH
        ai_goal_width = GOAL_WIDTH
        
        # Check if player has goal shrink active (affects player's goal)
        if player_paddle and hasattr(player_paddle, 'goal_shrink_active') and player_paddle.goal_shrink_active:
            player_goal_width = GOAL_WIDTH * 0.5
        
        # Check if AI has goal shrink active (affects AI's goal)
        if ai_paddle and hasattr(ai_paddle, 'goal_shrink_active') and ai_paddle.goal_shrink_active:
            ai_goal_width = GOAL_WIDTH * 0.5
        
        # Calculate actual goal boundaries
        PLAYER_GOAL_LEFT = SCREEN_WIDTH // 2 - player_goal_width // 2
        PLAYER_GOAL_RIGHT = SCREEN_WIDTH // 2 + player_goal_width // 2
        
        AI_GOAL_LEFT = SCREEN_WIDTH // 2 - ai_goal_width // 2
        AI_GOAL_RIGHT = SCREEN_WIDTH // 2 + ai_goal_width // 2
        
        # Check if puck is completely past the goal line
        if (self.y + PUCK_RADIUS <= 0 and 
            PLAYER_GOAL_LEFT <= self.x <= PLAYER_GOAL_RIGHT):
            return "AI"  # AI scored
        elif (self.y - PUCK_RADIUS >= SCREEN_HEIGHT and 
            AI_GOAL_LEFT <= self.x <= AI_GOAL_RIGHT):
            return "PLAYER"  # Player scored
        return None  # No goal
        
        # Calculate actual goal boundaries
        PLAYER_GOAL_LEFT = SCREEN_WIDTH // 2 - player_goal_width // 2
        PLAYER_GOAL_RIGHT = SCREEN_WIDTH // 2 + player_goal_width // 2
        
        AI_GOAL_LEFT = SCREEN_WIDTH // 2 - ai_goal_width // 2
        AI_GOAL_RIGHT = SCREEN_WIDTH // 2 + ai_goal_width // 2
        
        # Check if puck is completely past the goal line
        if (self.y + PUCK_RADIUS <= 0 and 
            PLAYER_GOAL_LEFT <= self.x <= PLAYER_GOAL_RIGHT):
            return "AI"  # AI scored
        elif (self.y - PUCK_RADIUS >= SCREEN_HEIGHT and 
            AI_GOAL_LEFT <= self.x <= AI_GOAL_RIGHT):
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

# Complete Paddle class with fixed update_player method

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
        self.can_cross_midline = False  # For speed power-up
        self.is_frozen = False  # For freeze power-up
        self.freeze_timer = 0   # Timer for freeze duration
        self.opponent_paddle = None  # Reference to opponent paddle
        self.multi_puck_active = False  # For multi-puck power-up


        # New properties for additional power-ups
        self.multi_puck_active = False  # For multi-puck power-up
        self.goal_shrink_active = False  # For goal shrink power-up
        self.goal_shrink_timer = 0  # Timer for goal shrink duration
    
    def on_update(self, delta_time):
        """Update paddle's status effects"""
        # Handle freeze timer
        if self.is_frozen:
            self.freeze_timer -= delta_time
            if self.freeze_timer <= 0:
                self.is_frozen = False
                self.freeze_timer = 0
        
        # Handle goal shrink timer
        if self.goal_shrink_active:
            self.goal_shrink_timer -= delta_time
            if self.goal_shrink_timer <= 0:
                self.goal_shrink_active = False
                self.goal_shrink_timer = 0
    
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
        # Draw multi-puck effect (3 side-by-side paddles)
        if self.multi_puck_active:
            # Calculate positions for side paddles
            offset = self.radius * 1.8  # Distance between paddle centers
            
            # Draw left paddle
            arcade.draw_circle_filled(
                self.x - offset,
                self.y,
                self.radius * 0.8,  # Slightly smaller
                color
            )
            
            # Draw right paddle
            arcade.draw_circle_filled(
                self.x + offset,
                self.y,
                self.radius * 0.8,  # Slightly smaller
                color
            )
        
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
            # Draw freeze indicator (snowflake symbol)
            arcade.draw_text(
                "❄",
                self.x,
                self.y,
                arcade.color.CYAN,
                20,
                anchor_x="center",
                anchor_y="center"
            )
        
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
            # Draw freeze indicator (snowflake symbol)
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
        # Normal collision detection for the main paddle
        dx = puck.x - self.x
        dy = puck.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        collision_happened = False
        particles = []
        
        # Check main paddle collision
        if distance <= self.radius + PUCK_RADIUS:
            collision_happened = True
        
        # Check side paddles if multi-puck is active
        if self.multi_puck_active and not collision_happened:
            # Left paddle
            dx_left = puck.x - (self.x - self.radius * 1.8)
            dy_left = puck.y - self.y
            distance_left = math.sqrt(dx_left**2 + dy_left**2)
            
            # Right paddle
            dx_right = puck.x - (self.x + self.radius * 1.8)
            dy_right = puck.y - self.y
            distance_right = math.sqrt(dx_right**2 + dy_right**2)
            
            # Check if puck collides with either side paddle
            if distance_left <= self.radius * 0.8 + PUCK_RADIUS:
                collision_happened = True
                # Update collision vector to use the left paddle's position
                dx = dx_left
                dy = dy_left
                distance = distance_left
            elif distance_right <= self.radius * 0.8 + PUCK_RADIUS:
                collision_happened = True
                # Update collision vector to use the right paddle's position
                dx = dx_right
                dy = dy_right
                distance = distance_right
        
        if collision_happened:
            # Calculate collision angle and normalize the direction
            angle = math.atan2(dy, dx)
            
            # Move puck outside of paddle to prevent sticking
            overlap = (self.radius if not self.multi_puck_active else self.radius * 0.8) + PUCK_RADIUS - distance
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