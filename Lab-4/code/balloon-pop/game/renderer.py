"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (200, 230, 245)
COLOR_TEXT = (30, 30, 30)


def draw_scene(surface, balloons):
    surface.fill(COLOR_BG)
    for b in balloons:
        pygame.draw.circle(surface, b.color, (int(b.x), int(b.y)), b.radius)
        pygame.draw.line(surface, (120, 120, 120), (b.x, b.y + b.radius), (b.x, b.y + b.radius + 12), 2)
        # Mark special balloons with +/- so they're readable without relying on color alone.
        if b.kind != "normal":
            pygame.draw.line(surface, (255, 255, 255), (b.x - 6, b.y), (b.x + 6, b.y), 3)
        if b.kind == "bonus":
            pygame.draw.line(surface, (255, 255, 255), (b.x, b.y - 6), (b.x, b.y + 6), 3)


def draw_legend(surface, font, types):
    """Small key in the top-right showing each balloon color and its points."""
    x = surface.get_width() - 150
    for i, (kind, (points, color)) in enumerate(types.items()):
        y = 14 + i * 24
        pygame.draw.circle(surface, color, (x, y + 8), 8)
        draw_text(surface, font, f"{kind} {points:+d}", (x + 14, y))


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, lines):
    """Centered panel with one or more lines of text (used for the end-of-round screen)."""
    w, h = surface.get_width(), surface.get_height()
    panel = pygame.Rect(0, 0, w - 120, 40 + 32 * len(lines))
    panel.center = (w // 2, h // 2)
    pygame.draw.rect(surface, (255, 255, 255), panel, border_radius=10)
    pygame.draw.rect(surface, (180, 40, 40), panel, width=3, border_radius=10)
    for i, line in enumerate(lines):
        surf = font.render(line, True, (180, 40, 40))
        surface.blit(surf, surf.get_rect(center=(w // 2, panel.top + 36 + 32 * i)))
