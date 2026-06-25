# AoC 2024 Day 22 — "Monkey Market"

Each buyer has a secret number that evolves by a pseudorandom step:

1. Multiply the secret by 64, then *mix* (XOR with the secret) and *prune* (take modulo 16777216).
2. Divide the secret by 32 (floor), then mix and prune.
3. Multiply the secret by 2048, then mix and prune.

Where:
- **mix**: `value = value XOR secret`
- **prune**: `value = value % 16777216`

## Part 1

For each buyer, simulate 2000 evolution steps to produce their 2000th next secret
number. Sum each buyer's 2000th next secret number across all buyers.

## Part 2

The price a buyer offers is the ones-digit of their current secret number. As the
secret evolves, the prices change. You instruct a monkey to sell on the first
occurrence of a specific sequence of 4 consecutive price changes (the deltas
between successive ones-digits). The same 4-change sequence is used for every
buyer; for each buyer the monkey sells at the first occurrence of that sequence
(if it ever occurs). Find the 4-change sequence that maximizes the total number
of bananas (sum of sell prices) across all buyers.

The input is a list of initial secret numbers, one per line.
