find_package(CxxTest REQUIRED)

# Set output directory for regression tests
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests/regression)

# Find all regression test files
file(GLOB REGRESSION_TEST_SOURCES "*.h")

# Generate test runners for each regression test file
foreach(TEST_FILE ${REGRESSION_TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    CXXTEST_ADD_TEST(Regression_${TEST_NAME} ${TEST_NAME}.cpp ${TEST_FILE})
    target_link_libraries(Regression_${TEST_NAME} PRIVATE trading_core)
    target_include_directories(Regression_${TEST_NAME} 
        PRIVATE 
            ${CMAKE_SOURCE_DIR}/backend/include
    )
    # Label as regression test
    set_tests_properties(Regression_${TEST_NAME} PROPERTIES LABELS "regression")
endforeach()