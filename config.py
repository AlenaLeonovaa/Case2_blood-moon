"""Константы игры «Кровавая Луна»."""

# Окно
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Стартовые ресурсы
START_FOOD = 10
START_MONEY = 10
START_LAND = 5
START_PEOPLE = 10
START_SMUTA = 0

# Лимиты
MAX_SMUTA = 10
MAX_TURNS = 20
WIN_PRESTIGE = 30
INCOME_LAND_DIVISOR = 2
INCOME_PEOPLE_DIVISOR = 5
PRESTIGE_MONEY_DIVISOR = 5
PRESTIGE_PEOPLE_DIVISOR = 5

# Цвета
COLORS = {
    # Фон и панели
    "bg": (18, 18, 24),
    "panel": (32, 32, 42),
    "text": (230, 230, 230),
    "button": (60, 60, 80),
    "button_hover": (90, 90, 90),

    # События
    "positive": (100, 220, 120),
    "negative": (220, 80, 80),

    # Игровые состояния
    "eliminated": (80, 80, 80),
    "alliance": (100, 180, 220),
    "disabled": (50, 50, 60),

    # Фракции
    "player1": (180, 30, 40),
    "player2": (122, 110, 90),
    "player3": (140, 60, 180),
    "player4": (60, 180, 90),
}

# Фракции
FACTIONS = [
    {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"},
    {"name": "Оборотни", "color_key": "player2", "resource_name": "Мясо"},
    {"name": "Ведьмы", "color_key": "player3", "resource_name": "Зелья"},
    {"name": "Охотники", "color_key": "player4", "resource_name": "Оружие"},
]

# Шрифты
FONT_TITLE_SIZE = 28
FONT_RESOURCE_SIZE = 22
FONT_LOG_SIZE = 18

# Панель ресурсов
PANEL_HEIGHT = 80

# Лог
LOG_WIDTH = 400
LOG_HEIGHT = 400
LOG_X = 20
LOG_Y = 100
LOG_MAX_MESSAGES = 5

# Модалка
MODAL_WIDTH = 500
MODAL_HEIGHT = 300

# Кнопки
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20

# Кнопки цели
TARGET_BUTTON_WIDTH = 150
TARGET_BUTTON_HEIGHT = 50
