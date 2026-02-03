from __future__ import annotations

import argparse
import random
import time

from kvstore.client import KVClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Write throughput benchmark")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--prepopulate", type=int, default=0)
    args = parser.parse_args()

    client = KVClient(args.host, args.port)

    for idx in range(args.prepopulate):
        client.set(f"pre_{idx}", random.randint(0, 1_000_000))

    start = time.perf_counter()
    for idx in range(args.count):
        client.set(f"k{idx}", random.randint(0, 1_000_000))
    duration = time.perf_counter() - start

    print(f"writes={args.count} duration={duration:.3f}s throughput={args.count / duration:.1f} ops/s")


if __name__ == "__main__":
    main()
