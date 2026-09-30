"""Состояние игры и логика хода."""

from typing import Optional

from config import (
    FACTIONS,
    MAX_TURNS,
    WIN_PRESTIGE,
    INCOME_LAND_DIVISOR,
    INCOME_PEOPLE_DIVISOR,
)

from logic.events_pool import apply_event, roll_event
from models.player import Player


class GameState:
    """Состояние игры: игроки, ходы, победитель."""

    def __init__(self) -> None:
        """Создаёт игру с 4 игроками."""

        self.players = [
            Player(
                faction["name"],
                faction
            )
            for faction in FACTIONS
        ]

        self.current = 0
        self.turn = 1
        self.winner: Optional[Player] = None
        self.log: list[str] = []


    @property
    def current_player(self) -> Player:
        """Возвращает текущего игрока."""

        return self.players[self.current]


    @property
    def is_game_over(self) -> bool:
        """Проверяет, закончилась ли игра."""

        return self.winner is not None


    def add_log(self, message: str) -> None:
        """Добавляет сообщение в лог."""

        self.log.append(message)

        if len(self.log) > 5:
            self.log.pop(0)


    def apply_income(self, player: Player) -> None:
        """Начисляет доход."""

        player.food += (
            player.land // INCOME_LAND_DIVISOR
        )

        player.money += (
            player.people // INCOME_PEOPLE_DIVISOR
        )


    def start_turn(self) -> tuple:
        """Начинает ход: доход и событие."""

        player = self.current_player

        self.apply_income(player)

        event, is_positive = roll_event()

        log_message = apply_event(
            player,
            event,
            is_positive
        )

        self.add_log(log_message)

        return event, is_positive, log_message


    def apply_action(
        self,
        action,
        target: Optional[Player] = None
    ) -> str:
        """Применяет выбранное действие."""

        actor = self.current_player

        log_message = action.apply(
            actor,
            target
        )

        self.add_log(log_message)

        return log_message


    def check_deaths(self) -> None:
        """Проверяет выбывание игроков."""

        for player in self.players:

            if player.is_dead:
                self.add_log(
                    f"{player.name} выбывает"
                )


    def check_winner(self) -> None:
        """Проверяет победу."""

        alive = [
            player
            for player in self.players
            if not player.is_dead
        ]

        for player in alive:

            if player.prestige >= WIN_PRESTIGE:

                self.winner = player
                self.add_log(
                    f"{player.name} победил!"
                )

                return


        if len(alive) == 1:

            self.winner = alive[0]

            self.add_log(
                f"{alive[0].name} победил!"
            )

            return


        if not alive:
            return


        if self.turn >= MAX_TURNS:

            best = max(
                alive,
                key=lambda player: player.prestige
            )

            self.winner = best

            self.add_log(
                f"{best.name} победил по престижу!"
            )


    def next_turn(self) -> None:
        """Передаёт ход следующему живому игроку."""

        self.turn += 1

        for _ in range(len(self.players)):

            self.current = (
                self.current + 1
            ) % len(self.players)

            if not self.current_player.is_dead:
                return
