from dataclasses import dataclass


@dataclass
class RandomEvent:
    """Случайное событие, выпадающее перед ходом.

    Attributes:
        id: идентификатор события (E1-E6).
        title: название события.
        effects: словарь эффектов, например {"food": -3, "land": -1}.
        is_positive: True, если событие изначально положительное.
    """

    id: str
    title: str
    effects: dict
    is_positive: bool
