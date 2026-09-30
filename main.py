"""Точка входа игры «Кровавая Луна»."""
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLORS,
    FONT_TITLE_SIZE, FONT_RESOURCE_SIZE, FONT_LOG_SIZE,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING,
    TARGET_BUTTON_WIDTH, TARGET_BUTTON_HEIGHT,
    LOG_MAX_MESSAGES, ICON_SIZE,
)
from ui.panel import draw_header, draw_resources_panel, draw_log_panel
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

# === ШРИФТЫ ===
fonts = {
    "huge":     pygame.font.SysFont("arial", 56, bold=True),
    "title":    pygame.font.SysFont("arial", FONT_TITLE_SIZE, bold=True),
    "sub":      pygame.font.SysFont("arial", 22, bold=True),
    "resource": pygame.font.SysFont("arial", FONT_RESOURCE_SIZE),
    "log":      pygame.font.SysFont("arial", FONT_LOG_SIZE),
    "button":   pygame.font.SysFont("arial", 22),
}

# === ЦВЕТА ФРАКЦИЙ ===
PLAYER_COLORS = [COLORS["player1"], COLORS["player2"], COLORS["player3"], COLORS["player4"]]
PLAYER_NAMES = ["ВАМПИРЫ", "ОБОРОТНИ", "ВЕДЬМЫ", "ОХОТНИКИ"]

# === СОСТОЯНИЯ ЭКРАНА ===
SCREEN_START = "start"
SCREEN_LORE  = "lore"
SCREEN_RULES = "rules"
SCREEN_GAME  = "game"
current_screen = SCREEN_START

