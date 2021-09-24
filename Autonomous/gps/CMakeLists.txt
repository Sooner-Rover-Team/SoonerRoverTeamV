cmake_minimum_required(VERSION 2.8)

project(gps_read)

include_directories("${PROJECT_SOURCE_DIR}")
add_subdirectory("${PROJECT_SOURCE_DIR}/lib")

# set(HEADER_FILES )

add_executable(gps_read main.cpp ${HEADER_FILES})

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -pthread")

target_link_libraries( gps_read gps )