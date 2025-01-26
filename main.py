import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALL_SPEED = 5

class AirHockeyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Air Hockey")
        self.ball_x = SCREEN_WIDTH // 2
        self.ball_y = SCREEN_HEIGHT // 2
        self.ball_dx = BALL_SPEED
        self.ball_dy = BALL_SPEED

    def on_draw(self):
        arcade.start_render()
        arcade.draw_circle_filled(self.ball_x, self.ball_y, 15, arcade.color.WHITE)
        arcade.draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLUE, 5)

    def update(self, delta_time):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Bounce the ball off the walls
        if self.ball_x < 15 or self.ball_x > SCREEN_WIDTH - 15:
            self.ball_dx *= -1
        if self.ball_y < 15 or self.ball_y > SCREEN_HEIGHT - 15:
            self.ball_dy *= -1

if __name__ == "__main__":
    game = AirHockeyGame()
    arcade.run()
