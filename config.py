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

# Цвета
COLORS = {
    # Фон и панели
    "bg": (0, 0, 0),
    "panel": (0, 0, 0),
    "text": (0, 0, 0),
    "button": (0, 0, 0),
    "button_hover": (0, 0, 0),

    # События
    "positive": (0, 0, 0),
    "negative": (0, 0, 0),

    # Игровые состояния
    "eliminated": (0, 0, 0),
    "alliance": (0, 0, 0),
    "disabled": (0, 0, 0),

    # Фракции
    "player1": (0, 0, 0),
    "player2": (0, 0, 0),
    "player3": (0, 0, 0),
    "player4": (0, 0, 0),
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
