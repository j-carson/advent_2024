import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


def safe(report):
    diffs = np.diff(report)
    signs = np.sign(diffs)
    if (np.all(signs > 0) or np.all(signs < 0)) and np.all(np.abs(diffs) < 4):
        return True
    return False


def dampen(report):
    for index in range(len(report)):
        if safe(np.delete(report, index)):
            return True
    ic(report)
    return False


def parse_line(txt):
    return np.array([int(i) for i in txt.split()])


def solve(input_data):
    reports = [parse_line(line) for line in input_data.splitlines()]

    score = 0
    for r in reports:
        if safe(r):
            score += 1
        elif dampen(r):
            score += 1
    return score


# --> Test driven development helpers

RETEST = (
    np.array([32, 35, 33, 34, 35, 38]),
    np.array([70, 71, 73, 74, 75, 78, 79, 83]),
)


@pytest.mark.parametrize("sample_data", RETEST)
def test_cases(sample_data) -> None:
    assert dampen(sample_data)


# Test any examples given in the problem
sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 4),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=("sample",))
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.disable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v", "--pdb"])
    if ex not in {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    #  Actual input data generally has more iterations, turn off log
    ic.enable()
    my_input = Path("input.txt").read_text().strip()
    result = solve(my_input)
    print(result)
