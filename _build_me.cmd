setlocal
call setvc
set DISTUTILS_USE_SDK=yes
set py_vcruntime_redist=yes
py setup.py bdist_wheel
