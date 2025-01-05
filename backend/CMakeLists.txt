# Include directories for the backend
include_directories(${Python_INCLUDE_DIRS})
include_directories(${CMAKE_SOURCE_DIR}/backend/include)

# Add the trading logic library
add_library(trading_logic STATIC src/trading_logic.cpp)
target_include_directories(trading_logic PUBLIC ${CMAKE_SOURCE_DIR}/backend/include)

# Add the pybind11 module
pybind11_add_module(trading_core src/binding.cpp)

# Link the trading logic library to the pybind11 module
target_link_libraries(trading_core PRIVATE trading_logic)

# Output paths for backend artifacts
set_target_properties(trading_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/backend/build
    PREFIX ""
    SUFFIX ".so"
)
