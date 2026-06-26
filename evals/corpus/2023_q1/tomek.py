from main import read_input

digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
digit_map = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9
}


# Convert a string representation of a digit (e.g either "2" or "eight", etc) to its numerical value.
def digit_to_value(digit: str) -> int:
    # Of the form "5","6",etc.
    if len(digit) == 1:
        return int(digit)
    elif digit in digit_map:
        return digit_map[digit]
    else:
        raise Exception(f"Unexpected digit: {digit}!")


def extract_calibration(line: str, include_words) -> int:
    representations = digits
    if include_words:
        representations += list(digit_map.keys())
    # Find locations of the digits in the input.
    digit_locations = []
    for digit in representations:
        index = 0
        while index != -1:
            index = line.find(digit, index)
            if index != -1:
                digit_locations.append((digit_to_value(digit), index))
                index += len(digit)
    assert len(digit_locations) > 0, f"Expected at least one digit in {line}!"
    # Calibration requires the first and last digits.
    sorted_locations = sorted(digit_locations, key=lambda x: x[1])
    return sorted_locations[0][0] * 10 + sorted_locations[-1][0]


def part1() -> int:
    lines = read_input('q1.txt')
    return sum(list(map(lambda x: extract_calibration(x, False), lines)))


def part2() -> int:
    lines = read_input('q1.txt')
    return sum(list(map(lambda x: extract_calibration(x, True), lines)))
