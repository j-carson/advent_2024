import sys
from collections import deque
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


def blockful(idn, size):
    for _ in range(size):
        yield (idn)


def get_disk_map(input_data):
    input_nums = [int(i) for i in input_data]
    sizes = deque(input_nums[::2])
    idns = deque(range(len(sizes)))
    frees = deque(input_nums[1::2])

    disk_map = []
    wip = []  # file we are in the process of moving

    while len(sizes):
        # Write down the full space
        # Pop a file off the idns and write that down
        size = sizes.popleft()
        idn = idns.popleft()
        disk_map.extend(blockful(idn, size))

        # Fill the subsequent free space
        free = frees.popleft()
        for _ in range(free):
            if not wip:
                wip = list(blockful(idns.pop(), sizes.pop()))
            disk_map.append(wip.pop())

    # make sure that we fill in the last little bit of the last file
    if wip:
        disk_map.extend(wip)

    return disk_map


def score(disk_map):
    total = 0
    for i, val in enumerate(disk_map):
        total += i * val
    return total


def solve(input_data):
    disk_map = get_disk_map(input_data)
    ic(disk_map)
    return score(disk_map)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 1928),
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
