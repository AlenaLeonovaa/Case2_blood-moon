"""Точка входа игры «Кровавая Луна»."""
import math
import random
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLORS,
    FONT_TITLE_SIZE, FONT_RESOURCE_SIZE, FONT_LOG_SIZE,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING,
    TARGET_BUTTON_WIDTH, TARGET_BUTTON_HEIGHT,
    LOG_MAX_MESSAGES, ICON_SIZE, MAX_TURNS, WIN_PRESTIGE,
)
from logic.game_state import GameState
from logic.events_pool import ACTIONS
from ui.panel import draw_header, draw_players_panel, get_player_card_rects
from ui.event_modal import draw_event_modal, draw_result_modal
from ui.event_texts import get_phrase, get_story
from ui.floating import FloatingText, snapshot, diff


# === ИНИЦИАЛИЗАЦИЯ ===
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Кровавая Луна")
clock = pygame.time.Clock()

# === ФОНЫ ===
background = pygame.image.load("assets/background.JPG")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

game_background = pygame.image.load("assets/game_background.jpeg")
game_background = pygame.transform.scale(game_background, (WINDOW_WIDTH, WINDOW_HEIGHT))

# === МУЗЫКА ===
def play_music(filename, volume=0.4):
    try:
        pygame.mixer.music.load(f"assets/music/{filename}")
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

play_music("menu_music.mp3")

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

icons_small = {
    key: pygame.transform.smoothscale(img, (24, 24))
    for key, img in icons.items()
}

# Корона для экрана победы
crown_img = pygame.image.load("assets/icon_crown.png").convert_alpha()
crown_img = pygame.transform.smoothscale(crown_img, (96, 96))

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
    "phrase":         pygame.font.SysFont("arial", 20, italic=True),
    "story":          pygame.font.SysFont("arial", 20),
    "floating":       pygame.font.SysFont("arial", 26, bold=True),
    "win_name":       pygame.font.SysFont("arial", 64, bold=True),
    "win_sub":        pygame.font.SysFont("arial", 26, bold=True),
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
STATE_RESULT = "result"
game_state = STATE_ACTION

# Данные текущего события
current_event = None
current_event_log = ""
current_event_phrase = ""
current_event_story = ""

# Результат действия
action_result_log = ""

# Выбранное действие
current_action = None

# Всплывающие цифры
floating_texts = []

# Хронология: последнее действие
last_action_text = ""


# === СИСТЕМА ЧАСТИЦ ДЛЯ САЛЮТА ===
FIREWORK_COLORS = [
    (255, 215, 0),
    (220, 60, 60),
    (180, 100, 220),
    (100, 220, 120),
    (255, 140, 60),
]

firework_particles = []
firework_timer = [0.0]


def spawn_firework(x, y):
    color = random.choice(FIREWORK_COLORS)
    count = random.randint(40, 60)
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)
        lifetime = random.uniform(0.8, 1.6)
        firework_particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "color": color,
            "age": 0.0,
            "lifetime": lifetime,
            "size": random.randint(2, 4),
        })


def update_fireworks(dt):
    firework_timer[0] += dt
    if firework_timer[0] >= 0.9:
        firework_timer[0] = 0.0
        spawn_firework(random.randint(200, 1080), random.randint(80, 320))

    for p in firework_particles[:]:
        p["age"] += dt
        p["x"] += p["vx"] * dt * 60
        p["y"] += p["vy"] * dt * 60
        p["vy"] += 0.15 * dt * 60
        if p["age"] >= p["lifetime"]:
            firework_particles.remove(p)


def draw_fireworks(surface):
    for p in firework_particles:
        alpha = max(0, int(255 * (1 - p["age"] / p["lifetime"])))
        size = max(1, int(p["size"] * (1 - p["age"] / p["lifetime"])))
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*p["color"], alpha), (size, size), size)
        surface.blit(surf, (int(p["x"] - size), int(p["y"] - size)))


def clear_fireworks():
    firework_particles.clear()
    firework_timer[0] = 0.0


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
    return COLORS.get(player.color_key, COLORS["text"])


def make_action_buttons():
    buttons = []
    total = len(ACTIONS) * BUTTON_WIDTH + (len(ACTIONS) - 1) * BUTTON_SPACING
    sx = (WINDOW_WIDTH - total) // 2
    for i, action in enumerate(ACTIONS):
        x = sx + i * (BUTTON_WIDTH + BUTTON_SPACING)
        rect = pygame.Rect(x, 600, BUTTON_WIDTH, 70)
        buttons.append({"rect": rect, "action": action, "hover_anim": 0.0})
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


# === ВСПЛЫВАЮЩИЕ ЦИФРЫ ===
RU_SHORT = {
    "food":   "ед",
    "money":  "дн",
    "land":   "зм",
    "people": "нр",
    "smuta":  "см",
}


def capture_all():
    return {i: snapshot(p) for i, p in enumerate(state.players)}


