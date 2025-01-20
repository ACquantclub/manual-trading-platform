# Core library configuration
add_library(trading_core STATIC 
    Order.cpp
    Position.cpp
)

# Set include directories for the core library
target_include_directories(trading_core
    PUBLIC 
        ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link external dependencies
target_link_libraries(trading_core
    PRIVATE 
        ${UUID_LIBRARIES}
)

# Add tests subdirectory if CxxTest is found
if(CXXTEST_FOUND)
    add_subdirectory(tests)
endif()

# Set compile features
target_compile_features(trading_core PUBLIC cxx_std_17)

# Set properties
set_target_properties(trading_core PROPERTIES
    CXX_EXTENSIONS OFF
    POSITION_INDEPENDENT_CODE ON
)