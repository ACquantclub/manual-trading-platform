find_package(CxxTest REQUIRED)

# Set output directory for system tests
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests/system)

# Find all system test files
file(GLOB SYSTEM_TEST_SOURCES "*.h")

# Generate test runners for each system test file
foreach(TEST_FILE ${SYSTEM_TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    CXXTEST_ADD_TEST(System_${TEST_NAME} ${TEST_NAME}.cpp ${TEST_FILE})
    target_link_libraries(System_${TEST_NAME} PRIVATE trading_core)
    target_include_directories(System_${TEST_NAME} 
        PRIVATE 
            ${CMAKE_SOURCE_DIR}/backend/include
    )
    # Label as system test
    set_tests_properties(System_${TEST_NAME} PROPERTIES LABELS "system")
endforeach()