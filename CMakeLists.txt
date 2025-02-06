cmake_minimum_required(VERSION 3.15)
project(manual_trading_platform VERSION 0.1.0)

# Global settings
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Set visibility settings for all targets
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN YES)

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Dependencies
find_package(Python 3.11 EXACT REQUIRED COMPONENTS Interpreter Development)
find_package(PkgConfig REQUIRED)
pkg_check_modules(UUID REQUIRED uuid)

# pybind11 setup - use Python's installed version
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE _pybind11_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
set(pybind11_DIR ${_pybind11_dir})
find_package(pybind11 CONFIG REQUIRED)

# Set Python module path
set(PYTHON_MODULE_PATH "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/python")
file(MAKE_DIRECTORY ${PYTHON_MODULE_PATH})

# Testing
find_package(CxxTest)
enable_testing()

# Main project
add_subdirectory(backend)
add_subdirectory(backend/bindings)