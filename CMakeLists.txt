cmake_minimum_required(VERSION 3.15)
project(manual_trading_platform)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define Python virtual environment paths
set(Python_ROOT_DIR "${CMAKE_SOURCE_DIR}/env")
set(Python_EXECUTABLE "${Python_ROOT_DIR}/bin/python3.11")

# Find Python and pybind11
find_package(Python 3.11 EXACT REQUIRED COMPONENTS Interpreter Development)
set(pybind11_DIR "${Python_ROOT_DIR}/lib/python3.11/site-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 CONFIG REQUIRED)

# Add the backend directory
add_subdirectory(backend)