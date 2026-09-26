class Player:
    """Игрок — одна из четырёх фракций."""

    def __init__(self, name: str, color: tuple) -> None:
        """Создаёт игрока с стартовыми ресурсами."""
        self.name = name
        self.color = color
        self.food = 10
        self.money = 10
        self.land = 5
        self.people = 10
        self.smuta = 0

    @property
    def prestige(self) -> int:
        """Считает престиж по формуле."""
        return self.land * 2 + self.money // 5 + self.people // 5 - self.smuta

    @property
    def is_dead(self) -> bool:
        """Проверяет, выбыл ли игрок."""
        return self.smuta >= 10 or self.people <= 0

    def can_afford(self, action) -> bool:
        """Проверяет, хватает ли ресурсов на действие."""
        return all(
            getattr(self, res) >= cost
            for res, cost in action.cost.items()
        )
