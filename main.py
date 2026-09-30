import pygame

pygame.init()

# === ОКНО ===
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кровавая Луна")
clock = pygame.time.Clock()

# === ФОН (один для всех экранов) ===
background = pygame.image.load("assets/background.PNG")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

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

# === ЦВЕТА ===
PANEL        = (32, 32, 42)
TEXT         = (230, 230, 230)
TEXT_DIM     = (150, 150, 160)
BUTTON       = (60, 60, 80)
BUTTON_HOVER = (90, 90, 120)
BUTTON_DIS   = (40, 40, 50)
POSITIVE     = (100, 220, 120)
NEGATIVE     = (220, 80, 80)
PLAYER1      = (180, 30, 40)

PLAYER_COLORS = [(180, 30, 40), (122, 110, 90), (140, 60, 180), (60, 180, 90)]
PLAYER_NAMES  = ["ВАМПИРЫ", "ОБОРОТНИ", "ВЕДЬМЫ", "ОХОТНИКИ"]

# === ШРИФТЫ ===
FONT_HUGE     = pygame.font.SysFont("arial", 56, bold=True)
FONT_TITLE    = pygame.font.SysFont("arial", 28, bold=True)
FONT_SUB      = pygame.font.SysFont("arial", 22, bold=True)
FONT_RESOURCE = pygame.font.SysFont("arial", 22)
FONT_LOG      = pygame.font.SysFont("arial", 17)
FONT_BUTTON   = pygame.font.SysFont("arial", 22)

# === СОСТОЯНИЯ ЭКРАНА ===
SCREEN_START = "start"
SCREEN_RULES = "rules"
SCREEN_GAME  = "game"
current_screen = SCREEN_START

# === КНОПКИ СТАРТОВОГО ЭКРАНА ===
start_btn = pygame.Rect(WIDTH // 2 - 180, 360, 360, 60)
rules_btn = pygame.Rect(WIDTH // 2 - 180, 440, 360, 60)
back_btn  = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 70, 200, 46)

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
current_action = None

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

continue_rect = pygame.Rect(0, 0, 200, 50)
continue_rect.center = (WIDTH // 2 + 150, 400)

# === СТАРТОВЫЙ ЭКРАН ===
def draw_start(mouse_pos):
    screen.blit(background, (0, 0))

    # затемнение
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    # заголовок
    title = FONT_HUGE.render("КРОВАВАЯ ЛУНА", True, TEXT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))

    # подзаголовок
    sub = FONT_SUB.render("Хроники Четырёх Земель", True, PLAYER1)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 280))

    # кнопка НАЧАТЬ ИГРУ
    color = BUTTON_HOVER if start_btn.collidepoint(mouse_pos) else BUTTON
    pygame.draw.rect(screen, color, start_btn, border_radius=8)
    draw_text_centered(screen, "НАЧАТЬ ИГРУ", start_btn, FONT_BUTTON, TEXT)

    # кнопка ПРАВИЛА
    color = BUTTON_HOVER if rules_btn.collidepoint(mouse_pos) else BUTTON
    pygame.draw.rect(screen, color, rules_btn, border_radius=8)
    draw_text_centered(screen, "ПРАВИЛА", rules_btn, FONT_BUTTON, TEXT)
    
