"""C27 annotation classifier: domain-richness of a single annotation in [0,1]."""

from __future__ import annotations

import ast

import pytest

from moses.commandments.c27_data_over_primitives import classify_annotation


def _ann(src: str) -> ast.expr:
    """Parse `x: <src>` and return the annotation node."""
    mod = ast.parse(f"x: {src}")
    return mod.body[0].annotation  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "src, expected",
    [
        # primitives / erased -> 0
        ("int", 0.0),
        ("str", 0.0),
        ("bool", 0.0),
        ("None", 0.0),
        ("Any", 0.0),
        ("dict", 0.0),
        ("list", 0.0),
        # concepts -> 1
        ("UserId", 1.0),
        ("Order", 1.0),
        ("datetime", 1.0),
        ("Decimal", 1.0),
        # weak -> 0.5
        ("Literal['a', 'b']", 0.5),
        # containers score by element / args
        ("list[Order]", 1.0),
        ("list[int]", 0.0),
        ("set[Customer]", 1.0),
        ("dict[UserId, Money]", 1.0),
        ("dict[str, int]", 0.0),
        ("dict[str, Order]", 0.0),          # min: key is primitive
        ("tuple[Order, Customer]", 1.0),
        ("tuple[int, int]", 0.0),
        ("tuple[Order, ...]", 1.0),
        # Optional / unions: None is stripped, nullability is not obsession
        ("Optional[Order]", 1.0),
        ("Order | None", 1.0),
        ("int | None", 0.0),
        ("Order | Customer", 1.0),
        ("int | str", 0.0),
        # typing-cased aliases
        ("List[Order]", 1.0),
        ("Dict[str, int]", 0.0),
        # transparent wrappers score by their inner type
        ("Annotated[int, 'meta']", 0.0),
        ("Annotated[Order, 'meta']", 1.0),
        ("ClassVar[str]", 0.0),
        ("Final[Order]", 1.0),
        # Callable scores by its return type
        ("Callable[[int], str]", 0.0),
        ("Callable[[int], Order]", 1.0),
        # bare protocol containers are erased -> 0 (consistent with bare list/dict)
        ("Iterable", 0.0),
        ("Sequence", 0.0),
        ("Mapping", 0.0),
        # mixed union takes the min
        ("Order | str", 0.0),
        ("Union[Order, None]", 1.0),
        ("Union[Order, str]", 0.0),
    ],
)
def test_classify_annotation(src, expected):
    assert classify_annotation(_ann(src)) == expected


def test_none_node_is_zero():
    assert classify_annotation(None) == 0.0


def test_container_ordering():
    # The load-bearing nuance: collection-of-concept beats primitive-valued map.
    assert classify_annotation(_ann("list[Order]")) > classify_annotation(_ann("dict[str, int]"))
    assert classify_annotation(_ann("dict[str, int]")) == classify_annotation(_ann("int"))
