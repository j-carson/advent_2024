import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


def safe(report):
    diffs = np.diff(report)
    ic(diffs)
    signs = np.sign(diffs)
    if (np.all(signs > 0) or np.all(signs < 0)) and np.all(np.abs(diffs) < 4):
        return True
    return False


def parse_line(txt):
    return np.array([int(i) for i in txt.split()])


def solve(input_data):
    reports = [parse_line(line) for line in input_data.splitlines()]
    return np.sum(safe(r) for r in reports)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 2),
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
