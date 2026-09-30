"""Модальное окно случайного события."""
import pygame

from config import COLORS

def draw_event_modal(screen, event, mouse_pos, continue_rect, fonts):
    """Рисует карточку события с кнопкой «Продолжить»."""
    event_rect = pygame.Rect(540, 170, 500, 300)
    pygame.draw.rect(screen, COLORS["panel"], event_rect, border_radius=12)

    ev_title = fonts["title"].render(event["title"], True, COLORS["text"])
    screen.blit(ev_title, (event_rect.centerx - ev_title.get_width() // 2, 230))

    ev_effect = fonts["resource"].render(event["effect"], True, COLORS["negative"])
    screen.blit(ev_effect, (event_rect.centerx - ev_effect.get_width() // 2, 300))

    hover = continue_rect.collidepoint(mouse_pos)
    color = COLORS["button_hover"] if hover else COLORS["button"]
    pygame.draw.rect(screen, color, continue_rect, border_radius=8)

    surf = fonts["button"].render("Продолжить", True, COLORS["text"])
    x = continue_rect.x + (continue_rect.width - surf.get_width()) // 2
    y = continue_rect.y + (continue_rect.height - surf.get_height()) // 2
    screen.blit(surf, (x, y))
