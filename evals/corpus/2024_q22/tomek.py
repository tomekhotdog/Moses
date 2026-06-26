from main import read_input

def parse_input(filename):
    return [int(x) for x in read_input(filename)]

def mix(initial, other):
    return initial ^ other

def prune(initial):
    return initial % 16777216

def next_secret_number(initial):
    result1 = initial * 64
    secret = mix(initial, result1)
    secret = prune(secret)
    result2 = secret // 32
    secret = mix(secret, result2)
    secret = prune(secret)
    result3 = secret * 2048
    secret = mix(secret, result3)
    secret = prune(secret)
    return secret

def generate_secret_numbers(initial, n, ones=False):
    generated = [initial % 10 if ones else initial]
    secret = initial
    for _ in range(n):
        secret = next_secret_number(secret)
        generated.append(secret % 10 if ones else secret)
    return generated

def calculate_deltas(secret_numbers):
    deltas = []
    for i in range(len(secret_numbers) - 1):
        deltas.append(secret_numbers[i+1] - secret_numbers[i])
    return deltas

def max_bananas_for_quad_deltas(secret_numbers, delta_lists):
    bananas_for_quad_deltas = {}
    bananas_noted_for_list = {}

    for i, deltas in enumerate(delta_lists):
        bananas_noted_for_list[i] = set()
        for j in range(len(deltas) - 3):
            quad_delta = (deltas[j], deltas[j+1], deltas[j+2], deltas[j+3])
            if quad_delta not in bananas_noted_for_list[i]:
                bananas_for_quad_deltas.setdefault(quad_delta, 0)
                corresponding_secret_number_idx = (j+3) + 1
                bananas_for_quad_deltas[quad_delta] += secret_numbers[i][corresponding_secret_number_idx]
                bananas_noted_for_list[i].add(quad_delta)

    return max(bananas_for_quad_deltas.values())

def part1() -> int:
    initials = parse_input('q22.txt')
    return sum([generate_secret_numbers(x, 2000)[-1] for x in initials])

def part2() -> int:
    initials = parse_input('q22.txt')
    secret_numbers = [generate_secret_numbers(x, 2000, ones=True) for x in initials]
    deltas = [calculate_deltas(x) for x in secret_numbers]
    return max_bananas_for_quad_deltas(secret_numbers, deltas)

# NB: execution takes ~15s.
print(part1())
print(part2())