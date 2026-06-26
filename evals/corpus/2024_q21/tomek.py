import itertools
import re
from main import read_input
from enum import Enum

class PadType(Enum):
    KeyPad = 1
    ArrowPad = 2

chars_map = {
    PadType.KeyPad: 'A0123456789',
    PadType.ArrowPad: '<v>^A'
}

number_to_position = {
    'A': (2, 3),
    '0': (1, 3),
    '1': (0, 2),
    '2': (1, 2),
    '3': (2, 2),
    '4': (0, 1),
    '5': (1, 1),
    '6': (2, 1),
    '7': (0, 0),
    '8': (1, 0),
    '9': (2, 0)
}

arrow_to_position = {
    'A': (2, 0),
    '^': (1, 0),
    '<': (0, 1),
    'v': (1, 1),
    '>': (2, 1)
}

def sequence_avoids_position(start_x, start_y, sequence, to_avoid):
    if to_avoid is None:
        return True
    x, y = start_x, start_y
    for s in sequence:
        if s == '^':
            y -= 1
        elif s == 'v':
            y += 1
        elif s == '<':
            x -= 1
        elif s == '>':
            x += 1
        elif s == 'A':
            continue
        else:
            raise Exception(f'Unexpected instruction: {s}')
        if (x, y) == to_avoid:
            return False
    return True

def sequences_for_position_transition(start_x, start_y, end_x, end_y):
    x_translation, y_translation = end_x - start_x, end_y - start_y
    x_buttons = '>' * x_translation if x_translation > 0 else '<' * abs(x_translation)
    y_buttons = 'v' * y_translation if y_translation > 0 else '^' * abs(y_translation)
    permutations = set(itertools.permutations(x_buttons + y_buttons))
    return [''.join(list(x)) + 'A' for x in permutations]

def sequences_for_keypad_transition(char1, char2):
    start_x, start_y = number_to_position[char1]
    end_x, end_y = number_to_position[char2]
    all_transitions = sequences_for_position_transition(start_x, start_y, end_x, end_y)
    return [x for x in all_transitions if sequence_avoids_position(start_x, start_y, x, (0, 3))]

def sequences_for_arrows_transition(char1, char2):
    start_x, start_y = arrow_to_position[char1]
    end_x, end_y = arrow_to_position[char2]
    all_transitions = sequences_for_position_transition(start_x, start_y, end_x, end_y)
    return [x for x in all_transitions if sequence_avoids_position(start_x, start_y, x, (0, 0))]

def sequences_for_transition(char1, char2, pad_type: PadType):
    if pad_type == PadType.KeyPad:
        return sequences_for_keypad_transition(char1, char2)
    elif pad_type == PadType.ArrowPad:
        return sequences_for_arrows_transition(char1, char2)
    else:
        raise Exception(f'Unexpected PadType: {pad_type}')

def build_base_transitions_map(pad_type: PadType):
    transitions_map = {}
    chars = chars_map[pad_type]
    for i in range(len(chars)):
        for j in range(len(chars)):
            start, end = chars[i], chars[j]
            possibilities = sequences_for_transition(start, end, pad_type)
            transitions_map[(start, end)] = min([len(x) for x in possibilities])

    return transitions_map

def build_transitions_map(arrow_transition_lengths, target_pad: PadType):
    transitions_map = {}
    chars = chars_map[target_pad]
    for i in range(len(chars)):
        for j in range(len(chars)):
            start, end = chars[i], chars[j]
            sequences = []
            for sequence in sequences_for_transition(start, end, target_pad):
                sequences.append(sequence_length(sequence, arrow_transition_lengths))
            transitions_map[(start, end)] = min(sequences)

    return transitions_map

def sequence_length(code, transition_lengths):
    prepended = 'A' + code
    code_transition_lengths = []
    for i in range(len(prepended) - 1):
        transition_length = transition_lengths[(prepended[i], prepended[i+1])]
        code_transition_lengths.append(transition_length)
    return sum(code_transition_lengths)

def code_numeric_part(code):
    match = re.match(r'(\d+)', code)
    if match:
        return int(match.group(1))
    raise Exception(f'Failed to extract numeric part of code! {code}')

def parse_codes(filename):
    return [row for row in read_input(filename)]

"""
Idea here is that every series of instructions (e.g. >^A) can be constructed from a series of transitions from the  
controlling pad (which starts from A (e.g. A>, >^, ^A). Solution involves iteratively building up the sequence 
lengths required for each transition at the nth arrow-pad and then the final keypad. Then use the constructed
transitions lookup table to calculate the 'complexities' of the codes. 
"""
def code_complexities(codes, arrow_keypads):
    arrow_transitions = build_base_transitions_map(PadType.ArrowPad)
    for i in range(arrow_keypads - 1):
        arrow_transitions = build_transitions_map(arrow_transitions, PadType.ArrowPad)

    keypad_transitions = build_transitions_map(arrow_transitions, PadType.KeyPad)
    return sum([sequence_length(code, keypad_transitions) * code_numeric_part(code) for code in codes])

def part1() -> int:
    codes = parse_codes('q21.txt')
    return code_complexities(codes, 2)

def part2() -> int:
    codes = parse_codes('q21.txt')
    return code_complexities(codes, 25)

print(part1())
print(part2())