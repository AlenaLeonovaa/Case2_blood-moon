"""Панели игрового экрана: header, ресурсы, лог."""
import pygame

from config import (
    COLORS, WINDOW_WIDTH, MAX_TURNS,
    LOG_MAX_MESSAGES, ICON_SIZE,
)


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


def draw_resources_panel(screen, player, icons, fonts):
    """Рисует панель с 6 ресурсами (объект Player)."""
    y_top = 66
    pygame.draw.rect(screen, COLORS["panel"], (0, y_top, WINDOW_WIDTH, 80))

    resources = [
        ("food",     "Пропитание", player.food),
        ("money",    "Деньги",     player.money),
        ("land",     "Земля",      player.land),
        ("people",   "Народ",      player.people),
        ("smuta",    "Смута",      player.smuta),
        ("prestige", "Престиж",    player.prestige),
    ]

    rx = 60
    for key, label, value in resources:
        screen.blit(icons[key], (rx, y_top + 16))
        color = COLORS["negative"] if (key == "smuta" and value >= 7) else COLORS["text"]
        val_surf = fonts["resource"].render(str(value), True, color)
        screen.blit(val_surf, (rx + ICON_SIZE + 10, y_top + 18))
        label_surf = fonts["log"].render(label, True, (150, 150, 160))
        screen.blit(label_surf, (rx, y_top + 52))
        rx += 190

def draw_log_panel(screen, messages, fonts):
    """Рисует панель лога событий. messages — список строк."""
    log_rect = pygame.Rect(20, 170, 400, 400)
    pygame.draw.rect(screen, COLORS["panel"], log_rect, border_radius=12)

    header = fonts["title"].render("ЛОГ СОБЫТИЙ", True, COLORS["text"])
    screen.blit(header, (40, 190))

    ly = 240
    for msg in messages:
        # Автоопределение цвета по содержимому
        if "+" in msg and "−" not in msg and "-" not in msg:
            color = COLORS["positive"]
        elif "−" in msg or "-" in msg:
            color = COLORS["negative"]
        else:
            color = COLORS["text"]

        line = fonts["log"].render(f"> {msg}", True, color)
        screen.blit(line, (40, ly))
        ly += 30
