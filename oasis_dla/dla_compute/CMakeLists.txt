cmake_minimum_required(VERSION 3.22)
project(compute_dla LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# requires: export CUDAQ_DIR=<cudaq_package>/lib/cmake/cudaq
find_package(CUDAQ REQUIRED)
# requires: uv add pybind11
find_package(pybind11 REQUIRED)

pybind11_add_module(compute_dla src/compute_dla.cpp)
target_compile_definitions(compute_dla PRIVATE CUDAQ_LIBRARY_MODE)
target_link_libraries(compute_dla PRIVATE cudaq::cudaq)
