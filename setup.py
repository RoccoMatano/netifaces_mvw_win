import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

################################################################################

if sys.platform != "win32":
    raise OSError("no support for non-Windows OS")

MIN_PY_VER = "3.8"

MIN_MAJOR, MIN_MINOR = map(int, MIN_PY_VER.split("."))
LIMITED_API = f"0x{MIN_MAJOR:02x}{MIN_MINOR:02x}0000"
LIMITED_API_TAG = f"cp{MIN_MAJOR}{MIN_MINOR}"

################################################################################

__version__ = "0.11.0"

iface_mod = Extension(
    "netifaces",
    sources=["src/entry.c", "src/netifaces.c"],
    libraries=["ws2_32", "iphlpapi", "kernel32", "ucrt", "vcruntime"],
    extra_compile_args=["/O1", "/Os", "/GS-"],
    extra_link_args = [
        "/manifest:no",
        "/emittoolversioninfo:no",
        "/nocoffgrpinfo",
        "/entry:entry_point",
        "/stub:src/roma.stub",
        "/opt:ref",
        "/opt:icf",
        "/section:.vanish,R",
        "/merge:.xdata=.vanish",
        "/merge:.pdata=.vanish",
        "/ignore:4253",
        "/ignore:4075",
        ],
    define_macros=[
        ("NETIFACES_VERSION", __version__),
        ("WIN32", 1),
        ("Py_LIMITED_API", LIMITED_API)
        ],
    py_limited_api=True
    )

################################################################################

class hacked_build_ext(build_ext):
    # hack to post-process ext after linking
    def build_extension(self, ext):
        ext_path = self.get_ext_fullpath(ext.name)
        super().build_extension(ext)
        subprocess.run(["squab.exe", ext_path])
        Path(ext_path + ".bak").unlink(missing_ok=True)

cmd_class = {'build_ext': hacked_build_ext}

################################################################################

setup (
    version=__version__,
    ext_modules=[iface_mod],
    options={'bdist_wheel': {'py_limited_api': LIMITED_API_TAG}},
    cmdclass=cmd_class,
    )

################################################################################
