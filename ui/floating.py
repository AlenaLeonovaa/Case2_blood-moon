"""Всплывающие числа над карточками — визуализация изменений ресурсов."""
import pygame


class FloatingText:
    """Всплывающий текст, который поднимается вверх и исчезает."""

    def __init__(self, text, color, x, y, font):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.font = font
        self.lifetime = 1.8  # секунды
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        self.y -= 45 * dt

    @property
    def dead(self):
        return self.age >= self.lifetime

    def draw(self, screen):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        surf = self.font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        screen.blit(surf, (self.x - surf.get_width() // 2, self.y))


def snapshot(player):
    """Снимок значений ресурсов игрока."""
    return {
        "food":   player.food,
        "money":  player.money,
        "land":   player.land,
        "people": player.people,
        "smuta":  player.smuta,
    }


def diff(before, after):
    """Возвращает список (ресурс, изменение) для изменившихся полей."""
    keys = ["food", "money", "land", "people", "smuta"]
    result = []
    for k in keys:
        d = after[k] - before[k]
        if d != 0:
            result.append((k, d))
    return result
