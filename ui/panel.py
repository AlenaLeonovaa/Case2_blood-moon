"""Панели игрового экрана: header, карточки фракций, лог."""
import pygame

from config import (
    COLORS, WINDOW_WIDTH, MAX_TURNS,
    LOG_MAX_MESSAGES, ICON_SIZE,
)


RU_NAMES = {
    "food":   "еда",
    "money":  "деньги",
    "land":   "земля",
    "people": "народ",
    "smuta":  "смута",
}


def translate(text):
    """Переводит английские ключи ресурсов в русские."""
    for en, ru in RU_NAMES.items():
        text = text.replace(en, ru)
    return text


# === HEADER ===
def draw_header(screen, player_name, player_color, turn_number, fonts):
    """Рисует верхнюю панель с именем игрока и номером хода."""
    pygame.draw.rect(screen, COLORS["panel"], (0, 0, WINDOW_WIDTH, 60))
    pygame.draw.rect(screen, player_color, (0, 60, WINDOW_WIDTH, 6))

    title = fonts["title"].render(f"ХОД: {player_name}", True, COLORS["text"])
    screen.blit(title, (24, 14))

    turn = fonts["resource"].render(
        f"Ход №{turn_number} / {MAX_TURNS}", True, COLORS["text"],
    )
    screen.blit(turn, (WINDOW_WIDTH - turn.get_width() - 24, 18))


# === КАРТОЧКА ФРАКЦИИ ===
def draw_player_card(screen, player, rect, is_active, icons_small, fonts):
    """Рисует карточку одной фракции.

    Args:
        player: объект Player.
        rect: pygame.Rect — область карточки.
        is_active: bool — чей сейчас ход.
        icons_small: dict — уменьшенные иконки 24×24.
    """
    color = COLORS.get(player.color_key, COLORS["text"])

    # Фон: активная — светлее
    bg_alpha = 240 if is_active else 180
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    surf.fill((40, 40, 52, bg_alpha) if is_active else (28, 28, 36, bg_alpha))
    screen.blit(surf, (rect.x, rect.y))

    # Рамка: активная — 3px её цвета, пассивная — 1px серым
    border = color if is_active else (60, 60, 80)
    border_width = 3 if is_active else 1
    pygame.draw.rect(screen, border, rect, border_width, border_radius=10)

    # Затемнение для мёртвых
    if player.is_dead:
        dead_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        dead_surf.fill((0, 0, 0, 160))
        screen.blit(dead_surf, (rect.x, rect.y))
        dead_text = fonts["title"].render("ВЫБЫЛ", True, COLORS["negative"])
        screen.blit(dead_text, (
            rect.centerx - dead_text.get_width() // 2,
            rect.centery - dead_text.get_height() // 2,
        ))
        return

    # Заголовок
    title = fonts["sub"].render(player.name, True, color)
    screen.blit(title, (rect.x + 12, rect.y + 8))

    # Ресурсы в 2 колонки по 3 строки
    rows = [
        [("food", player.food),       ("money", player.money)],
        [("land", player.land),       ("people", player.people)],
        [("smuta", player.smuta),     ("prestige", player.prestige)],
    ]

    col_w = (rect.width - 24) // 2
    for ri, row in enumerate(rows):
        for ci, (key, value) in enumerate(row):
            x = rect.x + 12 + ci * col_w
            y = rect.y + 40 + ri * 36

            # Иконка
            screen.blit(icons_small[key], (x, y))

            # Число
            color_val = COLORS["text"]
            if key == "smuta" and value >= 7:
                color_val = COLORS["negative"]
            elif key == "smuta" and value == 0:
                color_val = COLORS["positive"]

            val_surf = fonts["resource_small"].render(str(value), True, color_val)
            screen.blit(val_surf, (x + 28, y + 4))


# === ПАНЕЛЬ 4 ФРАКЦИЙ ===
def draw_players_panel(screen, players, current_index, icons_small, fonts):
    """Рисует 4 карточки фракций в ряд."""
    y_top = 66
    card_height = 160
    padding = 16
    card_width = (WINDOW_WIDTH - padding * 5) // 4

    for i, player in enumerate(players):
        x = padding + i * (card_width + padding)
        rect = pygame.Rect(x, y_top + padding, card_width, card_height)
        draw_player_card(screen, player, rect, i == current_index,
                         icons_small, fonts)


# === ЛОГ ===
def draw_log_panel(screen, messages, fonts):
    """Рисует лог событий."""
    log_rect = pygame.Rect(20, 260, WINDOW_WIDTH - 40, 300)
    pygame.draw.rect(screen, COLORS["panel"], log_rect, border_radius=12)

    header = fonts["title"].render("ЛОГ СОБЫТИЙ", True, COLORS["text"])
    screen.blit(header, (40, 275))

    ly = 320
    for msg in messages:
        ru_msg = translate(msg)

        has_plus = "+" in msg
        has_minus = "−" in msg or "-" in msg

        if has_plus and not has_minus:
            color = COLORS["positive"]
        elif has_minus:
            color = COLORS["negative"]
        else:
            color = COLORS["text"]

        line = fonts["log"].render(f"> {ru_msg}", True, color)
        screen.blit(line, (40, ly))
        ly += 32

def get_player_card_rects():
    """Возвращает список pygame.Rect — координаты 4 карточек фракций."""
    y_top = 66
    card_height = 220
    padding = 16
    card_width = (WINDOW_WIDTH - padding * 5) // 4
    rects = []
    for i in range(4):
        x = padding + i * (card_width + padding)
        rects.append(pygame.Rect(x, y_top + padding, card_width, card_height))
    return rects
