import sys
from pathlib import Path

import pytest
from icecream import ic
from parse import parse

# --> Puzzle solution


def solve(input_data):
    list1 = []
    list2 = []
    for line in input_data.strip().splitlines():
        d1, d2 = parse("{:d}  {:d}", line)
        list1.append(d1)
        list2.append(d2)

    list1 = sorted(list1)
    list2 = sorted(list2)

    score = 0
    for a, b in zip(list1, list2):
        dist = abs(a - b)
        score += dist

    return score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 11),
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
