from config import (
    START_GRAIN,
    START_MONEY,
    START_LAND,
    START_PEOPLE,
    START_SMUTA,
    PRESTIGE_MONEY_DIVISOR,
    PRESTIGE_PEOPLE_DIVISOR,
)


class Player:
    """
    Класс игрока.
    Хранит ресурсы и рассчитывает состояние фракции.
    """

    def __init__(self, name, faction, color):
        self.name = name
        self.faction = faction
        self.color = color

        # стартовые ресурсы
        self.grain = START_GRAIN
        self.money = START_MONEY
        self.land = START_LAND
        self.people = START_PEOPLE
        self.smuta = START_SMUTA

        # союзник (если есть временный союз)
        self.ally = None


    @property
    def prestige(self):
        """
        Формула престижа:
        земля*2 + деньги//5 + народ//5 - смута
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
        Игрок выбывает,
        если смута >= 10 или народ <= 0.
        """
        return self.smuta >= 10 or self.people <= 0


    def can_afford(self, cost):
        """
        Проверяет,
        хватает ли ресурсов для действия.

        Например:
        {"money": 3}
        означает:
        нужно минимум 3 денег.
        """

        for resource, amount in cost.items():
            if getattr(self, resource) < amount:
                return False

        return True


    def add_resource(self, resource, value):
        """
        Изменяет ресурс.

        Например:
        add_resource("money", 5)
        даст +5 денег.
        """

        current = getattr(self, resource)

        new_value = current + value

        # ресурсы не могут уходить ниже нуля
        if new_value < 0:
            new_value = 0

        setattr(self, resource, new_value)
