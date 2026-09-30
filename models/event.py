"""Модель случайного события игры «Кровавая Луна»."""

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
    event_type: str


    def get_effect_text(self):
        """
        Создаёт текстовое описание эффекта
        для лога и модального окна.
        """

        result = []

        for resource, value in self.effects.items():

            if value > 0:
                result.append(
                    f"+{value} {resource}"
                )

            else:
                result.append(
                    f"{value} {resource}"
                )

        return ", ".join(result)
