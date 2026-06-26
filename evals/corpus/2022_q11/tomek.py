from __future__ import annotations
from main import read_input_string
from typing import List
from functools import reduce


def parse_operation(desc: str):
    match desc:
        case '*':
            return lambda x, y: x * y
        case '+':
            return lambda x, y: x + y
        case _:
            raise Exception("Failed to parse specific operation: [" + desc + ']')


def parse_operand(desc: str):
    match desc:
        case 'old':
            return lambda x: x
        case constant:
            return lambda _: int(constant)


def product(items: List[int]) -> int:
    return reduce(lambda x, y: x * y, items, 1)


# Of the form: "Operation: new = old * 19"
class Operation:
    def __init__(self, raw_description):
        self.raw_description = raw_description
        assignment = raw_description.split('=')[1].strip()
        args = assignment.split(' ')
        if len(args) != 3:
            raise Exception("Failed to parse operation: [" + raw_description + ']')

        operand1 = parse_operand(args[0].strip())
        operation = parse_operation(args[1].strip())
        operand2 = parse_operand(args[2].strip())

        self.evaluation_function = lambda x: operation(operand1(x), operand2(x))

    def __str__(self):
        return self.raw_description

    def evaluate(self, input_value: int) -> int:
        return self.evaluation_function(input_value)


# Of the form: " by 17"
class Test:
    def __init__(self, raw_description):
        self.raw_description = raw_description
        args = raw_description.split("divisible by")
        if len(args) > 2:
            raise Exception("Failed to parse test: [" + raw_description + ']')
        divisor = int(args[1].strip())
        self.divisor = divisor
        self.evaluation_function = lambda x: x % divisor == 0

    def __str__(self):
        return self.raw_description

    def evaluate(self, input_value):
        return self.evaluation_function(input_value)


class FollowUpAction:
    def __init__(self, if_true_branch: str, if_false_branch: str):
        self.if_true = self.parse_follow_up_action(if_true_branch)
        self.if_false = self.parse_follow_up_action(if_false_branch)

    def parse_follow_up_action(self, desc: str):
        if "throw to monkey" not in desc:
            raise Exception('Failed to parse update action: [' + desc + ']')
        monkey_index = int(desc.split("throw to monkey")[1].strip())
        return lambda monkeys, item: monkeys[monkey_index].receive_item(item)


class Monkey:
    def __init__(self, index: int, starting_items: List[int],
                 operation: Operation, test: Test, follow_up: FollowUpAction):
        self.index = index
        self.items = starting_items
        self.operation = operation
        self.test = test
        self.follow_up = follow_up
        self.inspected_items = 0
        self.worry_reduction = lambda x: x

    def __str__(self):
        return 'Monkey ' + str(self.index) + ': ' + str(self.items)

    def play_turn(self, monkeys: List[Monkey]):
        while len(self.items) > 0:
            self.inspected_items += 1
            worry_level = self.items.pop(0)
            new_worry_level = self.operation.evaluate(worry_level)
            new_worry_level = self.worry_reduction(new_worry_level)
            if self.test.evaluate(new_worry_level):
                self.follow_up.if_true(monkeys, new_worry_level)
            else:
                self.follow_up.if_false(monkeys, new_worry_level)

    def receive_item(self, item):
        self.items.append(item)

    def configure_worry_reduction(self, worry_reduction):
        self.worry_reduction = worry_reduction


class Shenanigans:
    def __init__(self, monkeys: List[Monkey]):
        self.monkeys = monkeys

    def play_round(self):
        for monkey in self.monkeys:
            monkey.play_turn(self.monkeys)

    def play_rounds(self, n: int):
        for i in range(n):
            self.play_round()

    # Defined as the product of the number of inspections made by the two most active monkeys.
    def monkey_business(self) -> int:
        inspected_per_monkey = [monkey.inspected_items for monkey in self.monkeys]
        return product(sorted(inspected_per_monkey)[-2:])

    def configure_worry_reduction(self, worry_reduction):
        for monkey in self.monkeys:
            monkey.configure_worry_reduction(worry_reduction)


def parse_monkey(desc: str) -> Monkey:
    lines = desc.split('\n')
    if 'Monkey' not in lines[0]:
        raise Exception('Failed to parse monkey index: [' + lines[0] + ']')
    monkey_index = int(lines[0].split(' ')[1].split(':')[0])
    if 'Starting items' not in lines[1]:
        raise Exception('Failed to parse starting items: [' + lines[1] + ']')
    starting_items_str = lines[1].split(':')[1].split(',')
    starting_items = [int(item.strip()) for item in starting_items_str]
    if 'Operation' not in lines[2]:
        raise Exception('Failed to parse operation: [' + lines[2] + ']')
    operation = Operation(lines[2].split(':')[1])
    if 'Test' not in lines[3]:
        raise Exception('Failed to parse test: [' + lines[3] + ']')
    test = Test(lines[3].split(':')[1])
    follow_up = FollowUpAction(lines[4], lines[5])

    return Monkey(monkey_index, starting_items, operation, test, follow_up)


def parse_monkeys() -> List[Monkey]:
    lines = read_input_string('q11.txt')
    monkey_descriptions = lines.split('\n\n')
    return [parse_monkey(desc) for desc in monkey_descriptions]


def part1() -> int:
    shenanigans = Shenanigans(parse_monkeys())
    shenanigans.configure_worry_reduction(lambda x: int(x / 3))
    shenanigans.play_rounds(20)
    return shenanigans.monkey_business()


def part2() -> int:
    shenanigans = Shenanigans(parse_monkeys())
    lcm_divisors = product([monkey.test.divisor for monkey in shenanigans.monkeys])
    shenanigans.configure_worry_reduction(lambda x: int(x % lcm_divisors))
    shenanigans.play_rounds(10000)
    return shenanigans.monkey_business()
