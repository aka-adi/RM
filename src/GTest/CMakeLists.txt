cmake_minimum_required(VERSION 3.14)
project(test_rabit)

# GoogleTest requires at least C++14
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-g -O3")
include_directories(../)
link_directories(../../build /usr/lib/x86_64-linux-gnu)

include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(test_rabit test_rabit.cpp ../nicolas/util.h ../nicolas/util.cpp)
target_link_libraries(test_rabit bitmap pthread boost_filesystem boost_program_options boost_system urcu atomic tbb GTest::gtest_main)

include(GoogleTest)
gtest_add_tests(TARGET test_rabit)