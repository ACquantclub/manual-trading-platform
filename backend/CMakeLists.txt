cmake_minimum_required(VERSION 3.15)
project(trading_platform)
add_definitions(-DPy_BUILD_CORE)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define the Python virtual environment paths
set(Python_ROOT_DIR "${CMAKE_SOURCE_DIR}/../env")
set(Python_EXECUTABLE "${Python_ROOT_DIR}/bin/python3.11")

# Find Python and pybind11
find_package(Python 3.11 EXACT REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)

# Include directories
include_directories(${Python_INCLUDE_DIRS})
include_directories(${CMAKE_SOURCE_DIR}/include)

# Add the trading logic library
add_library(trading_logic STATIC src/trading_logic.cpp)
target_include_directories(trading_logic PUBLIC ${CMAKE_SOURCE_DIR}/include)

# Add the pybind11 module
pybind11_add_module(trading_core src/binding.cpp)

# Link the trading logic library to the pybind11 module
target_link_libraries(trading_core PRIVATE trading_logic)

# Output paths
set_target_properties(trading_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build
    PREFIX ""
    SUFFIX ".so"
)