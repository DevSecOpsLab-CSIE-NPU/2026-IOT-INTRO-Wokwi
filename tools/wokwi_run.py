#!/usr/bin/env python3
"""Run a MicroPython script on a Wokwi RFC2217 serial port."""

import os
import sys
import time
import serial

HOST = "localhost"
PORT = 4000

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_DIR = os.path.join(ROOT, "lib")


def read_until(ser, token: bytes, timeout: float = 10.0) -> bytes:
    buf = b""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        chunk = ser.read(ser.inWaiting() or 1)
        if chunk:
            buf += chunk
            if token in buf:
                return buf
    return buf


def read_n_markers(ser, marker: bytes, count: int, timeout: float = 30.0) -> bytes:
    buf = b""
    deadline = time.monotonic() + timeout
    while buf.count(marker) < count and time.monotonic() < deadline:
        chunk = ser.read(ser.inWaiting() or 1)
        if chunk:
            buf += chunk
    return buf


def enter_raw_repl(ser):
    ser.write(b"\r\x03\r\x03")
    data = read_until(ser, b">>> ", timeout=10.0)
    if b">>> " not in data:
        raise RuntimeError(f"REPL prompt not found; got: {data!r}")

    time.sleep(0.05)
    ser.flushInput()
    ser.write(b"\r\x01")

    data = read_until(ser, b"raw REPL; CTRL-B to exit\r\n>", timeout=10.0)
    if b"raw REPL; CTRL-B to exit\r\n>" not in data:
        raise RuntimeError(f"could not enter raw REPL; got: {data!r}")


def soft_reset(ser):
    ser.write(b"\x04")
    data = read_until(ser, b"raw REPL; CTRL-B to exit\r\n", timeout=10.0)
    if b"raw REPL; CTRL-B to exit\r\n" not in data:
        raise RuntimeError(f"soft reset failed; got: {data!r}")


def exec_raw(ser, code: bytes):
    """
    Execute code in raw REPL and return stdout, stderr.

    Raw REPL response:
        b"OK" + stdout + b"\\x04" + stderr + b"\\x04" + b">"
    """
    ser.write(code)
    ser.write(b"\x04")

    ack = read_until(ser, b"OK", timeout=10.0)
    if b"OK" not in ack:
        raise RuntimeError(f"device did not accept code; got: {ack!r}")

    out = read_n_markers(ser, b"\x04", 2, timeout=30.0)

    # 吃掉最後的 raw REPL prompt，避免下一次 exec_raw 讀到殘留的 b'>'
    read_until(ser, b">", timeout=3.0)

    parts = out.split(b"\x04")
    stdout = parts[0] if len(parts) > 0 else b""
    stderr = parts[1] if len(parts) > 1 else b""

    return stdout, stderr


def put_file(ser, name: str, data: bytes):
    """Write data to a file named name on the device filesystem."""
    code = (
        "f=open(%r,'wb')\n" % name
        + "f.write(%r)\n" % data
        + "f.close()\n"
    ).encode()

    _, stderr = exec_raw(ser, code)
    if stderr.strip():
        raise RuntimeError(f"failed to upload {name}: {stderr!r}")


def upload_libs(ser):
    """第一題只需要上傳 fonts.py。"""
    needed = ["fonts.py"]

    if not os.path.isdir(LIB_DIR):
        return

    for fname in needed:
        path = os.path.join(LIB_DIR, fname)

        if not os.path.exists(path):
            print(f"[WARN] lib/{fname} not found, skipped")
            continue

        with open(path, "rb") as f:
            data = f.read()

        print(f"Uploading lib/{fname} ({len(data)} bytes) ...")
        put_file(ser, fname, data)


def exit_raw_repl(ser):
    try:
        ser.write(b"\r\x02")
    except Exception:
        pass


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run a MicroPython script via Wokwi RFC2217")
    parser.add_argument("script", help="MicroPython script to run")
    parser.add_argument("--port", type=int, default=PORT, help=f"RFC2217 TCP port (default: {PORT})")
    parser.add_argument("--host", default=HOST, help=f"RFC2217 host (default: {HOST})")
    args = parser.parse_args()

    with open(args.script, "rb") as f:
        code = f.read()

    url = f"rfc2217://{args.host}:{args.port}"
    print(f"Connecting to {url} ...")

    ser = serial.serial_for_url(url, baudrate=115200, timeout=1)
    time.sleep(0.3)

    try:
        print("Entering raw REPL ...")
        enter_raw_repl(ser)

        print("Soft resetting ...")
        soft_reset(ser)

        upload_libs(ser)

        print(f"Running {args.script} ...")
        stdout, stderr = exec_raw(ser, code)

        if stdout.strip():
            sys.stdout.buffer.write(b"--- output ---\n")
            sys.stdout.buffer.write(stdout)
            if not stdout.endswith(b"\n"):
                sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.flush()

        if stderr.strip():
            sys.stderr.buffer.write(b"--- error ---\n")
            sys.stderr.buffer.write(stderr)
            sys.stderr.buffer.flush()
            sys.exit(1)

    finally:
        exit_raw_repl(ser)
        ser.close()


if __name__ == "__main__":
    main()