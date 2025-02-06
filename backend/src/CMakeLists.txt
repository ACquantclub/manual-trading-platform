# Add core library
add_subdirectory(core)

if(CXXTEST_FOUND)
    add_subdirectory(system_tests)
endif()