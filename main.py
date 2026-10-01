"""Точка входа игры «Кровавая Луна»."""
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLORS,
    FONT_TITLE_SIZE, FONT_RESOURCE_SIZE, FONT_LOG_SIZE,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING,
    TARGET_BUTTON_WIDTH, TARGET_BUTTON_HEIGHT,
    LOG_MAX_MESSAGES, ICON_SIZE,
)
from logic.game_state import GameState
from logic.events_pool import ACTIONS
from ui.panel import draw_header, draw_players_panel, draw_log_panel
from ui.event_modal import draw_event_modal


# === ИНИЦИАЛИЗАЦИЯ ===
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Кровавая Луна")
clock = pygame.time.Clock()

# === ФОН ===
background = pygame.image.load("assets/background.PNG")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

# === ИКОНКИ ===
def load_icon(name):
    img = pygame.image.load(f"assets/icon_{name}.png").convert_alpha()
    return pygame.transform.smoothscale(img, (ICON_SIZE, ICON_SIZE))

icons = {
    "food":     load_icon("food"),
    "money":    load_icon("money"),
    "land":     load_icon("land"),
    "people":   load_icon("people"),
    "smuta":    load_icon("smuta"),
    "prestige": load_icon("prestige"),
}

# Маленькие иконки 24×24 для карточек фракций
icons_small = {
    key: pygame.transform.smoothscale(img, (24, 24))
    for key, img in icons.items()
}

# === ШРИФТЫ ===
fonts = {
    "huge":           pygame.font.SysFont("arial", 56, bold=True),
    "title":          pygame.font.SysFont("arial", FONT_TITLE_SIZE, bold=True),
    "sub":            pygame.font.SysFont("arial", 22, bold=True),
    "resource":       pygame.font.SysFont("arial", FONT_RESOURCE_SIZE),
    "resource_small": pygame.font.SysFont("arial", 18),
    "log":            pygame.font.SysFont("arial", FONT_LOG_SIZE),
    "button":         pygame.font.SysFont("arial", 22),
    "event_title":    pygame.font.SysFont("arial", 44, bold=True),
    "event_effect":   pygame.font.SysFont("arial", 28, bold=True),
}

# === СОСТОЯНИЯ ЭКРАНА ===
SCREEN_START = "start"
SCREEN_LORE  = "lore"
SCREEN_RULES = "rules"
SCREEN_GAME  = "game"
SCREEN_OVER  = "over"
current_screen = SCREEN_START

# === ИГРА ===
state = GameState()

# === СОСТОЯНИЯ ХОДА ===
STATE_EVENT  = "event"
STATE_ACTION = "action"
STATE_TARGET = "target"
game_state = STATE_EVENT

# Текущее событие (для модалки)
current_event = None
current_event_log = ""

# Выбранное действие (для STATE_TARGET)
current_action = None


# === ХЕЛПЕРЫ ===
def draw_text_centered(surface, text, rect, font, color):
    surf = font.render(text, True, color)
    x = rect.x + (rect.width - surf.get_width()) // 2
    y = rect.y + (rect.height - surf.get_height()) // 2
    surface.blit(surf, (x, y))


def draw_panel(rect, alpha=200, border_color=None):
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    surf.fill((32, 32, 42, alpha))
    screen.blit(surf, (rect.x, rect.y))
    if border_color:
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=16)
    else:
        pygame.draw.rect(screen, (60, 60, 80), rect, 2, border_radius=16)


def get_player_color(player):
    """Возвращает RGB-цвет игрока по его color_key."""
    return COLORS.get(player.color_key, COLORS["text"])


def make_action_buttons():
    buttons = []
    total = len(ACTIONS) * BUTTON_WIDTH + (len(ACTIONS) - 1) * BUTTON_SPACING
    sx = (WINDOW_WIDTH - total) // 2
    for i, action in enumerate(ACTIONS):
        x = sx + i * (BUTTON_WIDTH + BUTTON_SPACING)
        rect = pygame.Rect(x, 620, BUTTON_WIDTH, BUTTON_HEIGHT)
        buttons.append({"rect": rect, "action": action})
    return buttons


def make_target_buttons():
    buttons = []
    others = [p for p in state.players if p is not state.current_player and not p.is_dead]
    if not others:
        return buttons
    total = len(others) * TARGET_BUTTON_WIDTH + (len(others) - 1) * BUTTON_SPACING
    sx = (WINDOW_WIDTH - total) // 2
    for i, target in enumerate(others):
        x = sx + i * (TARGET_BUTTON_WIDTH + BUTTON_SPACING)
        rect = pygame.Rect(x, 620, TARGET_BUTTON_WIDTH, TARGET_BUTTON_HEIGHT)
        buttons.append({"rect": rect, "target": target})
    return buttons


