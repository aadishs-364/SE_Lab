"""
GameEngine: owns all balloons, spawns new ones, and handles clicks.

Starter version: one balloon type (random size, fixed points), no
lives system yet, no timer yet. Click detection also has a known bug
(see game/click_detection.py) that Task 1 asks you to fix.
"""

import random

from game.balloon import Balloon, BALLOON_TYPES
from game.click_detection import check_pop
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 45
# Spawn odds per balloon type: mostly normal, some bonus, some penalty.
TYPE_WEIGHTS = {"normal": 70, "bonus": 15, "penalty": 15}
STARTING_LIVES = 3


class GameEngine:
    def __init__(self):
        self.balloons = []
        self.frames_until_spawn = 0
        self.score = 0
        self.lives = STARTING_LIVES
        self.game_over = False

    def _spawn_balloon(self):
        radius = random.randint(16, 44)
        x = random.randint(radius + 10, WIDTH - radius - 10)
        speed = random.uniform(1.5, 3.0)
        kind = random.choices(list(TYPE_WEIGHTS), weights=TYPE_WEIGHTS.values())[0]
        self.balloons.append(Balloon(x=x, y=-radius, radius=radius, speed=speed, kind=kind))

    def handle_click(self, pos):
        if self.game_over:
            return
        popped = check_pop(self.balloons, pos)
        if popped is not None:
            self.balloons.remove(popped)
            self.score += popped.points   # normal +10, bonus +30, penalty -20; never costs a life

    def update(self):
        if self.game_over:
            return

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_balloon()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for b in self.balloons:
            b.update()

        # Every balloon that escapes off the bottom costs one life.
        escaped = [b for b in self.balloons if b.is_past_bottom(HEIGHT)]
        if escaped:
            self.balloons = [b for b in self.balloons if not b.is_past_bottom(HEIGHT)]
            self.lives = max(0, self.lives - len(escaped))
            if self.lives == 0:
                self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.balloons)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}/{STARTING_LIVES}", (10, 36), (200, 40, 60))
        renderer.draw_legend(surface, font, BALLOON_TYPES)

        if self.game_over:
            renderer.draw_banner(surface, font, f"Game Over! Final score: {self.score}")
