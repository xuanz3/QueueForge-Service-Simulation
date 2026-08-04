cmake_minimum_required(VERSION 3.24)
project(queueforge_simulation VERSION 0.2.0 LANGUAGES CXX)

option(QUEUEFORGE_ENABLE_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)
option(QUEUEFORGE_WARNINGS_AS_ERRORS "Treat compiler warnings as build failures" OFF)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

function(queueforge_target_defaults target)
    target_compile_options(${target} PRIVATE
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
        -Wshadow
    )

    if(QUEUEFORGE_WARNINGS_AS_ERRORS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(${target} PRIVATE -Werror)
    endif()

    if(QUEUEFORGE_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(${target} PRIVATE
            -fsanitize=address,undefined
            -fno-omit-frame-pointer
        )
        target_link_options(${target} PRIVATE
            -fsanitize=address,undefined
            -fno-omit-frame-pointer
        )
    endif()
endfunction()

add_library(queueforge_engine
    src/health.cpp
    src/json.cpp
    src/json_io.cpp
    src/model.cpp
    src/random.cpp
    src/simulator.cpp
    src/waiting_queue.cpp
)
target_include_directories(queueforge_engine PUBLIC include)
queueforge_target_defaults(queueforge_engine)

add_executable(queueforge-sim src/main.cpp)
target_link_libraries(queueforge-sim PRIVATE queueforge_engine)
queueforge_target_defaults(queueforge-sim)

if(NOT QUEUEFORGE_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_link_options(queueforge-sim PRIVATE
        -static-libgcc
        -static-libstdc++
    )
endif()

enable_testing()

function(queueforge_add_test target source)
    add_executable(${target} ${source})
    target_link_libraries(${target} PRIVATE queueforge_engine)
    target_include_directories(${target} PRIVATE tests)
    queueforge_target_defaults(${target})
    add_test(NAME ${target} COMMAND ${target})
endfunction()

queueforge_add_test(queueforge-health-tests tests/health_test.cpp)
queueforge_add_test(queueforge-json-tests tests/json_test.cpp)
queueforge_add_test(queueforge-json-io-tests tests/json_io_test.cpp)
queueforge_add_test(queueforge-waiting-queue-tests tests/waiting_queue_test.cpp)
queueforge_add_test(queueforge-simulator-tests tests/simulator_test.cpp)
