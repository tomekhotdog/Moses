# Advent of Code 2024, Day 17: Chronospatial Computer

A 3-bit virtual machine has three registers A, B, C (which may hold any integer) and runs a program made of (opcode, operand) pairs. There are 8 opcodes:

- `adv` (0): A = A >> combo(operand)  (integer division of A by 2**combo)
- `bxl` (1): B = B XOR literal(operand)
- `bst` (2): B = combo(operand) % 8
- `jnz` (3): if A != 0, jump instruction pointer to literal(operand) (no auto-increment)
- `bxc` (4): B = B XOR C (operand ignored)
- `out` (5): emit combo(operand) % 8
- `bdv` (6): B = A >> combo(operand)
- `cdv` (7): C = A >> combo(operand)

Combo operands: 0-3 are literal values 0-3; 4 = register A; 5 = register B; 6 = register C; 7 is reserved. Literal operands are the operand value itself. The instruction pointer advances by 2 after each instruction unless a jump occurs.

**Part 1:** Run the program from the given initial register values and print the comma-separated list of values produced by `out`.

**Part 2:** Find the lowest positive initial value of register A that makes the program output an exact copy of its own program (a quine). This is typically solved by reconstructing A digit-by-digit (3 bits at a time) from the end of the program, since each loop iteration consumes the low 3 bits of A.
