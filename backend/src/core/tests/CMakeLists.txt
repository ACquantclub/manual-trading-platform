# Find CxxTest package
find_package(CxxTest REQUIRED)
if(NOT CXXTEST_FOUND)
    message(FATAL_ERROR "CxxTest not found!")
endif()

# Set test output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests)

# Find all test files
file(GLOB TEST_SOURCES "*.h")

# Generate test runners for each test file
foreach(TEST_FILE ${TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    CXXTEST_ADD_TEST(${TEST_NAME} ${TEST_NAME}.cpp ${TEST_FILE})
    target_link_libraries(${TEST_NAME} PRIVATE trading_core)
    target_include_directories(${TEST_NAME} 
        PRIVATE 
            ${CMAKE_SOURCE_DIR}/backend/include
    )
endforeach()