import sys
from functools import cache
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


@cache
def is_possible(display, towels):
    choices = [towel for towel in towels if display.startswith(towel)]

    total_possible = 0
    for choice in choices:
        if choice == display:
            total_possible += 1
        else:
            remaining_display = display[len(choice) :]
            total_possible += is_possible(remaining_display, towels)

    return total_possible


def solve(input_data):
    towel_string, displays = input_data.split("\n\n")
    towels = tuple(towel_string.split(", "))

    score = 0
    for display in displays.splitlines():
        score += is_possible(display, towels)
    return score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 16),
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
