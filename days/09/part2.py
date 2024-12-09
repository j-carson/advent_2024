import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


@dataclass
class MapEntry:
    idn: int
    location: int
    size: int


def blockful(idn, size):
    for _ in range(size):
        yield (idn)


def get_disk_map(input_data):
    input_nums = [int(i) for i in input_data]

    free_map = []
    disk_map = []

    full = True
    idn = 0
    location = 0

    ic(input_nums)
    for size in input_nums:
        if full:
            disk_map.append(MapEntry(idn=idn, location=location, size=size))
            idn += 1
        else:
            free_map.append(MapEntry(idn=0, location=location, size=size))

        location += size
        full = not full

    ic(disk_map)
    ic(free_map)

    for file in reversed(disk_map):
        for spot in free_map:
            if spot.location > file.location:
                break
            if spot.size >= file.size:
                file.location = spot.location
                spot.location += file.size
                spot.size -= file.size

    return disk_map


def score(disk_map):
    total = 0
    for file in disk_map:
        for idx in range(file.location, file.location + file.size):
            total += file.idn * idx
    return total


def solve(input_data):
    final_map = get_disk_map(input_data)

    final_map = sorted(final_map, key=lambda m: m.location)
    ic(final_map)
    return score(final_map)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 2858),
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
