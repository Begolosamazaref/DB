from __future__ import annotations

import argparse
import os
import random
import signal
import socket
import subprocess
import threading
import time

from kvstore.client import KVClient


def writer(host: str, port: int, stop: threading.Event, acked: list[str]) -> None:
    client = KVClient(host, port)
    idx = 0
    while not stop.is_set():
        key = f"key_{idx}"
        try:
            client.set(key, f"value_{idx}")
        except OSError:
            time.sleep(0.05)
            continue
        acked.append(key)
        idx += 1
        time.sleep(0.01)


def killer(process: subprocess.Popen, stop: threading.Event) -> None:
    while not stop.is_set():
        time.sleep(random.uniform(0.05, 0.2))
        try:
            os.kill(process.pid, signal.SIGKILL)
        except OSError:
            return


def wait_for_server(host: str, port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.1)
    raise SystemExit("Server did not become ready in time")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chaos test: killer thread")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--command", required=True, help="Command to start server")
    parser.add_argument("--restart", action="store_true", help="Restart server and verify acked keys")
    parser.add_argument("--verify-timeout", type=float, default=5.0)
    args = parser.parse_args()

    process = subprocess.Popen(args.command.split())
    stop = threading.Event()
    acked: list[str] = []

    wait_for_server(args.host, args.port, timeout=5.0)

    writer_thread = threading.Thread(target=writer, args=(args.host, args.port, stop, acked), daemon=True)
    writer_thread.start()

    killer_thread = threading.Thread(target=killer, args=(process, stop), daemon=True)
    killer_thread.start()

    time.sleep(2)
    stop.set()
    writer_thread.join(timeout=1)
    killer_thread.join(timeout=1)

    if args.restart:
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            try:
                os.kill(process.pid, signal.SIGKILL)
            except OSError:
                pass
        process = subprocess.Popen(args.command.split())
        wait_for_server(args.host, args.port, timeout=args.verify_timeout)
        deadline = time.time() + args.verify_timeout
        client = KVClient(args.host, args.port)
        missing = set(acked)
        while missing and time.time() < deadline:
            for key in list(missing):
                if client.get(key) is not None:
                    missing.discard(key)
            time.sleep(0.1)
        if missing:
            raise SystemExit(f"Missing {len(missing)} acked keys after restart")
        process.terminate()
        process.wait(timeout=2)

    print(f"Acked keys count: {len(acked)}")


if __name__ == "__main__":
    main()
