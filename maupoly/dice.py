"""Простой вспомогательный классу кубика."""

from dataclasses import dataclass
from random import randint
from typing import Self


@dataclass(frozen=True, slots=True)
class Dice:
    """Простой кубик для игры."""

    first: int
    second: int

    @property
    def is_double(self) -> bool:
        """Если выпал дубль."""
        return self.second == self.first

    @property
    def total(self) -> int:
        """Сколько всего выпало на кубике."""
        return self.first + self.second

    @classmethod
    def new(cls) -> Self:
        """Создаёт новый кубик."""
        return cls(randint(1, 6), randint(1, 6))

    def __str__(self) -> str:
        """Строковое представление кубика."""
        return f"{self.first} + {self.second} ({self.total})"
