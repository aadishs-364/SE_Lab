"""Self-check for the four lab tasks. Run: python test_game.py"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from game.balloon import Balloon
from game.click_detection import check_pop
from game.game_engine import GameEngine, ROUND_FRAMES, STARTING_LIVES
from game.renderer import HEIGHT

# Task 1: a click near the visible edge pops; a click just outside does not.
b = Balloon(x=100, y=100, radius=30, speed=0)
assert check_pop([b], (100 + 28, 100)) is b
assert check_pop([b], (100 + 20, 100 + 20)) is b      # diagonal, distance ~28
assert check_pop([b], (100 + 32, 100)) is None

# Task 2: each type changes the score by its own amount; popping never costs a life.
e = GameEngine()
for kind, delta in [("normal", 10), ("bonus", 30), ("penalty", -20)]:
    e.balloons = [Balloon(x=200, y=200, radius=30, speed=0, kind=kind)]
    before = e.score
    e.handle_click((210, 205))
    assert e.score - before == delta, kind
assert e.lives == STARTING_LIVES

# Task 3: each escaped balloon costs a life; game over at zero.
e = GameEngine()
e.frames_until_spawn = 10**9
for expected in (2, 1, 0):
    e.balloons = [Balloon(x=200, y=HEIGHT + 100, radius=20, speed=0)]
    e.update()
    assert e.lives == expected
assert e.game_over and e.end_reason == "Out of lives!"

# Task 4: round ends after 30 s, stops accepting clicks, and R resets everything.
e = GameEngine()
e.frames_until_spawn = 10**9
for _ in range(ROUND_FRAMES):
    e.update()
assert e.game_over and e.end_reason == "Time's up!"
e.balloons = [Balloon(x=200, y=200, radius=30, speed=0)]
e.handle_click((200, 200))
assert e.score == 0, "clicks must be ignored after the round ends"
e.score, e.lives = 99, 1
e.handle_keydown(pygame.K_r)
assert (e.score, e.lives, e.frames_left, e.game_over) == (0, STARTING_LIVES, ROUND_FRAMES, False)

# Smoke test: render a full round headlessly.
pygame.init()
screen = pygame.display.set_mode((700, 500))
font = pygame.font.SysFont("consolas", 22)
e = GameEngine()
for _ in range(ROUND_FRAMES + 10):
    e.update()
    e.draw(screen, font)

print("All lab task checks passed.")
