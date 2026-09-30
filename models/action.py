from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Action:
    """
    Описание действия игрока.

    Каждое действие содержит:
    - название;
    - стоимость;
    - нужна ли цель;
    - функцию применения.
    """

    id: str
    title: str
    cost: dict
    target_required: bool
    apply: Optional[Callable] = None
