from dataclasses import dataclass


@dataclass
class RandomEvent:
    """
    Случайное событие.

    is_positive:
    True — событие изначально положительное.
    False — отрицательное.
    """

    id: str
    title: str
    effects: dict
    is_positive: bool