def spawn_floats(old_snaps):
    rects = get_player_card_rects()
    for i, p in enumerate(state.players):
        if i not in old_snaps:
            continue
        after = snapshot(p)
        changes = diff(old_snaps[i], after)
        offset = 0
        for key, delta in changes:
            sign = "+" if delta > 0 else ""
            text = f"{sign}{delta} {RU_SHORT[key]}"
            color = COLORS["positive"] if delta > 0 else COLORS["negative"]
            rect = rects[i]
            floating_texts.append(FloatingText(
                text, color,
                rect.centerx,
                rect.y + 20 + offset,
                fonts["floating"],
            ))
            offset += 28


action_buttons = make_action_buttons()

continue_rect = pygame.Rect(0, 0, 300, 60)
continue_rect.center = (WINDOW_WIDTH // 2, 580)

start_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 180, 360, 360, 60)
rules_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 180, 440, 360, 60)
back_btn_rect  = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 70, 200, 46)
lore_continue_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 80, 300, 50)
over_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 80, 300, 50)


def get_win_reason():
    if state.winner is None:
        return ""
    alive = [p for p in state.players if not p.is_dead]
    if len(alive) == 1:
        return "Последнее королевство под Луной"
    if state.turn >= MAX_TURNS:
        return f"Победа по итогам {MAX_TURNS} ходов"
    return "Победа по престижу"


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
    global game_state, current_event, current_event_log, current_action, action_result_log
    global current_event_phrase, current_event_story, last_action_text

    screen.blit(game_background, (0, 0))

    dark = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    dark.fill((0, 0, 0, 90))
    screen.blit(dark, (0, 0))

    player = state.current_player
    player_color = get_player_color(player)

    draw_header(screen, player.name, player_color, state.turn, fonts)
    draw_players_panel(screen, state.players, state.current, icons_small, fonts)

    for ft in floating_texts:
        ft.draw(screen)

    # Плашка "Последнее действие"
    if last_action_text:
        panel_bg = pygame.Surface((WINDOW_WIDTH - 80, 44), pygame.SRCALPHA)
        panel_bg.fill((0, 0, 0, 170))
        screen.blit(panel_bg, (40, 508))

        label = fonts["phrase"].render("Последнее действие:", True, (180, 180, 190))
        screen.blit(label, (60, 520))

        text_surf = fonts["log"].render(last_action_text, True, COLORS["text"])
        screen.blit(text_surf, (270, 522))

    # СОБЫТИЕ
    if game_state == STATE_EVENT:
        event_dict = {
            "title":  current_event.title if current_event else "СОБЫТИЕ",
            "effect": current_event_log or "",
            "phrase": current_event_phrase,
            "story":  current_event_story,
        }
        draw_event_modal(screen, event_dict, mouse_pos, continue_rect, fonts)
        if clicked and continue_rect.collidepoint(click_pos):
            game_state = STATE_ACTION

    # ВЫБОР ДЕЙСТВИЯ
    elif game_state == STATE_ACTION:
        for btn in action_buttons:
            hover = btn["rect"].collidepoint(mouse_pos)
            action = btn["action"]
            afford = player.can_afford(action.cost)

            target_anim = 1.0 if hover and afford else 0.0
            btn["hover_anim"] += (target_anim - btn["hover_anim"]) * 0.25
            anim = btn["hover_anim"]

            grow = int(8 * anim)
            rect = btn["rect"].inflate(grow * 2, grow * 2)

            if not afford:
                color = COLORS["disabled"]
                border_col = (60, 60, 80)
            else:
                base = COLORS["button"]
                hi = COLORS["button_hover"]
                color = tuple(int(base[i] + (hi[i] - base[i]) * anim) for i in range(3))
                border_col = COLORS["player1"]

            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, border_col, rect, 2, border_radius=10)
            draw_text_centered(screen, action.title, rect,
                               fonts["button"], COLORS["text"])

        hint = fonts["resource"].render("Выберите действие", True, COLORS["text"])
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 565))

        if clicked:
            for btn in action_buttons:
                action = btn["action"]
                if btn["rect"].collidepoint(click_pos) and player.can_afford(action.cost):
                    if action.target_required:
                        current_action = action
                        game_state = STATE_TARGET
                    else:
                        before = capture_all()
                        log = state.apply_action(action, target=None)
                        spawn_floats(before)
                        state.check_deaths()
                        state.check_winner()
                        if state.is_game_over:
                            current_screen_global()
                        else:
                            action_result_log = log
                            last_action_text = log
                            game_state = STATE_RESULT
                    break

    # ВЫБОР ЦЕЛИ
    elif game_state == STATE_TARGET:
        hint = fonts["resource"].render(
            f"Выберите цель для «{current_action.title}»", True, COLORS["text"],
        )
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 565))

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
                    before = capture_all()
                    log = state.apply_action(current_action, btn["target"])
                    spawn_floats(before)
                    state.check_deaths()
                    state.check_winner()
                    if state.is_game_over:
                        current_screen_global()
                    else:
                        action_result_log = log
                        last_action_text = log
                        game_state = STATE_RESULT
                    break

    # РЕЗУЛЬТАТ ДЕЙСТВИЯ
    elif game_state == STATE_RESULT:
        draw_result_modal(screen, action_result_log, mouse_pos, continue_rect, fonts)
        if clicked and continue_rect.collidepoint(click_pos):
            state.next_turn()
            start_new_turn()


