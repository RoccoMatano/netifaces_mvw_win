import os
import sys
import subprocess
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
    extra_compile_args=["/W2", "/O1", "/Os", "/GS-"],
    extra_link_args = [
        "/manifest:no",
        "/emittoolversioninfo:no",
        "/nocoffgrpinfo",
        "/entry:entry_point",
        "/stub:src/roma.stub",
        "/opt:ref",
        "/opt:icf",
        "/ignore:4253",
        "/section:.vanish,R",
        "/merge:.xdata=.vanish",
        "/merge:.pdata=.vanish",
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
    def build_extension(self, ext):
        super().build_extension(ext)
        ext_path = self.get_ext_fullpath(ext.name)
        try:
            subprocess.run(["squab", ext_path], check=True, shell=True)
            os.unlink(ext_path + ".bak")
        except Exception:
            pass

################################################################################

cmd_class = {"build_ext": hacked_build_ext}
setup (
    version=__version__,
    ext_modules=[iface_mod],
    options={"bdist_wheel": {"py_limited_api": LIMITED_API_TAG}},
    cmdclass=cmd_class,
    )

################################################################################
