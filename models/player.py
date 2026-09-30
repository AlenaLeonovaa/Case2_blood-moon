"""Модель игрока для игры «Кровавая Луна»."""

from config import (
    START_FOOD,
    START_MONEY,
    START_LAND,
    START_PEOPLE,
    START_SMUTA,
    MAX_SMUTA,
    PRESTIGE_MONEY_DIVISOR,
    PRESTIGE_PEOPLE_DIVISOR,
)


class Player:
    """
    Игровая фракция одного игрока.
    Хранит ресурсы и состояние.
    """

    def __init__(self, name, faction):
        self.name = name

        # информация о фракции из config.py
        self.faction = faction["name"]
        self.resource_name = faction["resource_name"]

        self.color_key = faction["color_key"]

        # ресурсы
        self.food = START_FOOD
        self.money = START_MONEY
        self.land = START_LAND
        self.people = START_PEOPLE
        self.smuta = START_SMUTA
