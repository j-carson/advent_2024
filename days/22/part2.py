import sys
from collections import defaultdict, deque
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


def get_secret_deltas_and_prices(seed):
    secret = seed
    price = secret % 10

    for _ in range(2000):
        secret = next_secret(secret)
        delta_price = (secret % 10) - price
        price = secret % 10
        yield price, delta_price


def get_sell_signals(seed):
    d = deque(maxlen=4)
    scores = defaultdict(int)

    for price, delta_price in get_secret_deltas_and_prices(seed):
        d.append(delta_price)
        if len(d) == 4:
            key = tuple(d)
            if key not in scores:
                scores[key] = price
    return scores


def get_max_bananas(sell_signals):
    scores = {}

    for signal in sell_signals:
        for key in signal:
            if key not in scores:
                total = 0
                for signal2 in sell_signals:
                    total += signal2[key]
                scores[key] = total

    return max(scores.values())


def solve(input_data):
    sell_signals = [get_sell_signals(int(line)) for line in input_data.splitlines()]
    return get_max_bananas(sell_signals)


def test_example():
    sample = "1\n2\n3\n2024"
    assert solve(sample) == 23


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
