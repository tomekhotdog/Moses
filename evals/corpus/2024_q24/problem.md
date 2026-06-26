# AoC 2024 Day 24 — "Crossing Wires"

Wires carry boolean values; logic gates (AND, OR, XOR) combine two input wires
into an output wire. Inputs are wires named `x00..` and `y00..`; outputs are
wires `z00...`.

## Part 1
Simulate all gates and read the binary number formed by the z-wires
(`z00` = least significant) as a decimal.

## Part 2
The circuit is meant to be a binary adder (`x + y = z`) but 4 pairs of gate
output wires have been swapped; identify the 8 wires involved in swaps and
output their names sorted and comma-separated.

## Input format
Two sections separated by a blank line:

```
x00: 1
y00: 0
...

x00 AND y00 -> z00
x01 XOR y01 -> z01
...
```
