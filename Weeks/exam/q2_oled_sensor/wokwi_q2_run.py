#!/usr/bin/env python3
"""Run the Q2 MicroPython project on a Wokwi RFC2217 serial port.

This project only needs its local lib/ssd1306.py.  The shared runner uploads
unrelated display drivers too, which can make Q2 fail before main.py starts.
"""
import argparse
import os
import sys
import time

import serial


HOST = "localhost"
PORT = 4001


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
    time.sleep(0.2)
    ser.write(b"\r\x02")
    time.sleep(0.2)
    ser.write(b"\r\x03\r\x03")
    read_until(ser, b">>> ", timeout=5)
    ser.flushInput()
    ser.write(b"\r\x01")
    data = read_until(ser, b"raw REPL; CTRL-B to exit\r\n>")
    if b"raw REPL; CTRL-B to exit\r\n>" not in data:
        raise RuntimeError(f"could not enter raw REPL; got: {data!r}")


def exec_raw(ser, code: bytes, timeout: float = 30.0):
    ser.write(code)
    ser.write(b"\x04")
    ack = read_until(ser, b"OK", timeout=10)
    if b"OK" not in ack:
        raise RuntimeError(f"device did not accept code; got: {ack!r}")
    out = read_n_markers(ser, b"\x04", 2, timeout=timeout)
    parts = out.split(b"\x04")
    stdout = parts[0] if len(parts) > 0 else b""
    stderr = parts[1] if len(parts) > 1 else b""
    return stdout, stderr


def put_file(ser, name: str, data: bytes):
    code = (
        "f=open(%r,'wb')\n" % name
        + "f.write(%r)\n" % data
        + "f.close()\n"
    ).encode()
    _, stderr = exec_raw(ser, code, timeout=60)
    if stderr.strip():
        raise RuntimeError(f"failed to upload {name}: {stderr!r}")


def stream_output(ser, seconds: float = 8.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        chunk = ser.read(ser.inWaiting() or 1)
        if chunk:
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()


def mkdir(ser, name: str):
    code = (
        "import os\n"
        "try:\n"
        "    os.mkdir(%r)\n"
        "except OSError:\n"
        "    pass\n"
    ) % name
    _, stderr = exec_raw(ser, code.encode())
    if stderr.strip():
        raise RuntimeError(f"failed to create directory {name}: {stderr!r}")


def upload_project_lib(ser, project_dir: str):
    lib_dir = os.path.join(project_dir, "lib")
    if not os.path.isdir(lib_dir):
        return
    mkdir(ser, "lib")
    for fname in sorted(os.listdir(lib_dir)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(lib_dir, fname)
        with open(path, "rb") as f:
            data = f.read()
        remote_name = "lib/" + fname
        print(f"Uploading {remote_name} ({len(data)} bytes) ...")
        put_file(ser, remote_name, data)


def main():
    parser = argparse.ArgumentParser(description="Run Q2 on Wokwi RFC2217")
    parser.add_argument("script")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--upload-only", action="store_true")
    args = parser.parse_args()

    script_path = os.path.abspath(args.script)
    project_dir = os.path.dirname(script_path)
    with open(script_path, "rb") as f:
        code = f.read()

    url = f"rfc2217://{args.host}:{args.port}"
    print(f"Connecting to {url} ...")
    ser = serial.serial_for_url(url, baudrate=115200, timeout=1)
    try:
        time.sleep(0.3)
        print("Entering raw REPL ...")
        enter_raw_repl(ser)
        upload_project_lib(ser, project_dir)
        print(f"Uploading main.py ({len(code)} bytes) ...")
        put_file(ser, "main.py", code)
        stdout, stderr = exec_raw(ser, b"import os\nprint(os.listdir())\n")
        if stdout.strip():
            sys.stdout.buffer.write(b"--- files ---\n")
            sys.stdout.buffer.write(stdout)
            if not stdout.endswith(b"\n"):
                sys.stdout.buffer.write(b"\n")
        if stderr.strip():
            sys.stderr.buffer.write(b"--- error ---\n")
            sys.stderr.buffer.write(stderr)
            sys.exit(1)
        if args.upload_only:
            return

        print("Soft resetting to run main.py ...")
        ser.write(b"\r\x02")
        time.sleep(0.2)
        ser.write(b"\x04")
        stream_output(ser, seconds=8)
    finally:
        if args.upload_only:
            ser.write(b"\r\x02")
        ser.close()


if __name__ == "__main__":
    main()
