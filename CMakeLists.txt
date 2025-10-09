cmake_minimum_required(VERSION 3.16.0)

option(test "Build all tests." OFF) # Makes boolean 'test' available.

set(LIB_NAME bitmap)
set(PROJECT_NAME nicolas)

project(${PROJECT_NAME})

include_directories(${CMAKE_SOURCE_DIR}/src)

# Linux specific code
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    # RABIT relies on RCU to lazily free nodes. The RCU mechanism, however, incurs the invalid-offsetof warning. So we disable it.
    # The fastbit lib incurs a deprecated-declarations warning. So we disable it since we don't want to touch fastbit's code anyway.
    set(CMAKE_CXX_FLAGS "-g -ggdb -O3 -std=gnu++17 -fPIC -Wno-invalid-offsetof -Wno-deprecated-declarations")
    # set(CMAKE_CXX_FLAGS "-g -O3 -std=gnu++17 -fPIC")

    include_directories("/usr/include/x86_64-linux-gnu")
    include_directories("/usr/local/include")
    ADD_DEFINITIONS( "-DLINUX" )
    set(BOOST_LIBRARYDIR /usr/lib/x86_64-linux-gnu)
    set(BOOST_INCLUDEDIR /usr/include)
    set(Boost_NO_SYSTEM_PATHS on)
    find_package(Boost COMPONENTS filesystem program_options system REQUIRED)
ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")


# get GHz from /proc/cpuinfo
execute_process(
    COMMAND ${CMAKE_SOURCE_DIR}/get_cpu_ghz.sh
    OUTPUT_VARIABLE CPU_GHZ
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

add_definitions(-DCPU_GHZ=${CPU_GHZ})


find_library(URCU_LIBRARIES 
                NAMES urcu
                HINTS "/usr/lib/x86_64-linux-gnu;/usr/local/lib")

# fastbit
set(FASTBIT_OBJ src/fastbit/bitvector_base.h
                  src/fastbit/bitvector.cpp src/fastbit/bitvector.h
                  src/fastbit/bitvector8.cpp src/fastbit/bitvector8.h
                  src/fastbit/bitvector16.cpp src/fastbit/bitvector16.h
                  src/fastbit/fileManager.cpp src/fastbit/fileManager.h
                  src/fastbit/resource.cpp src/fastbit/resource.h
                  src/fastbit/util.cpp src/fastbit/util.h
                  src/fastbit/array_t.cpp src/fastbit/array_t.h)

# bitmap
set(BASE_TABLE_OBJ src/bitmaps/base_table.h src/bitmaps/base_table.cpp)
set(NAIVE_OBJ src/bitmaps/naive/table.h src/bitmaps/naive/table.cpp)
set(UCB_OBJ src/bitmaps/ucb/table.h src/bitmaps/ucb/table.cpp)
set(UB_OBJ src/bitmaps/ub/table.h src/bitmaps/ub/table.cpp)
# set(NBUB_SOURCE_FILES src/cubit/table.h src/cubit/table.cpp src/cubit/table_lk.h src/cubit/table_lk.cpp)
set(RABIT_OBJ src/bitmaps/rabit/segBtv.h src/bitmaps/rabit/segBtv.cpp 
        src/bitmaps/rabit/table.h src/bitmaps/rabit/table.cpp)
set(UTIL_OBJ src/nicolas/util.h src/nicolas/util.cpp)
add_library(bitmap STATIC ${FASTBIT_OBJ} ${BASE_TABLE_OBJ} ${NAIVE_OBJ} ${UCB_OBJ} ${UB_OBJ} ${RABIT_OBJ} ${UTIL_OBJ})
target_link_libraries(bitmap pthread atomic ${Boost_LIBRARIES} ${URCU_LIBRARIES})

# main
set(NICOLAS src/nicolas/nicolas.cpp)
set(PERF_OBJ src/GTest/perf.h src/GTest/perf.cpp) 
set(GTEST_OBJ src/nicolas/gen_bitmap.h src/nicolas/gen_bitmap.cpp)
add_executable(nicolas ${NICOLAS} ${PERF_OBJ} ${GTEST_OBJ})
target_link_libraries(nicolas bitmap pthread atomic ${Boost_LIBRARIES} ${URCU_LIBRARIES})


################################
# Testing
################################
#if (test)
#  # This adds another subdirectory, which has 'project(gtest)'.
#  add_subdirectory(src/gtest)
#
#  enable_testing()
#
#  # Include the gtest library. gtest_SOURCE_DIR is available due to
#  # 'project(gtest)' above.
#  # include_directories(${gtest_SOURCE_DIR}/include ${gtest_SOURCE_DIR})
#
#  ##############
#  # Unit Tests
#  ##############
#  add_executable(runUnitTests src/nicolas/test/test_common.cpp)
#
#  # Standard linking to gtest stuff.
#  target_link_libraries(runUnitTests gtest gtest_main)
#
#  # Extra linking for the project.
#  target_link_libraries(runUnitTests ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
#
#  # You can also omit NAME and COMMAND. The second argument could be some other
#  # test executable.
#  add_test(common-test runUnitTests)
#endif()
