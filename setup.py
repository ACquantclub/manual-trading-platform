from setuptools import setup, Extension
import pybind11
import sys
import os

# Get pybind11 include directories
pybind11_include = pybind11.get_include()

cpp_args = ['-std=c++17']
if sys.platform == 'linux':
    cpp_args.append('-fPIC')

ext_modules = [
    Extension(
        "trading",
        [
            "backend/bindings/bindings.cpp",
            "backend/src/core/Market.cpp",
            "backend/src/core/Order.cpp",
            "backend/src/core/OrderBook.cpp",
            "backend/src/core/Position.cpp",
            "backend/src/core/Trade.cpp"
        ],
        include_dirs=[
            "backend/include",
            pybind11_include,
        ],
        extra_compile_args=cpp_args,
        extra_link_args=['-luuid'],
        language='c++'
    ),
]

setup(
    name="trading",
    ext_modules=ext_modules,
    zip_safe=False,
    python_requires=">=3.11",
    install_requires=["pybind11>=2.10.0"],
)