# === ЭКРАН ПРАВИЛ ===
def draw_rules(mouse_pos):
    screen.blit(background, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = FONT_TITLE.render("ПРАВИЛА ИГРЫ", True, TEXT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    pygame.draw.line(screen, PLAYER1, (WIDTH // 2 - 200, 60), (WIDTH // 2 + 200, 60), 2)

    panel = pygame.Rect(60, 80, WIDTH - 120, HEIGHT - 165)
    pygame.draw.rect(screen, PANEL, panel, border_radius=16)

    left_x, right_x = 90, WIDTH // 2 + 15
    y_left, y_right = 100, 100

    def section(x, y, header, lines):
        screen.blit(FONT_SUB.render(header, True, PLAYER1), (x, y))
        yy = y + 28
        for line in lines:
            screen.blit(FONT_LOG.render(line, True, TEXT), (x, yy))
            yy += 20
        return yy + 12

    y_left = section(left_x, y_left, "ЦЕЛЬ ИГРЫ", [
        "Побеждает тот, кто первый наберёт 30 престижа.",
        "Если все выбыли кроме одного — он побеждает.",
        "После 20 ходов — побеждает с макс. престижем.",
    ])
    y_left = section(left_x, y_left, "РЕСУРСЫ (старт)", [
        "Пропитание 10 — еда, влияет на выживание",
        "Деньги 10 — валюта для сделок",
        "Земля 5 — территории, дают доход",
        "Народ 10 — сородичи, стая, ковен, отряд",
        "Смута 0 — безумие, при 10 — смерть",
    ])
    y_left = section(left_x, y_left, "ДОХОД (в начале хода)", [
        "+1 пропитание за каждые 2 земли",
        "+1 деньги за каждые 5 народа",
    ])
    y_left = section(left_x, y_left, "ФОРМУЛА ПРЕСТИЖА", [
        "престиж = земля×2 + деньги//5 + народ//5 − смута",
        "Деление целочисленное.",
    ])

    y_right = section(right_x, y_right, "ДЕЙСТВИЯ (1 за ход)", [
        "Союз −1 пропитание: у обоих −1 смуты (1 ход)",
        "Торговля −3 деньги: +3 пропитания себе",
        "Набег −1 народ: у цели −2 пропитания, +1 смуты",
        "Подкуп −3 деньги: у цели −2 смуты",
        "Раздор −2 деньги: у цели +2 смуты",
    ])
    y_right = section(right_x, y_right, "СОБЫТИЯ (1 за ход, случайно)", [
        "Пожар, Затмение, Эпидемия, Полная луна,",
        "Инквизиция, Травник.",
        "Исход случаен: позитив / негатив (50/50).",
    ])
    y_right = section(right_x, y_right, "ХОД ИГРОКА", [
        "1. Доход с земли и народа.",
        "2. Случайное событие.",
        "3. Действие (+ цель).",
        "4. Пересчёт престижа, проверка смертей и победы.",
    ])
    y_right = section(right_x, y_right, "СМЕРТЬ ИГРОКА", [
        "Смута ≥ 10 — безумие. Народ ≤ 0 — вымирание.",
    ])

    color = BUTTON_HOVER if back_btn.collidepoint(mouse_pos) else BUTTON
    pygame.draw.rect(screen, color, back_btn, border_radius=8)
    draw_text_centered(screen, "← НАЗАД", back_btn, FONT_BUTTON, TEXT)

# === ИГРОВОЙ ЭКРАН ===
def draw_game(mouse_pos, clicked, click_pos):
    global game_state, current_player, turn_number, current_action

    screen.blit(background, (0, 0))

    player = players[current_player]
    player_color = PLAYER_COLORS[current_player]

    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 60))
    pygame.draw.rect(screen, player_color, (0, 60, WIDTH, 6))
    screen.blit(FONT_TITLE.render(f"ХОД: {player['name']}", True, TEXT), (24, 14))
    turn = FONT_RESOURCE.render(f"Ход №{turn_number} / 20", True, TEXT)
    screen.blit(turn, (WIDTH - turn.get_width() - 24, 18))

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

    log_rect = pygame.Rect(20, 170, 400, 400)
    pygame.draw.rect(screen, PANEL, log_rect, border_radius=12)
    screen.blit(FONT_TITLE.render("ЛОГ СОБЫТИЙ", True, TEXT), (40, 190))
    ly = 240
    for msg, color in log_messages:
        screen.blit(FONT_LOG.render(f"> {msg}", True, color), (40, ly))
        ly += 30

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
            if start_btn.collidepoint(click_pos):
                current_screen = SCREEN_GAME
            elif rules_btn.collidepoint(click_pos):
                current_screen = SCREEN_RULES

    elif current_screen == SCREEN_RULES:
        draw_rules(mouse_pos)
        if clicked and back_btn.collidepoint(click_pos):
            current_screen = SCREEN_START

    elif current_screen == SCREEN_GAME:
        draw_game(mouse_pos, clicked, click_pos)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
