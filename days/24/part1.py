import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from icecream import ic
from parse import parse

# --> Puzzle solution


def XOR(a, b):
    return int(a != b)


def OR(a, b):
    return int(a or b)


def AND(a, b):
    return int(a and b)


@dataclass
class Gate:
    name: str
    depends1: str | None
    depends2: str | None
    action: Callable | None
    value: int = -1


def read_input(input_data):
    gates = {}

    registers, program = input_data.split("\n\n")
    for register in registers.splitlines():
        name, value = parse("{}: {:d}", register)
        gates[name] = Gate(name, name, name, None, value)

    ACTIONS = {"XOR": XOR, "OR": OR, "AND": AND}

    for line in program.splitlines():
        depends1, action, depends2, name = parse("{} {} {} -> {}", line)
        gates[name] = Gate(name, depends1, depends2, ACTIONS[action], -1)

    return gates


def resolve(gates):
    done = False

    while not done:
        done = True
        for gate in gates.values():
            if gate.value == -1:
                done = False
                d1 = gates[gate.depends1].value
                d2 = gates[gate.depends2].value

                if d1 != -1 and d2 != -1:
                    gate.value = gate.action(d1, d2)

    ic(gates)
    return gates


def score(gates):
    result = 0
    keys = (v for v in gates if v.startswith("z"))
    for key in keys:
        if gates[key].value:
            result += 1 << int(key[1:])
    return result


def solve(input_data):
    gates = read_input(input_data)
    gates = resolve(gates)
    return score(gates)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
sample_input2 = Path("input-sample2.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 4),
    (sample_input2, 2024),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=[1, 2])
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v"])
    if ex not in {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    #  Actual input data generally has more iterations, turn off log
    ic.disable()
    my_input = Path("input.txt").read_text().strip()
    result = solve(my_input)
    print(result)
