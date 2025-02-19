import sys
import os
import subprocess
import argparse
from pathlib import Path
import setuptools.build_meta as backend

################################################################################

THIS_SCRIPT = Path(__file__).resolve()

################################################################################

def perform_action(args):
    if args.action not in ("build_sdist", "build_wheel"):
        raise ValueError(f"unknown action: '{args.action}'")
    getattr(backend, args.action)(str(THIS_SCRIPT.parent / "dist"))

################################################################################

def initiate_actions():
    os.environ['DISTUTILS_USE_SDK'] = 'yes'
    cmd = [
        "setvc",
        "default",
        "x64" if sys.maxsize > (2**31 - 1) else "x86",
        "&&",
        sys.executable,
        str(THIS_SCRIPT),
        "--action",
        "build_wheel",
        ]
    subprocess.run(cmd, check=True, shell=True)

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--action")
    args = parser.parse_args()
    if not args.action:
        initiate_actions()
    else:
        perform_action(args)

################################################################################