# === ФЕЙКОВЫЕ ИГРОКИ ===
players = [
    {"name": "ВАМПИРЫ",  "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
    {"name": "ОБОРОТНИ", "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
    {"name": "ВЕДЬМЫ",   "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
    {"name": "ОХОТНИКИ", "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
]

current_player = 0
turn_number = 1
log_messages = [("Добро пожаловать!", COLORS["text"])]

# === СОСТОЯНИЯ ХОДА ===
STATE_EVENT  = "event"
STATE_ACTION = "action"
STATE_TARGET = "target"
game_state = STATE_EVENT

# === ДЕЙСТВИЯ ===
ACTIONS = [
    {"id": "alliance", "title": "Союз",     "cost": {"food": 1},   "target": True},
    {"id": "trade",    "title": "Торговля", "cost": {"money": 3},  "target": False},
    {"id": "raid",     "title": "Набег",    "cost": {"people": 1}, "target": True},
    {"id": "bribe",    "title": "Подкуп",   "cost": {"money": 3},  "target": True},
    {"id": "discord",  "title": "Раздор",   "cost": {"money": 2},  "target": True},
]

def can_afford(player, action):
    return all(player[res] >= cost for res, cost in action["cost"].items())

event = {"title": "ПОЖАР", "effect": "−3 food, −1 land"}
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


def make_action_buttons():
    buttons = []
    total = 5 * BUTTON_WIDTH + 4 * BUTTON_SPACING
    sx = (WINDOW_WIDTH - total) // 2
    for i, action in enumerate(ACTIONS):
        x = sx + i * (BUTTON_WIDTH + BUTTON_SPACING)
        rect = pygame.Rect(x, 620, BUTTON_WIDTH, BUTTON_HEIGHT)
        buttons.append({"rect": rect, "action": action})
    return buttons


def make_target_buttons():
    buttons = []
    others = [i for i in range(4) if i != current_player]
    total = 3 * TARGET_BUTTON_WIDTH + 2 * BUTTON_SPACING
    sx = (WINDOW_WIDTH - total) // 2
    for i, target_idx in enumerate(others):
        x = sx + i * (TARGET_BUTTON_WIDTH + BUTTON_SPACING)
        rect = pygame.Rect(x, 620, TARGET_BUTTON_WIDTH, TARGET_BUTTON_HEIGHT)
        buttons.append({"rect": rect, "target": target_idx})
    return buttons


def add_log(msg, color=None):
    if color is None:
        color = COLORS["text"]
    log_messages.insert(0, (msg, color))
    if len(log_messages) > LOG_MAX_MESSAGES:
        log_messages.pop()


action_buttons = make_action_buttons()

continue_rect = pygame.Rect(0, 0, 200, 50)
continue_rect.center = (WINDOW_WIDTH // 2 + 150, 400)

start_btn_rect  = pygame.Rect(WINDOW_WIDTH // 2 - 180, 360, 360, 60)
rules_btn_rect  = pygame.Rect(WINDOW_WIDTH // 2 - 180, 440, 360, 60)
back_btn_rect   = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 70, 200, 46)
lore_continue_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 80, 300, 50)


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

    # Заголовок
    title = fonts["huge"].render("ЛЕГЕНДА", True, COLORS["text"])
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))

    # Двойная линия
    pygame.draw.line(screen, COLORS["player1"],
                     (WINDOW_WIDTH // 2 - 260, 105),
                     (WINDOW_WIDTH // 2 + 260, 105), 3)
    pygame.draw.line(screen, (220, 80, 80),
                     (WINDOW_WIDTH // 2 - 200, 111),
                     (WINDOW_WIDTH // 2 + 200, 111), 1)

    # Панель
    panel = pygame.Rect(140, 135, WINDOW_WIDTH - 280, 470)
    surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    surf.fill((20, 20, 28, 220))
    screen.blit(surf, (panel.x, panel.y))
    pygame.draw.rect(screen, COLORS["player1"], panel, 2, border_radius=16)

    # Текст — единый шрифт, без выделений
    y = 170
    for line in LORE_LINES:
        if line:
            surf_text = fonts["log"].render(line, True, COLORS["text"])
            screen.blit(surf_text,
                        (WINDOW_WIDTH // 2 - surf_text.get_width() // 2, y))
        y += 28

    # Кнопка
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
    global game_state, current_player, turn_number, current_action

    screen.blit(background, (0, 0))

    player = players[current_player]
    player_color = PLAYER_COLORS[current_player]

    draw_header(screen, player["name"], player_color, turn_number, fonts)
    draw_resources_panel(screen, player, icons, fonts)
    draw_log_panel(screen, log_messages, fonts)

    if game_state == STATE_EVENT:
        draw_event_modal(screen, event, mouse_pos, continue_rect, fonts)
        if clicked and continue_rect.collidepoint(click_pos):
            game_state = STATE_ACTION

    elif game_state == STATE_ACTION:
        for btn in action_buttons:
            hover = btn["rect"].collidepoint(mouse_pos)
            afford = can_afford(player, btn["action"])
            if not afford:
                color = COLORS["disabled"]
            elif hover:
                color = COLORS["button_hover"]
            else:
                color = COLORS["button"]
            pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
            draw_text_centered(screen, btn["action"]["title"], btn["rect"],
                               fonts["button"], COLORS["text"])

        hint = fonts["resource"].render("Выберите действие", True, COLORS["text"])
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 580))

        if clicked:
            for btn in action_buttons:
                if btn["rect"].collidepoint(click_pos) and can_afford(player, btn["action"]):
                    action = btn["action"]
                    if action["target"]:
                        current_action = action
                        game_state = STATE_TARGET
                    else:
                        add_log(f"{player['name']}: {action['title']}")
                        current_player = (current_player + 1) % 4
                        turn_number += 1
                        game_state = STATE_EVENT
                    break

    elif game_state == STATE_TARGET:
        hint = fonts["resource"].render(
            f"Выберите цель для «{current_action['title']}»", True, COLORS["text"],
        )
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 580))

        target_buttons = make_target_buttons()
        for btn in target_buttons:
            t = btn["target"]
            hover = btn["rect"].collidepoint(mouse_pos)
            color = PLAYER_COLORS[t]
            if hover:
                color = tuple(min(c + 40, 255) for c in color)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
            draw_text_centered(screen, PLAYER_NAMES[t], btn["rect"],
                               fonts["log"], COLORS["text"])

        if clicked:
            for btn in target_buttons:
                if btn["rect"].collidepoint(click_pos):
                    target = btn["target"]
                    add_log(f"{player['name']} → {current_action['title']} → {PLAYER_NAMES[target]}")
                    current_player = (current_player + 1) % 4
                    turn_number += 1
                    game_state = STATE_EVENT
                    break


# === ГЛАВНЫЙ ЦИКЛ ===
def main():
    global current_screen
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

        elif current_screen == SCREEN_RULES:
            draw_rules(mouse_pos)
            if clicked and back_btn_rect.collidepoint(click_pos):
                current_screen = SCREEN_START

        elif current_screen == SCREEN_GAME:
            draw_game(mouse_pos, clicked, click_pos)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
