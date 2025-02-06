pybind11_add_module(trading_py bindings.cpp)

target_link_libraries(trading_py PRIVATE trading_core)

set_target_properties(trading_py PROPERTIES 
    OUTPUT_NAME "trading"
    LIBRARY_OUTPUT_DIRECTORY "${PYTHON_MODULE_PATH}"
)

target_include_directories(trading_py PRIVATE 
    ${CMAKE_SOURCE_DIR}/backend/include
)