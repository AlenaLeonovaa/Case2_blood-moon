import pygame

pygame.init()

# === ФОН ===
background = pygame.image.load("assets/background.PNG")
background = pygame.transform.scale(background, (1280, 720))

# === ОКНО ===
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кровавая Луна")
clock = pygame.time.Clock()

# === ЦВЕТА ===
BG           = (18, 18, 24)
PANEL        = (32, 32, 42)
TEXT         = (230, 230, 230)
BUTTON       = (60, 60, 80)
BUTTON_HOVER = (90, 90, 120)
POSITIVE     = (100, 220, 120)
NEGATIVE     = (220, 80, 80)
PLAYER1      = (180, 30, 40)   # Вампиры — красный

# === ШРИФТЫ ===
FONT_TITLE    = pygame.font.SysFont("arial", 28, bold=True)
FONT_RESOURCE = pygame.font.SysFont("arial", 22)
FONT_LOG      = pygame.font.SysFont("arial", 18)
FONT_BUTTON   = pygame.font.SysFont("arial", 22)

# === ФЕЙКОВЫЕ ДАННЫЕ (пока нет разработчиков) ===
player = {
    "name": "ВАМПИРЫ",
    "food": 10,
    "money": 10,
    "land": 5,
    "people": 10,
    "smuta": 0,
    "prestige": 12,
    "turn": 3,
}

log_messages = [
    ("Инквизиция: −2 food, +3 smuta", NEGATIVE),
    ("Оборотни совершили набег",      TEXT),
    ("Полная луна: +5 food",          POSITIVE),
    ("Ведьмы заключили союз",         TEXT),
    ("Затмение: +5 money",            POSITIVE),
]

event = {
    "title": "🔥 ПОЖАР",
    "effect": "−3 food, −1 land",
}

actions = ["Союз", "Торговля", "Набег", "Подкуп", "Раздор"]

# === КНОПКИ ДЕЙСТВИЙ (создаём один раз) ===
button_y = 620
button_w = 200
button_h = 50
spacing = 20
total_w = 5 * button_w + 4 * spacing
start_x = (WIDTH - total_w) // 2

buttons = []
for i, name in enumerate(actions):
    x = start_x + i * (button_w + spacing)
    rect = pygame.Rect(x, button_y, button_w, button_h)
    buttons.append({"rect": rect, "text": name, "hover": False})


# === ФУНКЦИЯ ОТРИСОВКИ ТЕКСТА ПО ЦЕНТРУ ===
def draw_text_centered(surface, text, rect, font, color):
    surf = font.render(text, True, color)
    x = rect.x + (rect.width - surf.get_width()) // 2
    y = rect.y + (rect.height - surf.get_height()) // 2
    surface.blit(surf, (x, y))


# === ГЛАВНЫЙ ЦИКЛ ===
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # --- ФОН ---
    screen.blit(background, (0, 0))

    # --- HEADER ---
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 60))
    pygame.draw.rect(screen, PLAYER1, (0, 60, WIDTH, 6))

    # Текст в header
    title = FONT_TITLE.render(f"ХОД: {player['name']}", True, TEXT)
    screen.blit(title, (24, 14))

    turn = FONT_RESOURCE.render(f"Ход №{player['turn']} / 20", True, TEXT)
    screen.blit(turn, (WIDTH - turn.get_width() - 24, 18))

    # --- ПАНЕЛЬ РЕСУРСОВ ---
    pygame.draw.rect(screen, PANEL, (0, 66, WIDTH, 80))
    resources = [
        ("🍞", "Пропитание", player["food"]),
        ("💰", "Деньги",     player["money"]),
        ("🏞", "Земля",      player["land"]),
        ("👥", "Народ",      player["people"]),
        ("🔥", "Смута",      player["smuta"]),
        ("⭐", "Престиж",    player["prestige"]),
    ]
    rx = 60
    for icon, label, value in resources:
        # иконка + число
        text = FONT_RESOURCE.render(f"{icon} {value}", True, TEXT)
        screen.blit(text, (rx, 82))
        # подпись снизу
        label_surf = FONT_LOG.render(label, True, (150, 150, 160))
        screen.blit(label_surf, (rx, 112))
        rx += 190

    # --- ЛОГ СОБЫТИЙ ---
    log_rect = pygame.Rect(20, 170, 400, 400)
    pygame.draw.rect(screen, PANEL, log_rect, border_radius=12)

    log_title = FONT_TITLE.render("ЛОГ СОБЫТИЙ", True, TEXT)
    screen.blit(log_title, (40, 190))

    ly = 240
    for msg, color in log_messages:
        line = FONT_LOG.render(f"> {msg}", True, color)
        screen.blit(line, (40, ly))
        ly += 30

    # --- КАРТОЧКА СОБЫТИЯ ---
    event_rect = pygame.Rect(540, 170, 500, 300)
    pygame.draw.rect(screen, PANEL, event_rect, border_radius=12)

    ev_title = FONT_TITLE.render(event["title"], True, TEXT)
    screen.blit(ev_title, (event_rect.centerx - ev_title.get_width() // 2, 230))

    ev_effect = FONT_RESOURCE.render(event["effect"], True, NEGATIVE)
    screen.blit(ev_effect, (event_rect.centerx - ev_effect.get_width() // 2, 300))

    # кнопка "Продолжить"
    cont_rect = pygame.Rect(0, 0, 200, 50)
    cont_rect.center = (event_rect.centerx, 400)
    pygame.draw.rect(screen, BUTTON, cont_rect, border_radius=8)
    draw_text_centered(screen, "Продолжить", cont_rect, FONT_BUTTON, TEXT)

    # --- КНОПКИ ДЕЙСТВИЙ ---
    for btn in buttons:
        hover = btn["rect"].collidepoint(mouse_pos)
        color = BUTTON_HOVER if hover else BUTTON
        pygame.draw.rect(screen, color, btn["rect"], border_radius=8)
        draw_text_centered(screen, btn["text"], btn["rect"], FONT_BUTTON, TEXT)

    # --- ПОДСКАЗКА ВНИЗУ ---
    hint = FONT_RESOURCE.render("Выберите действие", True, TEXT)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 690))

    # --- ОБНОВЛЕНИЕ ---
    pygame.display.flip()
    clock.tick(60)

pygame.quit()


