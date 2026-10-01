"""Модальное окно случайного события."""
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
    """Переводит английские ключи ресурсов в русские названия."""
    for en, ru in RU_NAMES.items():
        text = text.replace(en, ru)
    return text


def draw_event_modal(screen, event, mouse_pos, continue_rect, fonts):
    """Рисует карточку события. Плюсы — зелёным, минусы — красным."""
    event_rect = pygame.Rect(540, 170, 500, 300)
    pygame.draw.rect(screen, COLORS["panel"], event_rect, border_radius=12)

    # Заголовок
    ev_title = fonts["title"].render(event["title"], True, COLORS["text"])
    screen.blit(ev_title, (event_rect.centerx - ev_title.get_width() // 2, 220))

    # Разбор строки эффекта
    effect_str = event["effect"]  # например "Пожар: −3 food, −1 land"
    parts = effect_str.split(": ", 1)
    effects_text = parts[1] if len(parts) == 2 else effect_str

    pieces = [p.strip() for p in effects_text.split(",")]

    # Рисуем каждую часть отдельно, с цветом по знаку
    y = 290
    for piece in pieces:
        ru_piece = translate(piece)
        if "−" in piece or "-" in piece:
            color = COLORS["negative"]
        elif "+" in piece:
            color = COLORS["positive"]
        else:
            color = COLORS["text"]

        surf = fonts["resource"].render(ru_piece, True, color)
        screen.blit(surf, (event_rect.centerx - surf.get_width() // 2, y))
        y += 34

    # Кнопка «Продолжить»
    hover = continue_rect.collidepoint(mouse_pos)
    color = COLORS["button_hover"] if hover else COLORS["button"]
    pygame.draw.rect(screen, color, continue_rect, border_radius=8)

    surf = fonts["button"].render("Продолжить", True, COLORS["text"])
    x = continue_rect.x + (continue_rect.width - surf.get_width()) // 2
    yy = continue_rect.y + (continue_rect.height - surf.get_height()) // 2
    screen.blit(surf, (x, yy))
