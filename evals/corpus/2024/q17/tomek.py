from main import read_input
from enum import Enum

class Registers:
    def __init__(self, register_a, register_b, register_c):
        self.a = register_a
        self.b = register_b
        self.c = register_c

    def __str__(self):
        return f'Register A: {self.a}\nRegister B: {self.b}\nRegister C: {self.c}'

class Operand:
    def __init__(self, raw):
        self.raw = raw

    def evaluate_combo(self, registers: Registers):
        if not (0 <= self.raw <= 6):
            raise Exception(f'Invalid operand value: {self.raw}')
        if 0 <= self.raw <= 3:
            return self.raw
        if self.raw == 4:
            return registers.a
        if self.raw == 5:
            return registers.b
        if self.raw == 6:
            return registers.c
        raise Exception("Impossible!")

    def evaluate_literal(self):
        return self.raw

class InstructionType(Enum):
    adv = 0
    bxl = 1
    bst = 2
    jnz = 3
    bxc = 4
    out = 5
    bdv = 6
    cdv = 7

class Instruction:
    def __init__(self, opcode, operand):
        self.type = InstructionType(opcode)
        self.operand = Operand(operand)

class Program:
    def __init__(self, instructions):
        self.registers = Registers(0, 0, 0)
        self.instructions = instructions
        self.instructions_string = ''.join([str(i) for i in instructions])
        self.instruction_pointer = 0
        self.output = ''

    def __str__(self):
        output = ','.join([str(x) for x in self.output])
        return f'{self.registers}\n\nProgram: {self.instructions}\nOutput: {output}\n'

    def terminated(self):
        return self.instruction_pointer >= len(self.instructions)

    def next_instruction(self):
        instruction = int(self.instructions[self.instruction_pointer])
        operand = int(self.instructions[self.instruction_pointer + 1])
        return Instruction(instruction, operand)

    def evaluate_instruction(self, instruction: Instruction):
        if instruction.type == InstructionType.adv:
            self.registers.a = int(self.registers.a / (2 ** instruction.operand.evaluate_combo(self.registers)))
        elif instruction.type == InstructionType.bxl:
            self.registers.b = self.registers.b ^ instruction.operand.evaluate_literal()
        elif instruction.type == InstructionType.bst:
            self.registers.b = instruction.operand.evaluate_combo(self.registers) % 8
        elif instruction.type == InstructionType.jnz:
            if self.registers.a != 0:
                self.instruction_pointer = instruction.operand.evaluate_literal()
                return # Instruction pointer is not increased by 2 after this instruction.
        elif instruction.type == InstructionType.bxc:
            self.registers.b = self.registers.b ^ self.registers.c
        elif instruction.type == InstructionType.out:
            self.output += str(instruction.operand.evaluate_combo(self.registers) % 8)
        elif instruction.type == InstructionType.bdv:
            self.registers.b = int(self.registers.a / (2 ** instruction.operand.evaluate_combo(self.registers)))
        elif instruction.type == InstructionType.cdv:
            self.registers.c = int(self.registers.a / (2 ** instruction.operand.evaluate_combo(self.registers)))
        else:
            raise Exception(f'Unrecognised instruction type: {instruction.type}')

        self.instruction_pointer += 2

    def run(self, registers, visualise=False):
        self.registers = registers
        while not self.terminated():
            next_instruction = self.next_instruction()
            self.evaluate_instruction(next_instruction)
            if visualise:
                print(f'{self}\n*****************************')

    def output_matches_instructions(self):
        return self.instructions_string == self.output

    def copy(self):
        return Program(self.instructions)

def parse_program(filename) -> (Program, Registers):
    raw = read_input(filename)
    register_a = int(raw[0].split(':')[1].strip())
    register_b = int(raw[1].split(':')[1].strip())
    register_c = int(raw[2].split(':')[1].strip())
    instructions = [int(x) for x in raw[4].split(':')[1].strip().split(',')]
    registers = Registers(register_a, register_b, register_c)
    return Program(instructions), registers

# Trick here is to observe that the program involves looping around doing bit-fiddling of the register values.
# Crucially each loop involves a 3 bit shift for the value in register A. This restricts the search space for DFS.
def search_compatible(program, a, b, c, instructions_length, possible_a_values):
    for n in range(8):
        candidate_a = (a << 3) | n
        next_program = program.copy()
        next_program.run(Registers(candidate_a, b, c))
        if next_program.output == program.instructions_string[-instructions_length:]:
            if len(program.instructions) == instructions_length:
                possible_a_values.add(candidate_a)
            else:
                search_compatible(program, candidate_a, b, c, instructions_length + 1, possible_a_values)

    if len(possible_a_values) > 0:
        return min(possible_a_values)

def part1() -> str:
    program, registers = parse_program('q17.txt')
    program.run(registers)
    return ','.join([str(x) for x in program.output])

def part2() -> int:
    program, registers = parse_program('q17.txt')
    return search_compatible(program, 0, registers.b, registers.c, 1, set())

print(part1())
print(part2())