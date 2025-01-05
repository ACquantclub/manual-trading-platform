cmake_minimum_required(VERSION 3.15)
project(manual_trading_platform)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Dynamically find Python
find_package(Python 3.11 EXACT REQUIRED COMPONENTS Interpreter Development)

# Dynamically find pybind11
execute_process(
    COMMAND ${Python_EXECUTABLE} -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

find_package(pybind11 CONFIG REQUIRED HINTS ${pybind11_DIR})

# Add the backend directory
add_subdirectory(backend)