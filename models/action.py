from dataclasses import dataclass
from typing import Callable


@dataclass
class Action:
    """Управляемое действие игрока.

    Attributes:
        id: идентификатор действия (A1-A5).
        title: название действия.
        cost: словарь стоимости, например {"money": 3}.
        target_required: True, если нужно выбрать цель.
        apply: функция(actor, target) -> str, возвращает лог.
    """

    id: str
    title: str
    cost: dict
    target_required: bool
    apply: Callable
