# Add core library
add_subdirectory(core)

if(CXXTEST_FOUND)
    add_subdirectory(system_tests)
endif()

# Configure Python bindings
pybind11_add_module(trading ${CMAKE_SOURCE_DIR}/backend/bindings/bindings.cpp)

target_include_directories(trading 
    PRIVATE 
        ${CMAKE_SOURCE_DIR}/backend/include
)

target_link_libraries(trading 
    PRIVATE 
        trading_core
)

set_target_properties(trading PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
    PREFIX ""
    SUFFIX ".so"
)