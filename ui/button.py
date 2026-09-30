"""Класс кнопки."""
import pygame

from config import COLORS


class Button:
    """Кнопка с hover-эффектом и обработкой клика."""

    def __init__(self, rect, text, font, border_color=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.border_color = border_color
        self.hover = False

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = COLORS["button_hover"] if self.hover else COLORS["button"]
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=8)
        surf = self.font.render(self.text, True, COLORS["text"])
        x = self.rect.x + (self.rect.width - surf.get_width()) // 2
        y = self.rect.y + (self.rect.height - surf.get_height()) // 2
        screen.blit(surf, (x, y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
