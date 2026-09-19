from __future__ import annotations

import argparse
import math
import socket
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="模拟 ATS600 向桥接程序发送连续 UDP 坐标")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=10000)
    parser.add_argument("--hz", type=float, default=20.0)
    args = parser.parse_args()

    interval = 1.0 / max(1.0, args.hz)
    start = time.monotonic()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print(f"模拟数据发送至 {args.host}:{args.port}，频率 {args.hz:g} Hz；Ctrl+C 停止")
        while True:
            elapsed = time.monotonic() - start
            # X moves at 2 mm/s; Y/Z include small slow changes.
            x = 1000.0 + 2.0 * elapsed
            y = 2000.0 + 0.2 * math.sin(elapsed)
            z = 3000.0 + 0.2 * math.cos(elapsed)
            message = f"ATS600 X={x:.6f} Y={y:.6f} Z={z:.6f}"
            sock.sendto(message.encode("ascii"), (args.host, args.port))
            time.sleep(interval)


if __name__ == "__main__":
    main()
