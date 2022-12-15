import sys
from pathlib import Path
import subprocess
from sysconfig import get_config_var
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from wheel.bdist_wheel import bdist_wheel

if sys.platform != "win32":
    raise OSError("no support for non-Windows OS")

################################################################################

MIN_PY_VER = "3.6"

MIN_MAJOR, MIN_MINOR = map(int, MIN_PY_VER.split("."))
LIMITED_API = f"0x{MIN_MAJOR:02x}{MIN_MINOR:02x}0000"
IMPL_TAG_TO_BE_USED = f"cp{MIN_MAJOR}{MIN_MINOR}"
ABI_TAG_TO_BE_USED = f"abi{MIN_MAJOR}"

################################################################################

class hacked_bdist_wheel(bdist_wheel):
    # hack to ensure impl and abi tag can be set from the outside
    def get_tag(self):
        impl, abi_tag, plat_name = bdist_wheel.get_tag(self)
        impl = IMPL_TAG_TO_BE_USED
        abi_tag = ABI_TAG_TO_BE_USED
        return (impl, abi_tag, plat_name)

################################################################################

class hacked_build_ext(build_ext):
    # hack to ensure module name is "module.pyd" instead of
    # e.g. "module.cp38-win_amd64.pyd".
    def get_ext_filename(self, ext_name):
        ext_suffix = "." + get_config_var("EXT_SUFFIX").split(".")[-1]
        return ext_name + ext_suffix

    # hack for smaller executable
    ccflags = [
        "/nologo", "/O1", "/Os", "/W3", "/GL", "/DNDEBUG", "/MD", "/GF",
        "/GS-", "/Gy", "/permissive-", "/diagnostics:caret", "/Oy", "/GR-",
        "/Gw", "/volatileMetadata-",
        ]
    ldflags = [
        "/nologo", "/incremental:no", "/ltcg", "/dll", "/nxcompat",
        "/manifest:no", "/entry:entry_point", "/stub:roma.stub",
        "/emittoolversioninfo:no", "/release", "/last:.pdata", "/opt:ref",
        "/opt:icf", "/section:.vanish,R", "/merge:.xdata=.vanish",
        "/merge:.pdata=.vanish", "/ignore:4253", "/nocoffgrpinfo",
        ]
    def build_extension(self, ext):
        self.compiler.initialize(self.plat_name)
        self.compiler.compile_options = self.ccflags
        self.compiler._ldflags[self.compiler.SHARED_OBJECT, None] = self.ldflags
        build_ext.build_extension(self, ext)
        ext_name = self.get_ext_fullpath(ext.name)
        subprocess.run(["squab", ext_name])
        Path(ext_name + ".bak").unlink()

################################################################################

cmd_class = {
    "bdist_wheel": hacked_bdist_wheel,
    "build_ext": hacked_build_ext
    }

################################################################################

__version__ = "0.11.0"

iface_mod = Extension(
    "netifaces",
    sources=["entry.c", "netifaces.c"],
    libraries=["ws2_32", "iphlpapi", "kernel32", "ucrt", "vcruntime"],
    define_macros=[
        ("NETIFACES_VERSION", __version__),
        ("WIN32", 1),
        ("Py_LIMITED_API", LIMITED_API)
        ],
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
    cmdclass=cmd_class,
    )

################################################################################
