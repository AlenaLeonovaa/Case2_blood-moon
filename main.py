import pygame

pygame.init()

# === ОКНО ===
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кровавая Луна")
clock = pygame.time.Clock()

# === ЦВЕТА ===
BG           = (18, 18, 24)
PANEL        = (32, 32, 42)
TEXT         = (230, 230, 230)
TEXT_DIM     = (150, 150, 160)
TEXT_ACCENT  = (180, 30, 40)
BUTTON       = (60, 60, 80)
BUTTON_HOVER = (90, 90, 120)
BUTTON_DIS   = (40, 40, 50)
POSITIVE     = (100, 220, 120)
NEGATIVE     = (220, 80, 80)

PLAYER_COLORS = [(180, 30, 40), (122, 110, 90), (140, 60, 180), (60, 180, 90)]
PLAYER_NAMES  = ["ВАМПИРЫ", "ОБОРОТНИ", "ВЕДЬМЫ", "ОХОТНИКИ"]

# === ШРИФТЫ ===
FONT_HUGE     = pygame.font.SysFont("arial", 48, bold=True)
FONT_TITLE    = pygame.font.SysFont("arial", 28, bold=True)
FONT_SUB      = pygame.font.SysFont("arial", 20, bold=True)
FONT_RESOURCE = pygame.font.SysFont("arial", 22)
FONT_LOG      = pygame.font.SysFont("arial", 17)
FONT_BUTTON   = pygame.font.SysFont("arial", 22)

# === ФОНЫ ===
menu_bg = pygame.image.load("assets/start_bg.png")
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))

game_bg = pygame.image.load("assets/background.png")
game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))

# === ИКОНКИ ===
ICON_SIZE = 32
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

# === СОСТОЯНИЯ ЭКРАНА ===
SCREEN_START = "start"
SCREEN_RULES = "rules"
SCREEN_GAME  = "game"
current_screen = SCREEN_START

# === КНОПКИ СТАРТОВОГО ЭКРАНА (клик-зоны поверх картинки) ===
start_button_rect = pygame.Rect(470, 342, 354, 69)
rules_button_rect = pygame.Rect(470, 427, 354, 69)

# === КНОПКА "НАЗАД" ===
back_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 70, 200, 46)

