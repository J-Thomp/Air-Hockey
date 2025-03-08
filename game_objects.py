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
        
    def reset(self):
        """Reset puck to center with random initial velocity"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.trail = []
        self.speed_boost = False
        self.freeze_opponent = False
        
    def update(self):
        """Update puck position and apply friction"""
        self.x += self.dx
        self.y += self.dy
        
        # Apply friction
        self.dx *= FRICTION
        self.dy *= FRICTION
        
        # Update trail with a chance to add new position
        if len(self.trail) > 0 and random.random() < 0.3:
            self.trail.insert(0, {'x': self.x, 'y': self.y})
            if len(self.trail) > 5:
                self.trail.pop()
                
    def handle_boundary_collision(self, sound=None):
        """Handle collision with the rounded rink boundaries"""
        collision_happened = False
        particles = []
        
        # Calculate distances to each of the four corners
        corner_positions = [
            (CORNER_RADIUS, CORNER_RADIUS),  # Bottom-left
            (SCREEN_WIDTH - CORNER_RADIUS, CORNER_RADIUS),  # Bottom-right
            (CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS),  # Top-left
            (SCREEN_WIDTH - CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS)  # Top-right
        ]
        
        # Check if puck is near any corner
        for corner_x, corner_y in corner_positions:
            dx = self.x - corner_x
            dy = self.y - corner_y
            distance = math.sqrt(dx**2 + dy**2)
            
            # If puck is inside a corner but outside the rounded boundary
            if distance < CORNER_RADIUS + PUCK_RADIUS and distance > CORNER_RADIUS:
                # Calculate normal vector from corner center to puck
                if distance > 0:
                    normal_x = dx / distance
                    normal_y = dy / distance
                else:
                    normal_x, normal_y = 0, 0
                
                # Position puck on the boundary
                self.x = corner_x + normal_x * (CORNER_RADIUS + PUCK_RADIUS)
                self.y = corner_y + normal_y * (CORNER_RADIUS + PUCK_RADIUS)
                
                # Calculate reflection vector
                dot_product = self.dx * normal_x + self.dy * normal_y
                self.dx = (self.dx - 2 * dot_product * normal_x) * WALL_BOUNCE_DAMPING
                self.dy = (self.dy - 2 * dot_product * normal_y) * WALL_BOUNCE_DAMPING
                
                # Add vertical component to help prevent getting stuck
                if abs(self.dy) < 1:
                    self.dy = random.uniform(1, 3) * (1 if self.y < SCREEN_HEIGHT/2 else -1)
                
                collision_happened = True
                break
        
        # Check straight boundaries
        # Check goal areas too (except for the openings)
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2
        
        # Left boundary
        if self.x - PUCK_RADIUS < 0:
            if self.y < CORNER_RADIUS or self.y > SCREEN_HEIGHT - CORNER_RADIUS:
                # Let the corner handling take care of this
                pass
            else:
                self.x = PUCK_RADIUS
                self.dx *= -WALL_BOUNCE_DAMPING
                collision_happened = True
                
        # Right boundary
        elif self.x + PUCK_RADIUS > SCREEN_WIDTH:
            if self.y < CORNER_RADIUS or self.y > SCREEN_HEIGHT - CORNER_RADIUS:
                # Let the corner handling take care of this
                pass
            else:
                self.x = SCREEN_WIDTH - PUCK_RADIUS
                self.dx *= -WALL_BOUNCE_DAMPING
                collision_happened = True
                
        # Bottom boundary (check if not in goal)
        if self.y - PUCK_RADIUS < 0:
            if not (GOAL_LEFT <= self.x <= GOAL_RIGHT):
                if self.x < CORNER_RADIUS or self.x > SCREEN_WIDTH - CORNER_RADIUS:
                    # Let the corner handling take care of this
                    pass
                else:
                    self.y = PUCK_RADIUS
                    self.dy *= -WALL_BOUNCE_DAMPING
                    collision_happened = True
                    
        # Top boundary (check if not in goal)
        elif self.y + PUCK_RADIUS > SCREEN_HEIGHT:
            if not (GOAL_LEFT <= self.x <= GOAL_RIGHT):
                if self.x < CORNER_RADIUS or self.x > SCREEN_WIDTH - CORNER_RADIUS:
                    # Let the corner handling take care of this
                    pass
                else:
                    self.y = SCREEN_HEIGHT - PUCK_RADIUS
                    self.dy *= -WALL_BOUNCE_DAMPING
                    collision_happened = True
                    
        # Play sound and create particles if collision happened
        if collision_happened:
            if sound:
                arcade.play_sound(sound)
            particles = utils.spawn_particles(self.x, self.y, arcade.color.WHITE, 5)
            
            # Add extra bounce when in corners to prevent getting stuck
            is_near_corner = ((self.x < SCREEN_WIDTH * 0.25 or self.x > SCREEN_WIDTH * 0.75) and
                            (self.y < SCREEN_HEIGHT * 0.25 or self.y > SCREEN_HEIGHT * 0.75))
            
            is_slow = abs(self.dx) < 2 and abs(self.dy) < 2
            
            if is_near_corner and is_slow:
                # Add force toward center
                center_x = SCREEN_WIDTH // 2
                center_y = SCREEN_HEIGHT // 2
                
                # Vector to center
                to_center_x = center_x - self.x
                to_center_y = center_y - self.y
                
                # Normalize and apply boost
                magnitude = math.sqrt(to_center_x**2 + to_center_y**2)
                if magnitude > 0:
                    self.dx += (to_center_x / magnitude) * 3
                    self.dy += (to_center_y / magnitude) * 3
        
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
        current_pos = (self.x, self.y)
        distance_moved = math.sqrt((current_pos[0] - last_pos[0])**2 + 
                                  (current_pos[1] - last_pos[1])**2)
        
        if distance_moved < 5:  # If puck hasn't moved much
            stuck_timer += delta_time
            if stuck_timer > 2:  # If stuck for more than 2 seconds
                # Apply small random impulse to break free
                self.dx += random.uniform(-3, 3)
                self.dy += random.uniform(-3, 3)
                stuck_timer = 0
                return current_pos, stuck_timer, True
        else:
            stuck_timer = 0
            
        return current_pos, stuck_timer, False
    
    def check_for_stuck_in_corner(self):
        """Explicitly check and fix if puck is stuck in corners"""
        particles = []
        
        # Check if puck is in a corner and moving very slowly
        is_in_left_edge = self.x <= PUCK_RADIUS + 5
        is_in_right_edge = self.x >= SCREEN_WIDTH - PUCK_RADIUS - 5
        is_moving_slowly = abs(self.dx) < 1 and abs(self.dy) < 1
        
        if (is_in_left_edge or is_in_right_edge) and is_moving_slowly:
            # Apply a stronger impulse to escape the corner
            # Direct it toward the center of the field
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            # Calculate direction vector to center
            dx = center_x - self.x
            dy = center_y - self.y
            # Normalize
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                dx = dx / length * 5  # Apply a significant force
                dy = dy / length * 5
                
                # Set the new velocity
                self.dx = dx
                self.dy = dy
                
                # Create escape particles for visual feedback
                particles = utils.spawn_particles(self.x, self.y, 
                                        arcade.color.YELLOW, 8)
                return True, particles
                
        return False, particles
    
    def draw(self):
        """Draw the puck and its trail"""
        # Draw puck trail (visual effect)
        for i, trail in enumerate(self.trail):
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
        
        # Draw puck
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
        
    def update_player(self, mouse_x, mouse_y):
        """Update player paddle based on mouse position"""
        # Calculate movement deltas
        self.dx = mouse_x - self.x
        self.dy = mouse_y - self.y
        
        # Update paddle position
        self.x = mouse_x
        self.y = mouse_y
        
        # Constrain paddle to bottom half of screen and within boundaries
        self.constrain_to_rink(top_half=False)
    
    def update_ai(self, puck, ai_difficulty):
        """Update AI paddle movement"""
        # If AI is frozen by power-up, don't move
        if self.power_up_active and puck.freeze_opponent:
            return []
            
        # Default defensive position
        target_x = SCREEN_WIDTH // 2
        target_y = SCREEN_HEIGHT * AI_DEFENSE_POSITION
        
        # Enhanced corner handling
        is_in_corner = ((puck.x < PADDLE_RADIUS * 2 or 
                        puck.x > SCREEN_WIDTH - PADDLE_RADIUS * 2) and 
                        puck.y > SCREEN_HEIGHT / 2)
        
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
                
                # Update position
                self.x += self.dx
                self.y += self.dy
                
                # Constrain to top half of screen
                self.constrain_to_rink(top_half=True)
            
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
        if puck.y > SCREEN_HEIGHT // 2:
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
            
            self.dx = (dx / distance) * base_speed * speed_multiplier
            self.dy = (dy / distance) * base_speed * speed_multiplier
            
            # Update position
            self.x += self.dx
            self.y += self.dy
            
            # Constrain to top half of screen
            self.constrain_to_rink(top_half=True)
        
        return []
    
    def constrain_to_rink(self, top_half=False):
        """Constrain paddle position to the appropriate half of the rink"""
        # Constrain within the borders, considering rounded corners
        if top_half:
            # AI paddle - constrain to top half
            min_y = SCREEN_HEIGHT // 2 + self.radius
            max_y = SCREEN_HEIGHT - self.radius
            self.y = max(min_y, min(max_y, self.y))
        else:
            # Player paddle - constrain to bottom half
            min_y = self.radius
            max_y = SCREEN_HEIGHT // 2 - self.radius
            self.y = max(min_y, min(max_y, self.y))
            
        # Constrain x-coordinate to be within the rink
        min_x = self.radius
        max_x = SCREEN_WIDTH - self.radius
        self.x = max(min_x, min(max_x, self.x))
        
        # Special handling for corners
        if self.y < CORNER_RADIUS and self.x < CORNER_RADIUS:
            # Bottom-left corner
            distance = math.sqrt((self.x - CORNER_RADIUS)**2 + (self.y - CORNER_RADIUS)**2)
            if distance < CORNER_RADIUS - self.radius:
                # Paddle is within the valid area, no adjustment needed
                pass
            else:
                # Calculate normalized direction from corner center to paddle
                dx = self.x - CORNER_RADIUS
                dy = self.y - CORNER_RADIUS
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    # Move paddle to valid position
                    self.x = CORNER_RADIUS + dx/norm * (CORNER_RADIUS - self.radius)
                    self.y = CORNER_RADIUS + dy/norm * (CORNER_RADIUS - self.radius)
        
        elif self.y < CORNER_RADIUS and self.x > SCREEN_WIDTH - CORNER_RADIUS:
            # Bottom-right corner
            distance = math.sqrt((self.x - (SCREEN_WIDTH - CORNER_RADIUS))**2 + (self.y - CORNER_RADIUS)**2)
            if distance < CORNER_RADIUS - self.radius:
                # Paddle is within the valid area, no adjustment needed
                pass
            else:
                # Calculate normalized direction from corner center to paddle
                dx = self.x - (SCREEN_WIDTH - CORNER_RADIUS)
                dy = self.y - CORNER_RADIUS
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    # Move paddle to valid position
                    self.x = (SCREEN_WIDTH - CORNER_RADIUS) + dx/norm * (CORNER_RADIUS - self.radius)
                    self.y = CORNER_RADIUS + dy/norm * (CORNER_RADIUS - self.radius)
        
        elif self.y > SCREEN_HEIGHT - CORNER_RADIUS and self.x < CORNER_RADIUS:
            # Top-left corner
            distance = math.sqrt((self.x - CORNER_RADIUS)**2 + (self.y - (SCREEN_HEIGHT - CORNER_RADIUS))**2)
            if distance < CORNER_RADIUS - self.radius:
                # Paddle is within the valid area, no adjustment needed
                pass
            else:
                # Calculate normalized direction from corner center to paddle
                dx = self.x - CORNER_RADIUS
                dy = self.y - (SCREEN_HEIGHT - CORNER_RADIUS)
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    # Move paddle to valid position
                    self.x = CORNER_RADIUS + dx/norm * (CORNER_RADIUS - self.radius)
                    self.y = (SCREEN_HEIGHT - CORNER_RADIUS) + dy/norm * (CORNER_RADIUS - self.radius)
        
        elif self.y > SCREEN_HEIGHT - CORNER_RADIUS and self.x > SCREEN_WIDTH - CORNER_RADIUS:
            # Top-right corner
            distance = math.sqrt((self.x - (SCREEN_WIDTH - CORNER_RADIUS))**2 + (self.y - (SCREEN_HEIGHT - CORNER_RADIUS))**2)
            if distance < CORNER_RADIUS - self.radius:
                # Paddle is within the valid area, no adjustment needed
                pass
            else:
                # Calculate normalized direction from corner center to paddle
                dx = self.x - (SCREEN_WIDTH - CORNER_RADIUS)
                dy = self.y - (SCREEN_HEIGHT - CORNER_RADIUS)
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    # Move paddle to valid position
                    self.x = (SCREEN_WIDTH - CORNER_RADIUS) + dx/norm * (CORNER_RADIUS - self.radius)
                    self.y = (SCREEN_HEIGHT - CORNER_RADIUS) + dy/norm * (CORNER_RADIUS - self.radius)
    
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
        
    def check_collision_with_puck(self, puck, sound=None):
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
            
            # Spawn particles at collision point
            collision_x = puck.x - math.cos(angle) * PUCK_RADIUS
            collision_y = puck.y - math.sin(angle) * PUCK_RADIUS
            particles = utils.spawn_particles(collision_x, collision_y, arcade.color.WHITE, 10)
            
            return True, particles
            
        return False, particles
        
class PowerUp:
    def __init__(self, x=None, y=None, power_type=None):
        # If coordinates or type not specified, generate random ones
        if x is None or y is None:
            # Place in center area
            self.x = random.randint(SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4)
            self.y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        else:
            self.x = x
            self.y = y
            
        if power_type is None:
            power_up_types = ['speed', 'size', 'freeze']
            self.type = random.choice(power_up_types)
        else:
            self.type = power_type
            
        self.radius = 15
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
        elif self.type == 'size':
            # Increase paddle size
            paddle.radius = PADDLE_RADIUS * 1.5
        elif self.type == 'freeze':
            # Freeze opponent briefly
            puck.freeze_opponent = True
            
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