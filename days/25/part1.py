import sys
from itertools import product
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


class Lock:
    def __init__(self, columns):
        self.is_lock = True
        self.is_key = False
        self.columns = columns


class Key:
    def __init__(self, columns):
        self.is_lock = False
        self.is_key = True
        self.columns = columns


def parse(box):
    arr = np.array([list(line) for line in box.splitlines()])
    bool_arr = arr == "#"
    columns = np.sum(bool_arr, axis=0) - 1

    ic(arr, bool_arr, columns)

    if bool_arr[0, 0]:
        return Lock(columns)
    return Key(columns)


def solve(input_data):
    boxes = input_data.split("\n\n")
    stuff = [parse(box) for box in boxes]
    locks = [k for k in stuff if k.is_lock]
    keys = [k for k in stuff if k.is_key]
    matches = 0
    for lock, key in product(locks, keys):
        if np.all((lock.columns + key.columns) < 6):
            matches += 1
    return matches


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 3),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=("sample",))
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
