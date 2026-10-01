"""Модальное окно случайного события — большая карточка."""
import pygame

from config import COLORS


RU_NAMES = {
    "food":   "еда",
    "money":  "деньги",
    "land":   "земля",
    "people": "народ",
    "smuta":  "смута",
}


def translate(text):
    for en, ru in RU_NAMES.items():
        text = text.replace(en, ru)
    return text


def draw_event_modal(screen, event, mouse_pos, continue_rect, fonts):
    """Рисует большую карточку события по центру."""
    W, H = screen.get_size()

    # Затемнение фона
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Карточка
    card_w, card_h = 900, 500
    card = pygame.Rect(W // 2 - card_w // 2, H // 2 - card_h // 2 - 30, card_w, card_h)

    # Фон карточки
    surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
    surf.fill((28, 28, 38, 250))
    screen.blit(surf, (card.x, card.y))

    # Рамка (красная)
    pygame.draw.rect(screen, COLORS["player1"], card, 3, border_radius=16)
    pygame.draw.rect(screen, (220, 80, 80), card.inflate(-8, -8), 1, border_radius=14)

    # Заголовок
    title = fonts["event_title"].render(event["title"], True, COLORS["text"])
    screen.blit(title, (card.centerx - title.get_width() // 2, card.y + 50))

    # Линия под заголовком
    pygame.draw.line(screen, COLORS["player1"],
                     (card.centerx - 250, card.y + 130),
                     (card.centerx + 250, card.y + 130), 2)

    # Разбор эффекта
    effect_str = event["effect"]
    parts = effect_str.split(": ", 1)
    effects_text = parts[1] if len(parts) == 2 else effect_str
    pieces = [p.strip() for p in effects_text.split(",")]

    # Эффекты крупно, по центру
    y = card.y + 180
    for piece in pieces:
        ru_piece = translate(piece)
        if "−" in piece or "-" in piece:
            color = COLORS["negative"]
            prefix = "▼"
        elif "+" in piece:
            color = COLORS["positive"]
            prefix = "▲"
        else:
            color = COLORS["text"]
            prefix = "●"

        surf_text = fonts["event_effect"].render(f"{prefix}  {ru_piece}", True, color)
        screen.blit(surf_text, (card.centerx - surf_text.get_width() // 2, y))
        y += 60

    # Кнопка
    hover = continue_rect.collidepoint(mouse_pos)
    color = COLORS["button_hover"] if hover else COLORS["button"]
    pygame.draw.rect(screen, color, continue_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS["player1"], continue_rect, 2, border_radius=8)

    btn_text = fonts["button"].render("ПРОДОЛЖИТЬ", True, COLORS["text"])
    bx = continue_rect.x + (continue_rect.width - btn_text.get_width()) // 2
    by = continue_rect.y + (continue_rect.height - btn_text.get_height()) // 2
    screen.blit(btn_text, (bx, by))
