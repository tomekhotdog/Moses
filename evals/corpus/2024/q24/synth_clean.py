"""Advent of Code 2024 Day 24 — "Crossing Wires".

Part 1 simulates a combinational logic circuit and reads the value carried by
the z-wires.  Part 2 treats the circuit as a ripple-carry binary adder and
locates the eight gate-output wires that have been swapped, by checking each
gate against the structural rules a correct adder must obey.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from operator import and_, or_, xor
from typing import Callable, Dict, List

Z_PREFIX = "z"
INPUT_PREFIXES = ("x", "y")

GATE_OPS: Dict[str, Callable[[int, int], int]] = {
    "AND": and_,
    "OR": or_,
    "XOR": xor,
}


@dataclass(frozen=True)
class Gate:
    """A two-input logic gate driving a single output wire."""

    op: str
    lhs: str
    rhs: str
    out: str

    def evaluate(self, signals: Dict[str, int]) -> int:
        return GATE_OPS[self.op](signals[self.lhs], signals[self.rhs])

    def is_ready(self, signals: Dict[str, int]) -> bool:
        return self.lhs in signals and self.rhs in signals

    def reads_initial_inputs(self) -> bool:
        return self.lhs[0] in INPUT_PREFIXES and self.rhs[0] in INPUT_PREFIXES


def parse(text: str) -> tuple[Dict[str, int], List[Gate]]:
    initial_block, gate_block = text.strip().split("\n\n")

    signals: Dict[str, int] = {}
    for line in initial_block.splitlines():
        wire, value = line.split(":")
        signals[wire.strip()] = int(value)

    gates: List[Gate] = []
    for line in gate_block.splitlines():
        expression, out = line.split("->")
        lhs, op, rhs = expression.split()
        gates.append(Gate(op, lhs, rhs, out.strip()))

    return signals, gates


def simulate(signals: Dict[str, int], gates: List[Gate]) -> Dict[str, int]:
    """Iteratively evaluate gates until every output wire has a value."""
    signals = dict(signals)
    pending = list(gates)
    while pending:
        ready = [gate for gate in pending if gate.is_ready(signals)]
        if not ready:
            raise ValueError("circuit has no evaluable gate; possible cycle")
        for gate in ready:
            signals[gate.out] = gate.evaluate(signals)
        pending = [gate for gate in pending if gate.out not in signals]
    return signals


def read_number(signals: Dict[str, int], prefix: str = Z_PREFIX) -> int:
    wires = sorted((w for w in signals if w.startswith(prefix)), reverse=True)
    bits = "".join(str(signals[w]) for w in wires)
    return int(bits, 2)


def part1(text: str) -> int:
    signals, gates = parse(text)
    return read_number(simulate(signals, gates))


def find_swapped_wires(gates: List[Gate]) -> List[str]:
    """Return the wires whose gates violate ripple-carry-adder structure.

    Structural rules for a correct adder (n input bits, output z00..zNN):
      * Every z-wire except the most significant is driven by an XOR gate.
      * A gate feeding a z-wire from an XOR must take two intermediate wires.
      * An XOR gate that reads x/y inputs must feed another XOR or an AND.
      * An AND gate that reads x/y inputs (except bit 0) must feed an OR.
    """
    by_output = {gate.out: gate for gate in gates}
    z_wires = sorted(w for w in by_output if w.startswith(Z_PREFIX))
    highest_z = z_wires[-1]

    feeds_xor = {gate.lhs for gate in gates if gate.op == "XOR"}
    feeds_xor |= {gate.rhs for gate in gates if gate.op == "XOR"}
    feeds_or = {gate.lhs for gate in gates if gate.op == "OR"}
    feeds_or |= {gate.rhs for gate in gates if gate.op == "OR"}

    suspect: set[str] = set()
    for gate in gates:
        drives_z = gate.out.startswith(Z_PREFIX)

        # z-wires must come from XOR, except the final carry-out.
        if drives_z and gate.out != highest_z and gate.op != "XOR":
            suspect.add(gate.out)

        # A non-z XOR that reads x/y must feed another XOR.
        if gate.op == "XOR" and not drives_z:
            if gate.reads_initial_inputs() and gate.out not in feeds_xor:
                suspect.add(gate.out)
            if not gate.reads_initial_inputs():
                suspect.add(gate.out)

        # AND gates (except the half-adder for bit 0) must feed an OR.
        if gate.op == "AND" and gate.lhs not in ("x00", "y00"):
            if gate.out not in feeds_or:
                suspect.add(gate.out)

        # A gate driving z (other than the top one) should be XOR of two
        # intermediates, never an OR.
        if gate.op == "OR" and drives_z and gate.out != highest_z:
            suspect.add(gate.out)

    return sorted(suspect)


def part2(text: str) -> str:
    _, gates = parse(text)
    return ",".join(find_swapped_wires(gates))


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q24.txt"
    with open(path) as handle:
        text = handle.read()
    print(part1(text))
    print(part2(text))


if __name__ == "__main__":
    main()
