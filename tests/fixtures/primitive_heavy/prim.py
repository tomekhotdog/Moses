"""Primitive-obsessed: meaning smeared across str/int/dict."""

from __future__ import annotations


class OrderBook:
    orders: dict[str, int]

    def place(self, owner: str, total: float, currency: str) -> dict[str, int]:
        ...

    def for_owner(self, owner: str) -> list[str]:
        ...

    def summary(self, rows: list[str]) -> tuple[int, int, str]:
        ...
