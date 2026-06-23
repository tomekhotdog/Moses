"""Well-modelled domain: concepts everywhere, primitives wrapped."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import NewType

UserId = NewType("UserId", int)


class Status(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Money:
    amount: Decimal
    currency: str


@dataclass
class Order:
    id: UserId
    total: Money
    status: Status


class OrderBook:
    orders: dict[UserId, Order]

    def place(self, owner: UserId, total: Money) -> Order:
        ...

    def for_owner(self, owner: UserId) -> list[Order]:
        ...

    def balance(self, owner: UserId) -> Money:
        ...