def start_new_turn():
    global current_event, current_event_log, game_state
    global current_event_phrase, current_event_story

    before = capture_all()
    event, is_positive, log_message = state.start_turn()
    spawn_floats(before)

    if event is None:
        current_event = None
        current_event_log = ""
        current_event_phrase = ""
        current_event_story = ""
        game_state = STATE_ACTION
        return

    current_event = event
    current_event_log = log_message
    current_event_phrase = get_phrase(is_positive)
    current_event_story = get_story(event.id, state.current_player.name)
    game_state = STATE_EVENT


# === ЭКРАН ПОБЕДЫ/ПОРАЖЕНИЯ ===
def draw_game_over(mouse_pos):
    screen.blit(game_background, (0, 0))

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    screen.blit(overlay, (0, 0))

    draw_fireworks(screen)

    card_w, card_h = 760, 460
    card = pygame.Rect(
        WINDOW_WIDTH // 2 - card_w // 2,
        WINDOW_HEIGHT // 2 - card_h // 2 - 30,
        card_w, card_h,
    )

    surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
    surf.fill((16, 16, 24, 235))
    screen.blit(surf, (card.x, card.y))

    if state.winner:
        winner_color = get_player_color(state.winner)

        pygame.draw.rect(screen, winner_color, card, 3, border_radius=18)
        pygame.draw.rect(screen, (255, 215, 0), card.inflate(-10, -10), 1, border_radius=16)

        screen.blit(crown_img, (card.centerx - crown_img.get_width() // 2, card.y + 15))

        name = fonts["win_name"].render(state.winner.name, True, winner_color)
        screen.blit(name, (card.centerx - name.get_width() // 2, card.y + 120))

        win_word = fonts["win_sub"].render("ПОБЕДИЛИ", True, (255, 215, 0))
        screen.blit(win_word, (card.centerx - win_word.get_width() // 2, card.y + 200))

        pygame.draw.line(screen, winner_color,
                         (card.centerx - 260, card.y + 245),
                         (card.centerx + 260, card.y + 245), 2)

        reason = get_win_reason()
        reason_surf = fonts["resource"].render(reason, True, COLORS["text"])
        screen.blit(reason_surf, (card.centerx - reason_surf.get_width() // 2, card.y + 265))

        info = fonts["phrase"].render(
            f"Престиж: {state.winner.prestige}    Ходов: {state.turn} / {MAX_TURNS}",
            True, (180, 180, 190),
        )
        screen.blit(info, (card.centerx - info.get_width() // 2, card.y + 310))

        dead = [p for p in state.players if p.is_dead]
        if dead:
            dead_title = fonts["phrase"].render("Павшие под Кровавой Луной:", True, (160, 160, 170))
            screen.blit(dead_title, (card.centerx - dead_title.get_width() // 2, card.y + 355))

            names = "  •  ".join(p.name for p in dead)
            names_surf = fonts["log"].render(names, True, COLORS["negative"])
            screen.blit(names_surf, (card.centerx - names_surf.get_width() // 2, card.y + 390))

    else:
        pygame.draw.rect(screen, COLORS["player1"], card, 3, border_radius=18)

        title = fonts["huge"].render("НИКТО НЕ ВЫЖИЛ", True, COLORS["negative"])
        screen.blit(title, (card.centerx - title.get_width() // 2, card.y + 130))

        pygame.draw.line(screen, COLORS["player1"],
                         (card.centerx - 220, card.y + 220),
                         (card.centerx + 220, card.y + 220), 2)

        quote = fonts["resource"].render(
            "Кровавая Луна забрала всех...",
            True, (180, 180, 190),
        )
        screen.blit(quote, (card.centerx - quote.get_width() // 2, card.y + 260))

    color = COLORS["button_hover"] if over_btn_rect.collidepoint(mouse_pos) else COLORS["button"]
    pygame.draw.rect(screen, color, over_btn_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 215, 0), over_btn_rect, 2, border_radius=10)
    draw_text_centered(screen, "ИГРАТЬ СНОВА", over_btn_rect, fonts["button"], COLORS["text"])


def current_screen_global():
    global current_screen
    current_screen = SCREEN_OVER
    clear_fireworks()
    spawn_firework(WINDOW_WIDTH // 2, 300)
    play_music("win_music.mp3")


# === ГЛАВНЫЙ ЦИКЛ ===
def main():
    global current_screen, game_state, floating_texts, last_action_text

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for ft in floating_texts[:]:
            ft.update(dt)
            if ft.dead:
                floating_texts.remove(ft)

        if current_screen == SCREEN_OVER:
            update_fireworks(dt)

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
                floating_texts = []
                last_action_text = ""
                play_music("game_music.mp3")
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
                game_state = STATE_ACTION
                floating_texts = []
                last_action_text = ""
                clear_fireworks()
                play_music("menu_music.mp3")
                current_screen = SCREEN_START

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
