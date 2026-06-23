#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "2026-IOT-INTRO-Wokwi" / "tools"
sys.path.insert(0, str(TOOLS))

import serial
import wokwi_run


def main():
    parser = argparse.ArgumentParser(description="Run final exam question 1 on Wokwi")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=4000)
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    url = f"rfc2217://{args.host}:{args.port}"
    print(f"Connecting to {url} ...")
    ser = serial.serial_for_url(url, baudrate=115200, timeout=1)
    time.sleep(0.3)

    try:
        print("Entering raw REPL ...")
        wokwi_run.enter_raw_repl(ser)
        print("Soft resetting ...")
        wokwi_run.soft_reset(ser)

        for name in ("ili9341.py", "fonts.py"):
            data = (base / name).read_bytes()
            print(f"Uploading {name} ({len(data)} bytes) ...")
            wokwi_run.put_file(ser, name, data)

        print("Running main.py ...")
        stdout, stderr = wokwi_run.exec_raw(ser, (base / "main.py").read_bytes())
        if stdout.strip():
            sys.stdout.buffer.write(stdout)
            if not stdout.endswith(b"\n"):
                sys.stdout.buffer.write(b"\n")
        if stderr.strip():
            sys.stderr.buffer.write(stderr)
            raise SystemExit(1)
    finally:
        wokwi_run.exit_raw_repl(ser)
        ser.close()


if __name__ == "__main__":
    main()
