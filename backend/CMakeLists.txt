project(trading_backend)

# Set backend-specific variables
set(BACKEND_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)
set(BACKEND_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Configure include directories
include_directories(${BACKEND_INCLUDE_DIR})

# Add the source directory
add_subdirectory(src)

# Configure testing
if(CXXTEST_FOUND)
    enable_testing()
    include_directories(${CXXTEST_INCLUDE_DIR})
endif()