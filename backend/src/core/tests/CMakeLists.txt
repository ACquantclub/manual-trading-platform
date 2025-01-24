# Find CxxTest package
find_package(CxxTest REQUIRED)
if(NOT CXXTEST_FOUND)
    message(FATAL_ERROR "CxxTest not found!")
endif()

# Set test output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests)

# Find all test files
file(GLOB TEST_SOURCES "*.h")

# Create list for unit tests
set(UNIT_TESTS "")

# Generate test runners for each test file
foreach(TEST_FILE ${TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    CXXTEST_ADD_TEST(${TEST_NAME} ${TEST_NAME}.cpp ${TEST_FILE})
    target_link_libraries(${TEST_NAME} PRIVATE trading_core)
    target_include_directories(${TEST_NAME} 
        PRIVATE 
            ${CMAKE_SOURCE_DIR}/backend/include
    )
    # Label as unit test
    set_tests_properties(${TEST_NAME} PROPERTIES LABELS "unit")
    
    # Add to unit tests list
    list(APPEND UNIT_TESTS ${TEST_NAME})
endforeach()

# Custom target that builds and runs unit tests
add_custom_target(run_unit_tests ALL
    COMMAND ${CMAKE_CTEST_COMMAND} -L unit --output-on-failure
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    DEPENDS ${UNIT_TESTS}
    COMMENT "Running unit tests..."
)