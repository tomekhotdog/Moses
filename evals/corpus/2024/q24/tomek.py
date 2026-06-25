from main import read_input_string
from enum import Enum

WIRE_UNSET_VALUE = -1

class Operation(Enum):
    AND = 0
    OR = 1
    XOR = 2

def parse_operation(raw: str):
    if raw == 'AND':
        return Operation.AND
    elif raw == 'OR':
        return Operation.OR
    elif raw == 'XOR':
        return Operation.XOR
    else:
        raise Exception(f'Failed to parse operation: {raw}')

class Wire:
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def __str__(self):
        return f'{self.identifier} = {self.value}'

class Gate:
    def __init__(self, op: Operation, input_1: Wire, input_2: Wire, output: Wire):
        self.operation = op
        self.input_1 = input_1
        self.input_2 = input_2
        self.output = output

    def __str__(self):
        op_str = str(self.operation).split('.')[1]
        return f'{self.input_1.identifier} {op_str} {self.input_2.identifier} -> {self.output.identifier}'

    def ready(self) -> bool:
        return self.input_1.value != WIRE_UNSET_VALUE and self.input_2.value != WIRE_UNSET_VALUE

    def calculate(self):
        if not self.ready():
            raise Exception(f'Attempted to calculate gate ({self}) when inputs not set!')
        if self.operation == Operation.AND:
            self.output.value = self.input_1.value & self.input_2.value
        elif self.operation == Operation.OR:
            self.output.value = self.input_1.value | self.input_2.value
        elif self.operation == Operation.XOR:
            self.output.value = self.input_1.value ^ self.input_2.value
        else:
            raise Exception(f'Unexpected operation ({self.operation})!')

class Circuit:
    def __init__(self, wires, gates):
        self.wires = wires
        self.z_wires = list(set([x for x in wires.values() if x.identifier.startswith('z')]))
        self.z_wires.sort(key=lambda x: x.identifier)
        self.gates = gates
        self.output_wire_to_gates = { x.output.identifier : x for x in self.gates }

    def z_wires_set(self) -> bool:
        return all([x.value != WIRE_UNSET_VALUE for x in self.z_wires])

    def z_wires_value(self):
        return sum([self.z_wires[i].value * (2 ** i) for i in range(len(self.z_wires))])

    def tick(self):
        for gate in self.gates:
            if gate.ready():
                gate.calculate()

    def simulate(self):
        while not self.z_wires_set():
            self.tick()

def parse_input(filename):
    elems = read_input_string(filename).split('\n\n')
    initial_values = { x.split(':')[0]: int(x.split(':')[1].strip()) for x in elems[0].split('\n')}
    wires = {}
    gates = []

    def get_or_create_wire(wire_id):
        if wire_id not in wires:
            value = initial_values.get(wire_id, WIRE_UNSET_VALUE)
            wires[wire_id] = Wire(wire_id, value)
        return wires[wire_id]

    for x in elems[1].split('\n'):
        items = x.split('->')
        inputs = items[0].strip().split(' ')
        op = parse_operation(inputs[1])
        wire_out_id = items[1].strip()
        wire_out = get_or_create_wire(wire_out_id)
        wire_1_id = inputs[0]
        wire_1 = get_or_create_wire(wire_1_id)
        wire_2_id = inputs[2]
        wire_2 = get_or_create_wire(wire_2_id)
        gates.append(Gate(op, wire_1, wire_2, wire_out))
    return Circuit(wires, gates)

"""
Deep breaths... summoning 1st year hardware course... what was a D flip-flop again?
Our circuit is a broken 46 bit adder. The way this works is we go from least to most
significant bit (starting from x00, y00), XOR the inputs and carry forward (AND inputs). 

The circuit can therefore be split into sections that calculate the nth output bit (Zn):
                                 
                       Xn_1 Yn_1   <prev_carry> 
                          | |          |
                          AND         AND      
                           |____   ____|    Xn Yn
                                |  |         | |
                                 OR          XOR
                                  |           |
                             carry_wire    xor_wire        
                                  |____   ____|
                                       | |
                                       XOR
                                        |
                                        Zn

My approach involves looking for discrepancies between the above and what can be observed
in the actual circuit for the zth output bit.                                    
"""
def suspicious_wires_for_z_block(z_wire_id: str, circuit: Circuit):
    proximate_gate = circuit.output_wire_to_gates[z_wire_id]
    if proximate_gate.operation != Operation.XOR:
        return [z_wire_id]

    w1_gate = circuit.output_wire_to_gates[proximate_gate.input_1.identifier]
    w2_gate = circuit.output_wire_to_gates[proximate_gate.input_2.identifier]
    input_gates = [w1_gate, w2_gate]
    unexpected_ands = [x for x in input_gates if x.operation == Operation.AND]
    # Expecting to see an XOR and an OR as input to the z_gate. Wires leading from AND gates have been swapped.
    if len(unexpected_ands) > 0:
        return [x.output.identifier for x in unexpected_ands]

    xors = [x for x in input_gates if x.operation == Operation.XOR]
    if len(xors) == 2:
        # Identify the XOR gate not of the expected form: x21 XOR y21 -> xxx.
        return [x.output.identifier for x in xors if x.input_1.identifier[0] not in ['x', 'y']]

    xn_yn_xor_wire_gate = w1_gate if w1_gate.operation == Operation.XOR else w2_gate
    combined_carry_wire_gate = w1_gate if w1_gate.operation == Operation.OR else w2_gate
    combined_carry_w1_gate = circuit.output_wire_to_gates[combined_carry_wire_gate.input_1.identifier]
    combined_carry_w2_gate = circuit.output_wire_to_gates[combined_carry_wire_gate.input_2.identifier]

    unexpected = [x for x in [combined_carry_w1_gate, combined_carry_w2_gate] if x.operation != Operation.AND]
    if len(unexpected) > 0:
        return [x.output.identifier for x in unexpected]

    return []

def suspicious_wires(circuit: Circuit):
    suspicious = []
    # A bit untidy, but some special cases apply for the extreme bits
    # which were not required for the solution.
    for i in range(44, 1, -1):
        z_wire_id = f'z{i}' if i >= 10 else f'z0{i}'
        suspicious += suspicious_wires_for_z_block(z_wire_id, circuit)
    return ','.join(sorted(suspicious))

def part1() -> int:
    circuit = parse_input('q24.txt')
    circuit.simulate()
    return circuit.z_wires_value()

def part2() -> str:
    circuit = parse_input('q24.txt')
    return suspicious_wires(circuit)


print(part1())
print(part2())