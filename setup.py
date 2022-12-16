import sys
from pathlib import Path
from setuptools import setup, Extension

################################################################################

if sys.platform != "win32":
    raise OSError("no support for non-Windows OS")

MIN_PY_VER = "3.6"

MIN_MAJOR, MIN_MINOR = map(int, MIN_PY_VER.split("."))
LIMITED_API = f"0x{MIN_MAJOR:02x}{MIN_MINOR:02x}0000"
LIMITED_API_TAG = f"cp{MIN_MAJOR}{MIN_MINOR}"

################################################################################

__version__ = "0.11.0"

iface_mod = Extension(
    "netifaces",
    sources=["entry.c", "netifaces.c"],
    libraries=["ws2_32", "iphlpapi", "kernel32", "ucrt", "vcruntime"],
    extra_compile_args=["/O1", "/Os", "/GS-",],
    extra_link_args = [
        "/manifest:no",
        "/emittoolversioninfo:no",
        "/nocoffgrpinfo",
        "/entry:entry_point",
        "/stub:roma.stub",
        "/section:.vanish,R",
        "/merge:.xdata=.vanish",
        "/merge:.pdata=.vanish",
        "/ignore:4253",
        ],
    define_macros=[
        ("NETIFACES_VERSION", __version__),
        ("WIN32", 1),
        ("Py_LIMITED_API", LIMITED_API)
        ],
    py_limited_api=True
    )

with open(Path(__file__).parent / "README.rst", "r") as fp:
    long_desc = fp.read()

################################################################################

setup (
    name="netifaces",
    version=__version__,
    zip_safe=True,
    description="Portable network interface information.",
    license="MIT License",
    long_description=long_desc,
    author="Alastair Houghton",
    author_email="alastair@alastairs-place.net",
    url="https://github.com/al45tair/netifaces",
    python_requires=f">={MIN_PY_VER}",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: System :: Networking",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        ],
    ext_modules=[iface_mod],
    options={'bdist_wheel': {'py_limited_api': LIMITED_API_TAG}},
    )

################################################################################
