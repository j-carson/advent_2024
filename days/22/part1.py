import sys
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


def mix(a, b):
    return a ^ b


def prune(a):
    return a % 16777216


def next_secret(secret):
    step1 = prune(mix(secret, secret * 64))
    step2 = prune(mix(step1 // 32, step1))
    return prune(mix(step2, step2 * 2048))


def test_next_secret():
    secret = 123
    expected_sequence = [
        15887950,
        16495136,
        527345,
        704524,
        1553684,
        12683156,
        11100544,
        12249484,
        7753432,
        5908254,
    ]
    for item in expected_sequence:
        secret = next_secret(secret)
        assert secret == item


@pytest.mark.parametrize(
    "start,result",
    [
        (1, 8685429),
        (10, 4700978),
        (100, 15273692),
        (2024, 8667524),
    ],
)
def test_2000_secrets(start, result):
    secret = start
    for i in range(2000):
        secret = next_secret(secret)
    assert secret == result


def solve(input_data):
    score = 0
    for line in input_data.splitlines():
        secret = int(line)
        for _ in range(2000):
            secret = next_secret(secret)
        score += secret
    return score


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