# === ФЕЙКОВЫЕ ИГРОКИ ===
players = [
    {"name": "ВАМПИРЫ",  "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
    {"name": "ОБОРОТНИ", "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
    {"name": "ВЕДЬМЫ",   "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
    {"name": "ОХОТНИКИ", "food": 10, "money": 10, "land": 5, "people": 10, "smuta": 0, "prestige": 12},
]

current_player = 0
turn_number = 1
log_messages = [("Добро пожаловать!", TEXT)]

STATE_EVENT  = "event"
STATE_ACTION = "action"
STATE_TARGET = "target"
game_state = STATE_EVENT

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

# === ХЕЛПЕРЫ ===
def draw_text_centered(surface, text, rect, font, color):
    surf = font.render(text, True, color)
    x = rect.x + (rect.width - surf.get_width()) // 2
    y = rect.y + (rect.height - surf.get_height()) // 2
    surface.blit(surf, (x, y))

def make_action_buttons():
    buttons = []
    bw, bh, sp = 200, 50, 20
    total = 5 * bw + 4 * sp
    sx = (WIDTH - total) // 2
    for i, action in enumerate(ACTIONS):
        x = sx + i * (bw + sp)
        rect = pygame.Rect(x, 620, bw, bh)
        buttons.append({"rect": rect, "action": action})
    return buttons

def make_target_buttons():
    buttons = []
    bw, bh, sp = 150, 50, 20
    others = [i for i in range(4) if i != current_player]
    total = 3 * bw + 2 * sp
    sx = (WIDTH - total) // 2
    for i, target_idx in enumerate(others):
        x = sx + i * (bw + sp)
        rect = pygame.Rect(x, 620, bw, bh)
        buttons.append({"rect": rect, "target": target_idx})
    return buttons

def add_log(msg, color=TEXT):
    log_messages.insert(0, (msg, color))
    if len(log_messages) > 5:
        log_messages.pop()

action_buttons = make_action_buttons()

# === КНОПКА "ПРОДОЛЖИТЬ" ===
continue_rect = pygame.Rect(0, 0, 200, 50)
continue_rect.center = (WIDTH // 2 + 150, 400)

# ===== ОТРИСОВКА: СТАРТОВЫЙ ЭКРАН =====
def draw_start(mouse_pos):
    screen.blit(menu_bg, (0, 0))
    if start_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (220, 60, 60), start_button_rect, 2, border_radius=8)
    if rules_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (200, 200, 210), rules_button_rect, 2, border_radius=8)

# ===== ОТРИСОВКА: ЭКРАН ПРАВИЛ =====
def draw_rules(mouse_pos):
    screen.fill(BG)
    title = FONT_HUGE.render("ПРАВИЛА ИГРЫ", True, TEXT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 25))
    pygame.draw.line(screen, TEXT_ACCENT, (WIDTH // 2 - 200, 92), (WIDTH // 2 + 200, 92), 2)

    panel = pygame.Rect(60, 115, WIDTH - 120, HEIGHT - 200)
    pygame.draw.rect(screen, PANEL, panel, border_radius=16)

    left_x, right_x = 100, WIDTH // 2 + 20
    y_left, y_right = 145, 145

    def section(x, y, header, lines):
        screen.blit(FONT_SUB.render(header, True, TEXT_ACCENT), (x, y))
        yy = y + 32
        for line in lines:
            screen.blit(FONT_LOG.render(line, True, TEXT), (x, yy))
            yy += 22
        return yy + 16

    y_left = section(left_x, y_left, "ЦЕЛЬ ИГРЫ", [
        "Набрать 30 престижа ИЛИ остаться",
        "последним с смутой < 10 и народом > 0.",
    ])
    y_left = section(left_x, y_left, "РЕСУРСЫ (стартовые)", [
        "Пропитание 10 — еда, влияет на выживание",
        "Деньги 10 — валюта для торговли",
        "Земля 5 — территории, дают доход",
        "Народ 10 — население и армия",
        "Смута 0 — негативный ресурс, при 10 — проигрыш",
    ])
    y_left = section(left_x, y_left, "ФОРМУЛА ПРЕСТИЖА", [
        "престиж = земля×2 + деньги//5 + народ//5 − смута",
    ])

    y_right = section(right_x, y_right, "ДЕЙСТВИЯ (1 за ход)", [
        "Союз — −1 пропитание, у обоих −1 смуты",
        "Торговля — −3 деньги, +3 пропитания (без цели)",
        "Набег — −1 народ, у цели −2 пропитания, +1 смуты",
        "Подкуп — −3 деньги, у цели −2 смуты",
        "Раздор — −2 деньги, у цели +2 смуты",
    ])
    y_right = section(right_x, y_right, "СОБЫТИЯ (1 за ход)", [
        "6 случайных: Пожар, Затмение, Эпидемия,",
        "Полная луна, Инквизиция, Травник.",
        "Исход — случайный: позитив / негатив (50/50).",
    ])
    y_right = section(right_x, y_right, "ХОД ИГРОКА", [
        "1. Случайное событие.",
        "2. Управляемое действие.",
        "3. Переход хода к следующему игроку.",
    ])

    hover = back_button_rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER if hover else BUTTON
    pygame.draw.rect(screen, color, back_button_rect, border_radius=8)
    draw_text_centered(screen, "← НАЗАД", back_button_rect, FONT_BUTTON, TEXT)

# ===== ОТРИСОВКА: ИГРОВОЙ ЭКРАН =====
def draw_game(mouse_pos, clicked, click_pos):
    global game_state, current_player, turn_number, current_action

    screen.blit(game_bg, (0, 0))

    player = players[current_player]
    player_color = PLAYER_COLORS[current_player]

    # HEADER
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 60))
    pygame.draw.rect(screen, player_color, (0, 60, WIDTH, 6))
    title = FONT_TITLE.render(f"ХОД: {player['name']}", True, TEXT)
    screen.blit(title, (24, 14))
    turn = FONT_RESOURCE.render(f"Ход №{turn_number} / 20", True, TEXT)
    screen.blit(turn, (WIDTH - turn.get_width() - 24, 18))

    # РЕСУРСЫ
    pygame.draw.rect(screen, PANEL, (0, 66, WIDTH, 80))
    resources = [
        ("food",     "Пропитание", player["food"]),
        ("money",    "Деньги",     player["money"]),
        ("land",     "Земля",      player["land"]),
        ("people",   "Народ",      player["people"]),
        ("smuta",    "Смута",      player["smuta"]),
        ("prestige", "Престиж",    player["prestige"]),
    ]
    rx = 60
    for key, label, value in resources:
        screen.blit(icons[key], (rx, 82))
        color = NEGATIVE if (key == "smuta" and value >= 7) else TEXT
        screen.blit(FONT_RESOURCE.render(str(value), True, color), (rx + ICON_SIZE + 10, 84))
        screen.blit(FONT_LOG.render(label, True, TEXT_DIM), (rx, 118))
        rx += 190

    # ЛОГ
    log_rect = pygame.Rect(20, 170, 400, 400)
    pygame.draw.rect(screen, PANEL, log_rect, border_radius=12)
    screen.blit(FONT_TITLE.render("ЛОГ СОБЫТИЙ", True, TEXT), (40, 190))
    ly = 240
    for msg, color in log_messages:
        screen.blit(FONT_LOG.render(f"> {msg}", True, color), (40, ly))
        ly += 30

    # СОСТОЯНИЕ: СОБЫТИЕ
    if game_state == STATE_EVENT:
        event_rect = pygame.Rect(540, 170, 500, 300)
        pygame.draw.rect(screen, PANEL, event_rect, border_radius=12)
        ev_title = FONT_TITLE.render(event["title"], True, TEXT)
        screen.blit(ev_title, (event_rect.centerx - ev_title.get_width() // 2, 230))
        ev_effect = FONT_RESOURCE.render(event["effect"], True, NEGATIVE)
        screen.blit(ev_effect, (event_rect.centerx - ev_effect.get_width() // 2, 300))
        pygame.draw.rect(screen, BUTTON, continue_rect, border_radius=8)
        draw_text_centered(screen, "Продолжить", continue_rect, FONT_BUTTON, TEXT)
        if clicked and continue_rect.collidepoint(click_pos):
            game_state = STATE_ACTION

    # СОСТОЯНИЕ: ВЫБОР ДЕЙСТВИЯ
    elif game_state == STATE_ACTION:
        for btn in action_buttons:
            hover = btn["rect"].collidepoint(mouse_pos)
            afford = can_afford(player, btn["action"])
            color = BUTTON_DIS if not afford else (BUTTON_HOVER if hover else BUTTON)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
            draw_text_centered(screen, btn["action"]["title"], btn["rect"], FONT_BUTTON, TEXT)
        hint = FONT_RESOURCE.render("Выберите действие", True, TEXT)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 580))
        if clicked:
            for btn in action_buttons:
                if btn["rect"].collidepoint(click_pos) and can_afford(player, btn["action"]):
                    action = btn["action"]
                    if action["target"]:
                        current_action = action
                        game_state = STATE_TARGET
                    else:
                        add_log(f"{player['name']}: {action['title']}", TEXT)
                        current_player = (current_player + 1) % 4
                        turn_number += 1
                        game_state = STATE_EVENT
                    break

    # СОСТОЯНИЕ: ВЫБОР ЦЕЛИ
    elif game_state == STATE_TARGET:
        hint = FONT_RESOURCE.render(f"Выберите цель для «{current_action['title']}»", True, TEXT)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 580))
        target_buttons = make_target_buttons()
        for btn in target_buttons:
            t = btn["target"]
            hover = btn["rect"].collidepoint(mouse_pos)
            color = PLAYER_COLORS[t]
            if hover:
                color = tuple(min(c + 40, 255) for c in color)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
            draw_text_centered(screen, PLAYER_NAMES[t], btn["rect"], FONT_LOG, TEXT)
        if clicked:
            for btn in target_buttons:
                if btn["rect"].collidepoint(click_pos):
                    target = btn["target"]
                    add_log(f"{player['name']} → {current_action['title']} → {PLAYER_NAMES[target]}", TEXT)
                    current_player = (current_player + 1) % 4
                    turn_number += 1
                    game_state = STATE_EVENT
                    break

# === ГЛАВНЫЙ ЦИКЛ ===
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
            if start_button_rect.collidepoint(click_pos):
                current_screen = SCREEN_GAME
            elif rules_button_rect.collidepoint(click_pos):
                current_screen = SCREEN_RULES

    elif current_screen == SCREEN_RULES:
        draw_rules(mouse_pos)
        if clicked and back_button_rect.collidepoint(click_pos):
            current_screen = SCREEN_START

    elif current_screen == SCREEN_GAME:
        draw_game(mouse_pos, clicked, click_pos)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