action_buttons = make_action_buttons()

# Кнопка «Продолжить» в модалке события
continue_rect = pygame.Rect(0, 0, 300, 60)
continue_rect.center = (WINDOW_WIDTH // 2, 580)

# Кнопки экранов
start_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 180, 360, 360, 60)
rules_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 180, 440, 360, 60)
back_btn_rect  = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 70, 200, 46)
lore_continue_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 80, 300, 50)
over_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 120, 300, 50)


# === СТАРТОВЫЙ ЭКРАН ===
def draw_start(mouse_pos):
    screen.blit(background, (0, 0))
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    screen.blit(overlay, (0, 0))

    title = fonts["huge"].render("КРОВАВАЯ ЛУНА", True, COLORS["text"])
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
    pygame.draw.line(screen, COLORS["player1"],
                     (WINDOW_WIDTH // 2 - 260, 280),
                     (WINDOW_WIDTH // 2 + 260, 280), 3)
    sub = fonts["sub"].render("Хроники Четырёх Земель", True, (200, 200, 210))
    screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 295))

    color = COLORS["button_hover"] if start_btn_rect.collidepoint(mouse_pos) else COLORS["button"]
    pygame.draw.rect(screen, color, start_btn_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS["player1"], start_btn_rect, 2, border_radius=8)
    draw_text_centered(screen, "НАЧАТЬ ИГРУ", start_btn_rect, fonts["button"], COLORS["text"])

    color = COLORS["button_hover"] if rules_btn_rect.collidepoint(mouse_pos) else COLORS["button"]
    pygame.draw.rect(screen, color, rules_btn_rect, border_radius=8)
    pygame.draw.rect(screen, (60, 60, 80), rules_btn_rect, 2, border_radius=8)
    draw_text_centered(screen, "ПРАВИЛА", rules_btn_rect, fonts["button"], COLORS["text"])


# === ЭКРАН ЛЕГЕНДЫ ===
LORE_LINES = [
    "Много веков четыре могущественные фракции",
    "скрывались во тьме.",
    "",
    "Вампиры  •  Оборотни  •  Ведьмы  •  Охотники",
    "",
    "Но в ночь Кровавой Луны древний баланс",
    "был разрушен.",
    "",
    "Каждое королевство стремится захватить земли,",
    "укрепить власть и пережить наступление врагов.",
    "",
    "Но Луна не прощает слабости.",
    "Только одна фракция станет хозяином нового мира.",
]


def draw_lore(mouse_pos):
    screen.blit(background, (0, 0))
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = fonts["huge"].render("ЛЕГЕНДА", True, COLORS["text"])
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))

    pygame.draw.line(screen, COLORS["player1"],
                     (WINDOW_WIDTH // 2 - 260, 105),
                     (WINDOW_WIDTH // 2 + 260, 105), 3)
    pygame.draw.line(screen, (220, 80, 80),
                     (WINDOW_WIDTH // 2 - 200, 111),
                     (WINDOW_WIDTH // 2 + 200, 111), 1)

    panel = pygame.Rect(140, 135, WINDOW_WIDTH - 280, 470)
    surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    surf.fill((20, 20, 28, 220))
    screen.blit(surf, (panel.x, panel.y))
    pygame.draw.rect(screen, COLORS["player1"], panel, 2, border_radius=16)

    y = 170
    for line in LORE_LINES:
        if line:
            surf_text = fonts["log"].render(line, True, COLORS["text"])
            screen.blit(surf_text,
                        (WINDOW_WIDTH // 2 - surf_text.get_width() // 2, y))
        y += 28

    color = COLORS["button_hover"] if lore_continue_rect.collidepoint(mouse_pos) else COLORS["button"]
    pygame.draw.rect(screen, color, lore_continue_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS["player1"], lore_continue_rect, 2, border_radius=8)
    draw_text_centered(screen, "ПРОДОЛЖИТЬ", lore_continue_rect,
                       fonts["button"], COLORS["text"])


# === ЭКРАН ПРАВИЛ ===
def draw_rules(mouse_pos):
    screen.blit(background, (0, 0))
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = fonts["huge"].render("ПРАВИЛА", True, COLORS["text"])
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 18))
    pygame.draw.line(screen, COLORS["player1"],
                     (WINDOW_WIDTH // 2 - 220, 82),
                     (WINDOW_WIDTH // 2 + 220, 82), 3)

    left_panel  = pygame.Rect(40, 105, WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 205)
    right_panel = pygame.Rect(WINDOW_WIDTH // 2 + 20, 105, WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 205)
    draw_panel(left_panel, alpha=210, border_color=(60, 60, 80))
    draw_panel(right_panel, alpha=210, border_color=(60, 60, 80))

    left_x, right_x = 70, WINDOW_WIDTH // 2 + 50
    y_left, y_right = 130, 130

    def section(x, y, header, lines):
        pygame.draw.rect(screen, COLORS["player1"], (x - 12, y + 4, 4, 20))
        screen.blit(fonts["sub"].render(header, True, COLORS["text"]), (x, y))
        yy = y + 30
        for line in lines:
            screen.blit(fonts["log"].render(line, True, (200, 200, 210)), (x, yy))
            yy += 20
        return yy + 14

    y_left = section(left_x, y_left, "ЦЕЛЬ ИГРЫ", [
        "Первый набрал 30 престижа — победил.",
        "Остался последним живым — победил.",
        "После 20 ходов — побеждает с макс. престижем.",
    ])
    y_left = section(left_x, y_left, "РЕСУРСЫ (старт)", [
        "Пропитание 10 — еда, влияет на выживание",
        "Деньги 10 — валюта для сделок",
        "Земля 5 — территории, дают доход",
        "Народ 10 — сородичи, стая, ковен, отряд",
        "Смута 0 — безумие, при 10 — смерть",
    ])
    y_left = section(left_x, y_left, "ДОХОД В НАЧАЛЕ ХОДА", [
        "+1 пропитание за каждые 2 земли",
        "+1 деньги за каждые 5 народа",
    ])
    y_left = section(left_x, y_left, "ФОРМУЛА ПРЕСТИЖА", [
        "земля×2 + деньги//5 + народ//5 − смута",
    ])

    y_right = section(right_x, y_right, "ДЕЙСТВИЯ", [
        "Союз: −1 еда, обоим −1 смуты",
        "Торговля: −3 деньги, +3 еды",
        "Набег: −1 народ, у цели −2 еды, +1 смуты",
        "Подкуп: −3 деньги, у цели −2 смуты",
        "Раздор: −2 деньги, у цели +2 смуты",
    ])
    y_right = section(right_x, y_right, "СОБЫТИЯ (случайные)", [
        "Пожар, Затмение, Эпидемия,",
        "Полная луна, Инквизиция, Травник.",
        "Исход 50/50: позитив или негатив.",
    ])
    y_right = section(right_x, y_right, "ХОД ИГРОКА", [
        "1. Доход с земли и народа.",
        "2. Случайное событие.",
        "3. Действие (+ цель).",
        "4. Пересчёт престижа, проверка смертей.",
    ])
    y_right = section(right_x, y_right, "СМЕРТЬ ИГРОКА", [
        "Смута ≥ 10 — безумие.",
        "Народ ≤ 0 — вымирание.",
    ])

    color = COLORS["button_hover"] if back_btn_rect.collidepoint(mouse_pos) else COLORS["button"]
    pygame.draw.rect(screen, color, back_btn_rect, border_radius=8)
    pygame.draw.rect(screen, (60, 60, 80), back_btn_rect, 2, border_radius=8)
    draw_text_centered(screen, "← НАЗАД", back_btn_rect, fonts["button"], COLORS["text"])


# === ИГРОВОЙ ЭКРАН ===
def draw_game(mouse_pos, clicked, click_pos):
    global game_state, current_event, current_event_log, current_action

    screen.blit(background, (0, 0))

    player = state.current_player
    player_color = get_player_color(player)

    # Заголовок + 4 карточки фракций + лог
    draw_header(screen, player.name, player_color, state.turn, fonts)
    draw_players_panel(screen, state.players, state.current, icons_small, fonts)
    draw_log_panel(screen, state.log, fonts)

    if game_state == STATE_EVENT:
        event_dict = {
            "title": current_event.title if current_event else "СОБЫТИЕ",
            "effect": current_event_log,
        }
        draw_event_modal(screen, event_dict, mouse_pos, continue_rect, fonts)
        if clicked and continue_rect.collidepoint(click_pos):
            game_state = STATE_ACTION

    elif game_state == STATE_ACTION:
        for btn in action_buttons:
            hover = btn["rect"].collidepoint(mouse_pos)
            afford = player.can_afford(btn["action"].cost)
            if not afford:
                color = COLORS["disabled"]
            elif hover:
                color = COLORS["button_hover"]
            else:
                color = COLORS["button"]
            pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
            draw_text_centered(screen, btn["action"].title, btn["rect"],
                               fonts["button"], COLORS["text"])

        hint = fonts["resource"].render("Выберите действие", True, COLORS["text"])
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 580))

        if clicked:
            for btn in action_buttons:
                if btn["rect"].collidepoint(click_pos) and player.can_afford(btn["action"].cost):
                    action = btn["action"]
                    if action.target_required:
                        current_action = action
                        game_state = STATE_TARGET
                    else:
                        state.apply_action(action, target=None)
                        state.check_deaths()
                        state.check_winner()
                        if state.is_game_over:
                            current_screen_global()
                        else:
                            state.next_turn()
                            start_new_turn()
                    break

    elif game_state == STATE_TARGET:
        hint = fonts["resource"].render(
            f"Выберите цель для «{current_action.title}»", True, COLORS["text"],
        )
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 580))

        target_buttons = make_target_buttons()
        for btn in target_buttons:
            target = btn["target"]
            hover = btn["rect"].collidepoint(mouse_pos)
            color = get_player_color(target)
            if hover:
                color = tuple(min(c + 40, 255) for c in color)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
            draw_text_centered(screen, target.name, btn["rect"],
                               fonts["log"], COLORS["text"])

        if clicked:
            for btn in target_buttons:
                if btn["rect"].collidepoint(click_pos):
                    state.apply_action(current_action, btn["target"])
                    state.check_deaths()
                    state.check_winner()
                    if state.is_game_over:
                        current_screen_global()
                    else:
                        state.next_turn()
                        start_new_turn()
                    break


def start_new_turn():
    """Начинает новый ход: доход + событие."""
    global current_event, current_event_log, game_state
    event, is_positive, log_message = state.start_turn()
    current_event = event
    current_event_log = log_message
    game_state = STATE_EVENT


# === ЭКРАН ПОБЕДЫ/ПОРАЖЕНИЯ ===
def draw_game_over(mouse_pos):
    screen.blit(background, (0, 0))
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    if state.winner:
        title = fonts["huge"].render("ПОБЕДА!", True, COLORS["positive"])
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))

        name = fonts["title"].render(f"{state.winner.name}", True, get_player_color(state.winner))
        screen.blit(name, (WINDOW_WIDTH // 2 - name.get_width() // 2, 300))

        prest = fonts["resource"].render(
            f"Престиж: {state.winner.prestige}", True, COLORS["text"])
        screen.blit(prest, (WINDOW_WIDTH // 2 - prest.get_width() // 2, 350))
    else:
        title = fonts["huge"].render("ИГРА ОКОНЧЕНА", True, COLORS["text"])
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))

    color = COLORS["button_hover"] if over_btn_rect.collidepoint(mouse_pos) else COLORS["button"]
    pygame.draw.rect(screen, color, over_btn_rect, border_radius=8)
    pygame.draw.rect(screen, COLORS["player1"], over_btn_rect, 2, border_radius=8)
    draw_text_centered(screen, "ИГРАТЬ СНОВА", over_btn_rect, fonts["button"], COLORS["text"])


def current_screen_global():
    """Переключает на экран победы."""
    global current_screen
    current_screen = SCREEN_OVER


# === ГЛАВНЫЙ ЦИКЛ ===
def main():
    global current_screen, game_state

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        click_pos = (0, 0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                clicked = True
                click_pos = e.pos

        if current_screen == SCREEN_START:
            draw_start(mouse_pos)
            if clicked:
                if start_btn_rect.collidepoint(click_pos):
                    current_screen = SCREEN_LORE
                elif rules_btn_rect.collidepoint(click_pos):
                    current_screen = SCREEN_RULES

        elif current_screen == SCREEN_LORE:
            draw_lore(mouse_pos)
            if clicked and lore_continue_rect.collidepoint(click_pos):
                current_screen = SCREEN_GAME
                start_new_turn()

        elif current_screen == SCREEN_RULES:
            draw_rules(mouse_pos)
            if clicked and back_btn_rect.collidepoint(click_pos):
                current_screen = SCREEN_START

        elif current_screen == SCREEN_GAME:
            draw_game(mouse_pos, clicked, click_pos)

        elif current_screen == SCREEN_OVER:
            draw_game_over(mouse_pos)
            if clicked and over_btn_rect.collidepoint(click_pos):
                state.__init__()
                game_state = STATE_EVENT
                current_screen = SCREEN_START

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
