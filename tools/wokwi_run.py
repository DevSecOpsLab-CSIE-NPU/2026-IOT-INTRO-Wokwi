#!/usr/bin/env python3
"""Run a MicroPython script on a Wokwi RFC2217 serial port with proper timing.

Before running the target script, modules from the repo-root ``lib/`` folder
and the project-local ``lib/`` folder are uploaded to the device filesystem.
The target script is also stored as ``main.py`` so the Wokwi REPL can see it
with ``os.listdir()`` and it can run after a soft reset.
"""
import os
import sys
import time
import serial

HOST = "localhost"
PORT = 4000

# repo root = parent of the tools/ directory that holds this file
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
    """Read until `marker` has appeared `count` times (or timeout)."""
    buf = b""
    deadline = time.monotonic() + timeout
    while buf.count(marker) < count and time.monotonic() < deadline:
        chunk = ser.read(ser.inWaiting() or 1)
        if chunk:
            buf += chunk
    return buf


def enter_raw_repl(ser):
    ser.write(b"\r\x02")
    time.sleep(0.05)
    ser.write(b"\r\x03\r\x03")     # Ctrl+C twice — interrupt running code
    # Wait for ">>> " to confirm REPL is ready before sending Ctrl+A.
    # Over RFC2217/TCP the banner may still be in-flight when we connect,
    # so a fixed sleep is not reliable.
    data = read_until(ser, b">>> ")
    if b">>> " not in data:
        print(f"Friendly REPL prompt not seen; trying raw REPL anyway. Got: {data!r}")
    time.sleep(0.05)
    ser.flushInput()
    ser.write(b"\r\x01")            # Ctrl+A — enter raw REPL
    data = read_until(ser, b"raw REPL; CTRL-B to exit\r\n>")
    if b"raw REPL; CTRL-B to exit\r\n>" not in data:
        raise RuntimeError(f"could not enter raw REPL; got: {data!r}")


def soft_reset(ser):
    ser.write(b"\x04")              # Ctrl+D — soft reset
    data = read_until(ser, b"raw REPL; CTRL-B to exit\r\n")
    if b"raw REPL; CTRL-B to exit\r\n" not in data:
        raise RuntimeError(f"soft reset failed; got: {data!r}")


def exec_raw(ser, code: bytes):
    r"""Execute code in raw REPL and return (stdout, stderr).

    Raw-REPL response after Ctrl+D is:
        b"OK" + <stdout> + b"\x04" + <stderr> + b"\x04" + b">"
    so we wait for *two* b"\x04" markers before parsing.
    """
    ser.write(code)
    ser.write(b"\x04")             # Ctrl+D — execute
    ack = read_until(ser, b"OK", timeout=5)
    if b"OK" not in ack:
        raise RuntimeError(f"device did not accept code; got: {ack!r}")
    out = read_n_markers(ser, b"\x04", 2, timeout=30)
    parts = out.split(b"\x04")
    stdout = parts[0] if len(parts) > 0 else b""
    stderr = parts[1] if len(parts) > 1 else b""
    return stdout, stderr


def put_file(ser, name: str, data: bytes):
    """Write `data` to a file named `name` on the device filesystem."""
    code = (
        "f=open(%r,'wb')\n" % name
        + "f.write(%r)\n" % data
        + "f.close()\n"
    ).encode()
    _, stderr = exec_raw(ser, code)
    if stderr.strip():
        raise RuntimeError(f"failed to upload {name}: {stderr!r}")


def mkdir(ser, name: str):
    """Create a directory on the device if it does not already exist."""
    code = (
        "import os\n"
        "try:\n"
        "    os.mkdir(%r)\n"
        "except OSError:\n"
        "    pass\n"
    ) % name
    code = code.encode()
    _, stderr = exec_raw(ser, code)
    if stderr.strip():
        raise RuntimeError(f"failed to create directory {name}: {stderr!r}")


def upload_libs(ser):
    """Upload every *.py in the repo-root lib/ folder to the device."""
    if not os.path.isdir(LIB_DIR):
        return
    for fname in sorted(os.listdir(LIB_DIR)):
        if not fname.endswith(".py"):
            continue
        with open(os.path.join(LIB_DIR, fname), "rb") as f:
            data = f.read()
        print(f"Uploading lib/{fname} ({len(data)} bytes) ...")
        put_file(ser, fname, data)


def upload_project_lib(ser, script_path: str):
    """Upload project-local lib/*.py to /lib for imports like from lib import fonts."""
    project_dir = os.path.dirname(os.path.abspath(script_path))
    project_lib = os.path.join(project_dir, "lib")
    if not os.path.isdir(project_lib):
        return
    mkdir(ser, "lib")
    for fname in sorted(os.listdir(project_lib)):
        if not fname.endswith(".py"):
            continue
        with open(os.path.join(project_lib, fname), "rb") as f:
            data = f.read()
        remote_name = "lib/" + fname
        print(f"Uploading {remote_name} ({len(data)} bytes) ...")
        put_file(ser, remote_name, data)


def exit_raw_repl(ser):
    ser.write(b"\r\x02")            # Ctrl+B — back to friendly REPL


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run a MicroPython script via Wokwi RFC2217")
    parser.add_argument("script", help="MicroPython script to run")
    parser.add_argument("--port", type=int, default=PORT, help=f"RFC2217 TCP port (default: {PORT})")
    parser.add_argument("--host", default=HOST, help=f"RFC2217 host (default: {HOST})")
    parser.add_argument("--upload-only", action="store_true",
                        help="upload main.py and project libs, then print os.listdir() without running main.py")
    args = parser.parse_args()

    script_path = args.script
    with open(script_path, "rb") as f:
        code = f.read()

    url = f"rfc2217://{args.host}:{args.port}"
    print(f"Connecting to {url} ...")
    ser = serial.serial_for_url(url, baudrate=115200, timeout=1)

    time.sleep(0.3)                 # let RFC2217 negotiate

    try:
        print("Entering raw REPL ...")
        enter_raw_repl(ser)
        print("Soft resetting ...")
        soft_reset(ser)
        upload_libs(ser)
        upload_project_lib(ser, script_path)
        print(f"Uploading main.py ({len(code)} bytes) ...")
        put_file(ser, "main.py", code)
        stdout, stderr = exec_raw(ser, b"import os\nprint(os.listdir())\n")
        if stdout.strip():
            sys.stdout.buffer.write(b"--- files ---\n")
            sys.stdout.buffer.write(stdout)
            if not stdout.endswith(b"\n"):
                sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.flush()
        if stderr.strip():
            sys.stderr.buffer.write(b"--- error ---\n")
            sys.stderr.buffer.write(stderr)
            sys.stderr.buffer.flush()
            sys.exit(1)
        if args.upload_only:
            return
        print(f"Running {script_path} ...")
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
