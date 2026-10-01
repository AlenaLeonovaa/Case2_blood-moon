import pytest
from models.player import Player
from logic.events_pool import action_alliance, action_trade, action_raid, action_bribe, action_discord, roll_event


#Тесты для класса PLAYER (models/player.py)

def test_player_initialization():
    """Проверка стартовых ресурсов игрока"""
    p = Player("Тест", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    assert p.food == 10
    assert p.money == 10
    assert p.land == 5
    assert p.people == 10
    assert p.smuta == 0


def test_prestige_formula():
    """Проверка формулы престижа: land*2 + money//5 + people//5 - smuta"""
    p = Player("Тест", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p.land = 5
    p.money = 10
    p.people = 10
    p.smuta = 0
    # 5*2 + 10//5 + 10//5 - 0 = 10 + 2 + 2 = 14
    assert p.prestige == 14


def test_death_by_smuta():
    """Проверка смерти при смуте >= 10"""
    p = Player("Тест", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p.smuta = 10
    assert p.is_dead == True


def test_death_by_people():
    """Проверка смерти при народе <= 0"""
    p = Player("Тест", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p.people = 0
    assert p.is_dead == True


def test_can_afford():
    """Проверка, хватает ли ресурсов на действие"""
    p = Player("Тест", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p.money = 5
    # Действие стоит 3 деньги
    assert p.can_afford({"money": 3}) == True
    # Действие стоит 10 денег
    assert p.can_afford({"money": 10}) == False


#Тесты для действий (logic/events_pool.py)

def test_action_alliance():
    """A1: Союз уменьшает смуту у обоих на 1 (но не ниже 0)"""
    p1 = Player("Игрок1", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p2 = Player("Игрок2", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p1.smuta = 5
    p2.smuta = 0

    action_alliance(p1, p2)

    assert p1.smuta == 4
    assert p2.smuta == 0  # Проверка, что не ушло в минус


def test_action_trade():
    """A2: Торговля: -3 деньги, +3 пропитание"""
    p1 = Player("Игрок1", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p1.money = 10
    p1.food = 5

    action_trade(p1, None)  # Торговля не требует цели

    assert p1.money == 7
    assert p1.food == 8


def test_action_raid():
    """A3: Набег: -1 народ у себя, -2 еды у цели, +1 смута себе"""
    p1 = Player("Игрок1", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p2 = Player("Игрок2", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p1.people = 10
    p1.smuta = 0
    p2.food = 10

    action_raid(p1, p2)

    assert p1.people == 9
    assert p1.smuta == 1
    assert p2.food == 8


def test_action_bribe():
    """A4: Подкуп: -3 деньги у себя, -2 смуты у цели"""
    p1 = Player("Игрок1", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p2 = Player("Игрок2", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p1.money = 10
    p2.smuta = 5

    action_bribe(p1, p2)

    assert p1.money == 7
    assert p2.smuta == 3


def test_action_discord():
    """A5: Раздор: -2 деньги у себя, +2 смуты у цели"""
    p1 = Player("Игрок1", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p2 = Player("Игрок2", {"name": "Вампиры", "color_key": "player1", "resource_name": "Кровь"})
    p1.money = 10
    p2.smuta = 2

    action_discord(p1, p2)

    assert p1.money == 8
    assert p2.smuta == 4


#Тесты для событий (logic/events_pool.py)

def test_roll_event_distribution():
    """T8: Проверка вероятности (должно быть ~50/50)"""
    positives = 0
    iterations = 1000
    for _ in range(iterations):
        event, is_positive = roll_event()
        if is_positive:
            positives += 1

    # Проверяем, что отклонение от 50% не больше 10% (для 1000 итераций)
    assert 400 < positives < 600
