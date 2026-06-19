"""A clean module. No Commandment should fire here."""

from dataclasses import dataclass

SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class LineItem:
    """A single priced line on an order."""

    name: str
    price: float
    quantity: int

    def subtotal(self) -> float:
        return self.price * self.quantity


@dataclass(frozen=True)
class Order:
    """An order composed of line items."""

    items: tuple[LineItem, ...]

    def total(self) -> float:
        return sum(item.subtotal() for item in self.items)

    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


def days_to_seconds(days: int) -> int:
    return days * SECONDS_PER_DAY


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
