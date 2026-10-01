"""Случайное событие игры «Кровавая Луна»."""

from dataclasses import dataclass


@dataclass
class RandomEvent:
    """Случайное событие.
    """

    id: str
    title: str
    effects: dict
    is_positive: bool
    is_random: bool = True