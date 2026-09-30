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
    Игрок (фракция) в игре «Кровавая Луна».

    Хранит:
    - название фракции;
    - ресурс силы;
    - деньги;
    - землю;
    - народ;
    - смуту;
    - цветовую настройку.
    """

    def __init__(self, name, faction):
        """
        Создание игрока.

        Args:
            name: имя игрока.
            faction: словарь фракции из config.py.
        """

        self.name = name

        # Данные фракции
        self.faction = faction["name"]
        self.resource_name = faction["resource_name"]
        self.color_key = faction["color_key"]

        # Стартовые ресурсы
        self.food = START_FOOD
        self.money = START_MONEY
        self.land = START_LAND
        self.people = START_PEOPLE
        self.smuta = START_SMUTA

        # Союзник (используется позже для механики союза)
        self.alliance_with = None


    @property
    def prestige(self):
        """
        Расчёт престижа игрока.

        Формула:
        земля * 2 + деньги // 5 + народ // 5 - смута
        """

        return (
            self.land * 2
            + self.money // PRESTIGE_MONEY_DIVISOR
            + self.people // PRESTIGE_PEOPLE_DIVISOR
            - self.smuta
        )


    @property
    def is_dead(self):
        """
        Проверка, выбыл ли игрок.

        Игрок погибает если:
        - смута >= 10;
        - народ <= 0.
        """

        return self.smuta >= MAX_SMUTA or self.people <= 0


    def can_afford(self, cost):
        """
        Проверяет, хватает ли ресурсов для действия.

        Пример:
        {
            "money": 3
        }

        означает, что нужно минимум 3 денег.
        """

        for resource, amount in cost.items():

            if getattr(self, resource) < amount:
                return False

        return True


    def change_resource(self, resource, amount):
        """
        Изменяет количество ресурса.

        Например:

        change_resource("money", 5)

        даст +5 денег.

        Если ресурс становится меньше нуля,
        он устанавливается в 0.
        """

        current_value = getattr(self, resource)

        new_value = current_value + amount

        if new_value < 0:
            new_value = 0

        setattr(self, resource, new_value)
