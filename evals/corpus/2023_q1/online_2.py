# Source: https://medium.com/@coldstart_coder/python-advent-of-code-2023-day-1-trebuchet-troubles-c2ead56812e8
# Real online solution (Coldstart Coder). Saved as-found.

import re


def process_input_part1(code_input: str) -> int:
    lines = code_input.split("\n")
    sum = 0
    for line in lines:
        numbers_only = re.sub("[^\d]", "", line)
        calibration_value_for_line = numbers_only[0] + numbers_only[-1]
        sum += int(calibration_value_for_line)
    return sum


def process_input_part2(code_input: str) -> int:
    lines = code_input.split("\n")
    sum = 0
    spelt_out_digits = [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine"
    ]
    digit_mapping = {spelt_out_digit: str(i) for i, spelt_out_digit in enumerate(spelt_out_digits)}
    digit_mapping.update({str(i): str(i) for i in range(10)})

    combined_or = "|".join(digit_mapping.keys())
    expression = "(?=(%s))" % combined_or

    for line in lines:
        digit_elements = [digit_mapping[item] for item in re.findall(expression, line)]
        calibration_value_for_line = digit_elements[0] + digit_elements[-1]
        sum += int(calibration_value_for_line)
    return sum
