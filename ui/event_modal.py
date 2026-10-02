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
    for en, ru in RU_NAMES.items():
        text = text.replace(en, ru)
    return text


def wrap_text(text, font, max_width):
    """Разбивает текст на строки по ширине."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_event_modal(screen, event, mouse_pos, continue_rect, fonts):
    """Рисует карточку события.

    event: dict с полями title, effect, phrase, story.
    """
    W, H = screen.get_size()

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    card_w, card_h = 900, 520
    card = pygame.Rect(W // 2 - card_w // 2, H // 2 - card_h // 2 - 30, card_w, card_h)

    surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
    surf.fill((28, 28, 38, 250))
    screen.blit(surf, (card.x, card.y))

    pygame.draw.rect(screen, COLORS["player1"], card, 3, border_radius=16)
    pygame.draw.rect(screen, (220, 80, 80), card.inflate(-8, -8), 1, border_radius=14)

    # Фраза сверху
    phrase = event.get("phrase", "")
    if phrase:
        phrase_surf = fonts["phrase"].render(phrase, True, (200, 200, 210))
        screen.blit(phrase_surf,
                    (card.centerx - phrase_surf.get_width() // 2, card.y + 25))

    # Название события
    title = fonts["event_title"].render(event["title"], True, COLORS["text"])
    screen.blit(title, (card.centerx - title.get_width() // 2, card.y + 60))

    # Линия
    pygame.draw.line(screen, COLORS["player1"],
                     (card.centerx - 250, card.y + 130),
                     (card.centerx + 250, card.y + 130), 2)

    # История
    story = event.get("story", "")
    y = card.y + 150
    if story:
        lines = wrap_text(story, fonts["story"], card.width - 80)
        for line in lines:
            line_surf = fonts["story"].render(line, True, (220, 220, 230))
            screen.blit(line_surf,
                        (card.centerx - line_surf.get_width() // 2, y))
            y += 26
        y += 20

    # Эффекты
    effect_str = event["effect"]
    if effect_str:
        parts = effect_str.split(": ", 1)
        effects_text = parts[1] if len(parts) == 2 else effect_str
        pieces = [p.strip() for p in effects_text.split(",")]

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
            y += 45

    # Кнопка
    hover = continue_rect.collidepoint(mouse_pos)
    color = COLORS["button_hover"] if hover else COLORS["button"]
    pygame.draw.rect(screen, color, continue_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS["player1"], continue_rect, 2, border_radius=8)

    btn_text = fonts["button"].render("ПРОДОЛЖИТЬ", True, COLORS["text"])
    bx = continue_rect.x + (continue_rect.width - btn_text.get_width()) // 2
    by = continue_rect.y + (continue_rect.height - btn_text.get_height()) // 2
    screen.blit(btn_text, (bx, by))

def draw_result_modal(screen, result_text, mouse_pos, continue_rect, fonts):
    """Модалка результата действия — компактнее и по центру."""
    W, H = screen.get_size()

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    card_w, card_h = 700, 280
    card = pygame.Rect(W // 2 - card_w // 2, H // 2 - card_h // 2, card_w, card_h)

    # Фон
    surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
    surf.fill((24, 24, 32, 250))
    screen.blit(surf, (card.x, card.y))

    # Рамка цвета активного игрока
    pygame.draw.rect(screen, COLORS["player1"], card, 3, border_radius=16)
    pygame.draw.rect(screen, (200, 60, 60), card.inflate(-8, -8), 1, border_radius=14)

    # Заголовок
    title = fonts["title"].render("ДЕЙСТВИЕ СОВЕРШЕНО", True, COLORS["player1"])
    screen.blit(title, (card.centerx - title.get_width() // 2, card.y + 30))

    # Разделитель
    pygame.draw.line(screen, COLORS["player1"],
                     (card.centerx - 200, card.y + 85),
                     (card.centerx + 200, card.y + 85), 2)

    # Текст результата — переведённый
    ru_text = translate(result_text)
    lines = wrap_text(ru_text, fonts["resource"], card.width - 80)
    y = card.y + 110
    for line in lines:
        surf_text = fonts["resource"].render(line, True, COLORS["text"])
        screen.blit(surf_text, (card.centerx - surf_text.get_width() // 2, y))
        y += 30

    # Кнопка
    hover = continue_rect.collidepoint(mouse_pos)
    color = COLORS["button_hover"] if hover else COLORS["button"]
    pygame.draw.rect(screen, color, continue_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS["player1"], continue_rect, 2, border_radius=8)

    btn_text = fonts["button"].render("ПРОДОЛЖИТЬ", True, COLORS["text"])
    bx = continue_rect.x + (continue_rect.width - btn_text.get_width()) // 2
    by = continue_rect.y + (continue_rect.height - btn_text.get_height()) // 2
    screen.blit(btn_text, (bx, by))
