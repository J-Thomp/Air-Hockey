# Air Hockey
# Created by J-Thomp

import arcade
import math
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Air Hockey"

PADDLE_RADIUS = 30
PUCK_RADIUS = 20
PADDLE_SPEED = 5
FRICTION = 0.99
WALL_BOUNCE_DAMPING = 0.8

# Goal constants
GOAL_WIDTH = 200
GOAL_HEIGHT = 20

class AirHockeyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)

        # Player paddles
        self.player1_paddle = None
        self.player2_paddle = None
        
        # Puck
        self.puck = None
        
        # Scores
        self.player1_score = 0
        self.player2_score = 0

    def setup(self):
        # Create player paddles
        self.player1_paddle = {
            'x': SCREEN_WIDTH // 4,
            'y': SCREEN_HEIGHT // 2,
            'dx': 0,
            'dy': 0
        }
        
        self.player2_paddle = {
            'x': 3 * SCREEN_WIDTH // 4,
            'y': SCREEN_HEIGHT // 2,
            'dx': 0,
            'dy': 0
        }
        
        # Create puck
        self.puck = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'dx': 0,
            'dy': 0
        }
        
        # Reset scores
        self.player1_score = 0
        self.player2_score = 0

    def on_draw(self):
        self.clear()
        
        # Draw court
        arcade.draw_lrbt_rectangle_outline(
            left=0, 
            right=SCREEN_WIDTH, 
            top=SCREEN_HEIGHT, 
            bottom=0, 
            color=arcade.color.BLACK, 
            border_width=4
        )
        
        # Draw center line
        arcade.draw_line(
            SCREEN_WIDTH // 2, 
            0, 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT, 
            arcade.color.BLACK, 
            2
        )
        
        # Draw center circle
        arcade.draw_circle_outline(
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2, 
            100, 
            arcade.color.BLACK, 
            2
        )
        
        # Draw goal areas
        # Player 1 goal (left side)
        arcade.draw_lrbt_rectangle_outline(
            left=0, 
            right=GOAL_WIDTH, 
            top=SCREEN_HEIGHT // 2 + GOAL_HEIGHT // 2, 
            bottom=SCREEN_HEIGHT // 2 - GOAL_HEIGHT // 2, 
            color=arcade.color.RED,
            border_width=4
        )
        
        # Player 2 goal (right side)
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH - GOAL_WIDTH, 
            right=SCREEN_WIDTH, 
            top=SCREEN_HEIGHT // 2 + GOAL_HEIGHT // 2, 
            bottom=SCREEN_HEIGHT // 2 - GOAL_HEIGHT // 2, 
            color=arcade.color.LIGHT_BLUE,
            border_width=4
        )
        
        # Draw paddles
        arcade.draw_circle_filled(
            self.player1_paddle['x'], 
            self.player1_paddle['y'], 
            PADDLE_RADIUS, 
            arcade.color.RED
        )
        
        arcade.draw_circle_filled(
            self.player2_paddle['x'], 
            self.player2_paddle['y'], 
            PADDLE_RADIUS, 
            arcade.color.BLUE
        )
        
        # Draw puck
        arcade.draw_circle_filled(
            self.puck['x'], 
            self.puck['y'], 
            PUCK_RADIUS, 
            arcade.color.BLACK
        )
        
        # Draw scores
        arcade.draw_text(
            f"Player 1: {self.player1_score}", 
            10, 
            SCREEN_HEIGHT - 30, 
            arcade.color.BLACK, 
            20
        )
        
        arcade.draw_text(
            f"Player 2: {self.player2_score}", 
            SCREEN_WIDTH - 150, 
            SCREEN_HEIGHT - 30, 
            arcade.color.BLACK, 
            20
        )

    def on_update(self, delta_time):
        # Move paddles
        self.player1_paddle['x'] += self.player1_paddle['dx']
        self.player1_paddle['y'] += self.player1_paddle['dy']
        self.player2_paddle['x'] += self.player2_paddle['dx']
        self.player2_paddle['y'] += self.player2_paddle['dy']

        # Constrain paddles to screen
        self.player1_paddle['x'] = max(PADDLE_RADIUS, 
            min(SCREEN_WIDTH // 2 - PADDLE_RADIUS, 
                self.player1_paddle['x']))
        self.player1_paddle['y'] = max(PADDLE_RADIUS, 
            min(SCREEN_HEIGHT - PADDLE_RADIUS, 
                self.player1_paddle['y']))
        
        self.player2_paddle['x'] = max(SCREEN_WIDTH // 2 + PADDLE_RADIUS, 
            min(SCREEN_WIDTH - PADDLE_RADIUS, 
                self.player2_paddle['x']))
        self.player2_paddle['y'] = max(PADDLE_RADIUS, 
            min(SCREEN_HEIGHT - PADDLE_RADIUS, 
                self.player2_paddle['y']))

        # Move puck
        self.puck['x'] += self.puck['dx']
        self.puck['y'] += self.puck['dy']
        
        # Apply friction to puck
        self.puck['dx'] *= FRICTION
        self.puck['dy'] *= FRICTION
        
        # Puck wall collision
        if (self.puck['x'] - PUCK_RADIUS <= 0 or 
            self.puck['x'] + PUCK_RADIUS >= SCREEN_WIDTH):
            self.puck['dx'] *= -WALL_BOUNCE_DAMPING
        
        if (self.puck['y'] - PUCK_RADIUS <= 0 or 
            self.puck['y'] + PUCK_RADIUS >= SCREEN_HEIGHT):
            self.puck['dy'] *= -WALL_BOUNCE_DAMPING
        
        # Check for goals
        self.check_goals()
        
        # Paddle-puck collision
        self.handle_paddle_puck_collision(
            self.player1_paddle, self.player2_paddle
        )

    def on_key_press(self, key, modifiers):
        # Player 1 controls (WASD)
        if key == arcade.key.W:
            self.player1_paddle['dy'] = PADDLE_SPEED
        elif key == arcade.key.S:
            self.player1_paddle['dy'] = -PADDLE_SPEED
        elif key == arcade.key.A:
            self.player1_paddle['dx'] = -PADDLE_SPEED
        elif key == arcade.key.D:
            self.player1_paddle['dx'] = PADDLE_SPEED
        
        # Player 2 controls (Arrow keys)
        elif key == arcade.key.UP:
            self.player2_paddle['dy'] = PADDLE_SPEED
        elif key == arcade.key.DOWN:
            self.player2_paddle['dy'] = -PADDLE_SPEED
        elif key == arcade.key.LEFT:
            self.player2_paddle['dx'] = -PADDLE_SPEED
        elif key == arcade.key.RIGHT:
            self.player2_paddle['dx'] = PADDLE_SPEED

    def on_key_release(self, key, modifiers):
        # Stop movement when key is released
        if key in (arcade.key.W, arcade.key.S):
            self.player1_paddle['dy'] = 0
        elif key in (arcade.key.A, arcade.key.D):
            self.player1_paddle['dx'] = 0
        
        if key in (arcade.key.UP, arcade.key.DOWN):
            self.player2_paddle['dy'] = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player2_paddle['dx'] = 0

    def handle_paddle_puck_collision(self, *paddles):
        for paddle in paddles:
            # Calculate distance between paddle and puck
            dx = self.puck['x'] - paddle['x']
            dy = self.puck['y'] - paddle['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            # Check for collision
            if distance <= PADDLE_RADIUS + PUCK_RADIUS:
                # Calculate collision angle
                angle = math.atan2(dy, dx)
                
                # Transfer momentum
                speed = math.sqrt(
                    self.puck['dx']**2 + self.puck['dy']**2
                )
                
                # Reflect puck with additional paddle velocity
                self.puck['dx'] = (
                    math.cos(angle) * speed * 1.2 + 
                    paddle['dx'] * 0.5
                )
                self.puck['dy'] = (
                    math.sin(angle) * speed * 1.2 + 
                    paddle['dy'] * 0.5
                )

    def check_goals(self):
        # Check for goals
        GOAL_TOP = SCREEN_HEIGHT // 2 + GOAL_HEIGHT // 2
        GOAL_BOTTOM = SCREEN_HEIGHT // 2 - GOAL_HEIGHT // 2
        
        if (self.puck['x'] <= GOAL_WIDTH and 
            GOAL_BOTTOM <= self.puck['y'] <= GOAL_TOP):
            # Player 2 scores
            self.player2_score += 1
            self.reset_puck()
        
        elif (self.puck['x'] >= SCREEN_WIDTH - GOAL_WIDTH and 
              GOAL_BOTTOM <= self.puck['y'] <= GOAL_TOP):
            # Player 1 scores
            self.player1_score += 1
            self.reset_puck()

    def reset_puck(self):
        # Reset puck to center with random initial velocity
        self.puck = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3)
        }

def main():
    window = AirHockeyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()