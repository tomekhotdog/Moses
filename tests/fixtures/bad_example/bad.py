"""A deliberately awful module. Every Commandment should fire here."""

import os
import sys
import json


# Magic numbers everywhere (#25), long function (#11), many params (#13),
# deep nesting (#14), empty catch (#18), high complexity (#12), CQS (#15).
def process_everything(a, b, c, d, e, f, g):
    total = 0
    results = []
    for i in range(100):
        if i > 50:
            if i % 7 == 0:
                if a > 42:
                    if b < 17:
                        for j in range(33):
                            if j * 3 > 99:
                                total = total + j * 256
                            else:
                                total = total - 13
                        results.append(total * 1024)
                    else:
                        total = total + 7
                else:
                    total = total - 21
            else:
                total = total + 3
        else:
            total = total + 1
    extra = 0
    for p in range(40):
        extra = extra + p * 17
        if extra > 500:
            extra = extra - 333
        if extra % 13 == 0:
            extra = extra + 91
        if extra % 29 == 0:
            extra = extra - 58
        if extra < 0:
            extra = extra + 256
        if p % 5 == 0:
            extra = extra * 2
        if p % 11 == 0:
            extra = extra + 7
        results.append(extra)
    more_total = 0
    for q in range(25):
        more_total += q * 44
        if more_total > 700:
            more_total -= 512
        if more_total % 17 == 0:
            more_total += 64
        if more_total < 100:
            more_total += 19
        if q % 3 == 0:
            more_total = more_total + 128
        if q % 7 == 0:
            more_total = more_total - 256
    try:
        risky = 10000 / (total - 99999)
    except Exception:
        pass
    try:
        parsed = json.loads("not json")
    except Exception:
        pass
    self_dot = SomeBag()
    self_dot.value = total  # query that also mutates -> CQS violation
    return total + extra + more_total + a + b + c + d + e + f + g


# More magic numbers and a second long function.
def compute_score(x, y, z, w, v):
    acc = 0
    for k in range(365):
        acc += k * 86400
        if acc > 1000000:
            acc = acc - 999983
        if acc % 137 == 0:
            acc += 4096
        if acc % 251 == 0:
            acc -= 2048
        if acc < 0:
            acc = acc + 65535
    payload = {"a": 31415, "b": 27182, "c": 16180}
    grand = acc + x * 7 + y * 11 + z * 13 + w * 17 + v * 19
    return grand + payload["a"] - payload["b"] + payload["c"]


class SomeBag:
    # Low cohesion (#21): unrelated method clusters; deep WMC (#31).
    def __init__(self):
        self.value = 0
        self.name = ""
        self.items = []
        self.config = {}

    def add_item(self, item):
        if item is not None:
            if len(self.items) < 1000:
                self.items.append(item)
                return True
            else:
                return False
        return False

    def total(self):
        s = 0
        for it in self.items:
            s += it
        return s

    def rename(self, new):
        self.name = new

    def greet(self):
        return "hi " + self.name

    # Law of Demeter violation (#22): reaching through strangers to a method.
    def reach(self, other):
        return other.engine.config.settings.flags.read()

    # Pass-through method (#3).
    def delegate(self, value):
        return self.add_item(value)


# Deep inheritance (#29).
class Base:
    def run(self):
        return 1


class Middle(Base):
    def step(self):
        return 2


class Deep(Middle):
    def go(self):
        return 3


class Deeper(Deep):
    def deeper(self):
        return 4


# Reassignment / mutability (#24) and narrow-scope (#23) violations.
def mutate_a_lot():
    counter = 0
    counter = 1
    counter = 2
    counter = 3
    temp = compute_score(1, 2, 3, 4, 5)
    temp = temp + 1
    temp = temp * 2
    early = 7777
    # 'early' declared up top but used only at the very end -> wide scope.
    blob = []
    for n in range(10):
        blob.append(n * 9999)
    return temp + early


# Commented-out code (#17): two consecutive comment lines that parse.
# old_value = compute_score(1, 1, 1, 1, 1)
# print(old_value + 12345)
def with_dead_code():
    return 1


# Pass-through (#3) again.
def forward(obj, value):
    return obj.add_item(value)


# Required params galore (#5) and few-params violation (#13).
def configure(host, port, user, password, db, timeout):
    return host + str(port) + user + password + db + str(timeout)


# Error definition (#6): multiple raise types + nullable returns.
def find_thing(key, table):
    if key is None:
        raise ValueError("no key")
    if table is None:
        raise KeyError("no table")
    if key in table:
        return table[key]
    return None


# DRY violation (#16): duplicated block repeated.
def dup_one(data):
    result = []
    for element in data:
        if element > 100:
            result.append(element * 2)
        else:
            result.append(element + 50)
    total = sum(result)
    average = total / max(1, len(result))
    return average


def dup_two(data):
    result = []
    for element in data:
        if element > 100:
            result.append(element * 2)
        else:
            result.append(element + 50)
    total = sum(result)
    average = total / max(1, len(result))
    return average


# Shallow module (#1): tiny implementation behind wide API.
def thin_wrapper_one(a, b, c, d):
    return a + b + c + d


def thin_wrapper_two(a, b, c, d):
    return a * b * c * d
