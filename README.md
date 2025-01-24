# Manual Trading Platform

A C++ trading platform with Python bindings.

## Contributing

### Test Structure
The project uses CxxTest and has three levels of testing:

1. **Unit Tests** (`backend/src/core/tests/`)
   - Run automatically during build
   - Test individual components
   - Run with: `make`

2. **System Tests** (`backend/src/system_tests/`)
   - Integration tests for complete workflows
   - Run with: `ctest -L system`

3. **Regression Tests** (`backend/regress/`)
   - Long-running tests for stability
   - Performance and load testing
   - Run with: `ctest -L regression`

### Building and Testing

```bash
# Setup build directory
mkdir build && cd build

# Configure CMake
cmake ..

# Build project and run unit tests
make

# Run all tests
ctest --output-on-failure

# Run specific test categories
ctest -L system        # system tests only
ctest -L regression   # regression tests only
ctest -LE unit       # everything except unit tests
```