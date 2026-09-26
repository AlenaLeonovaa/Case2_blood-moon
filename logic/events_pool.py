"""События и действия игры «Кровавая Луна»."""

import random

from models.action import Action
from models.event import RandomEvent


def action_alliance(actor, target):
    """A1: Союз — оба получают −1 смуты."""
    actor.smuta = max(0, actor.smuta - 1)
    target.smuta = max(0, target.smuta - 1)
    actor.alliance_with = target
    target.alliance_with = actor
    return f"{actor.name} заключил союз с {target.name}"


def action_trade(actor, target):
    """A2: Торговля — −3 деньги, +3 пропитание."""
    actor.money -= 3
    actor.food += 3
    return f"{actor.name} обменял 3 деньги на 3 пропитания"


def action_raid(actor, target):
    """A3: Набег — −1 народ, у цели −2 пропитания, +1 смуты себе."""
    actor.people -= 1
    target.food = max(0, target.food - 2)
    actor.smuta += 1
    return f"{actor.name} совершил набег на {target.name}"


def action_bribe(actor, target):
    """A4: Подкуп — −3 деньги, у цели −2 смуты."""
    actor.money -= 3
    target.smuta = max(0, target.smuta - 2)
    return f"{actor.name} подкупил {target.name}"


def action_discord(actor, target):
    """A5: Раздор — −2 деньги, у цели +2 смуты."""
    actor.money -= 2
    target.smuta += 2
    return f"{actor.name} посеял раздор в {target.name}"


ACTIONS = [
    Action(
        id="A1",
        title="Союз",
        cost={"food": 1},
        target_required=True,
        apply=action_alliance,
    ),
    Action(
        id="A2",
        title="Торговля",
        cost={"money": 3},
        target_required=False,
        apply=action_trade,
    ),
    Action(
        id="A3",
        title="Набег",
        cost={"people": 1},
        target_required=True,
        apply=action_raid,
    ),
    Action(
        id="A4",
        title="Подкуп",
        cost={"money": 3},
        target_required=True,
        apply=action_bribe,
    ),
    Action(
        id="A5",
        title="Раздор",
        cost={"money": 2},
        target_required=True,
        apply=action_discord,
    ),
]


EVENTS = [
    RandomEvent(
        id="E1",
        title="Пожар",
        effects={"food": -3, "land": -1},
        is_positive=False,
    ),
    RandomEvent(
        id="E2",
        title="Затмение",
        effects={"money": 5},
        is_positive=True,
    ),
    RandomEvent(
        id="E3",
        title="Эпидемия",
        effects={"people": -3, "smuta": 2},
        is_positive=False,
    ),
    RandomEvent(
        id="E4",
        title="Полная луна",
        effects={"food": 5},
        is_positive=True,
    ),
    RandomEvent(
        id="E5",
        title="Инквизиция",
        effects={"food": -2, "smuta": 3},
        is_positive=False,
    ),
    RandomEvent(
        id="E6",
        title="Травник",
        effects={"money": 3, "land": 1},
        is_positive=True,
    ),
]


def roll_event():
    """Выбирает случайное событие и определяет позитив/негатив.

    Returns:
        tuple: (event, is_positive_outcome).
    """
    event = random.choice(EVENTS)
    is_positive_outcome = random.random() < 0.5
    return event, is_positive_outcome


def apply_event(player, event, is_positive_outcome):
    """Применяет событие к игроку с учётом инверсии."""
    should_invert = event.is_positive != is_positive_outcome

    log_parts = []
    for resource, value in event.effects.items():
        actual_value = -value if should_invert else value

        if resource == "smuta":
            player.smuta = max(0, player.smuta + actual_value)
        else:
            current = getattr(player, resource)
            new_value = max(0, current + actual_value)
            setattr(player, resource, new_value)

        sign = "+" if actual_value > 0 else ""
        log_parts.append(f"{sign}{actual_value} {resource}")

    return f"{event.title}: {', '.join(log_parts)}"
