import sys
from functools import cache
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


@cache
def count_stones(start_val, n_blinks):
    # Return the number of stones after n blinks
    # for a stone with given start val and number
    # of blinks

    if n_blinks == 0:
        return 1

    if start_val == 0:
        return count_stones(1, n_blinks - 1)

    strval = str(start_val)
    n_digits = len(strval)

    if n_digits % 2 == 0:
        half = n_digits // 2
        v1 = int(strval[:half])
        v2 = int(strval[half:])
        return count_stones(v1, n_blinks - 1) + count_stones(v2, n_blinks - 1)

    return count_stones(start_val * 2024, n_blinks - 1)


def solve(input_data, n_blinks):
    numbers = [int(i) for i in input_data.split()]
    return sum([count_stones(n, n_blinks) for n in numbers])


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    ("0 1 10 99 999", 1, 7),
    ("125 17", 1, 3),
    ("125 17", 6, 22),
    ("125 17", 25, 55312),
]


@pytest.mark.parametrize("sample_data,n_blinks,sample_solution", EXAMPLES)
def test_samples(sample_data, n_blinks, sample_solution) -> None:
    assert solve(sample_data, n_blinks) == sample_solution


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
    result = solve(my_input, 25)
    print(result)
