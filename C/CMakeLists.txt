cmake_minimum_required(VERSION 3.15)

project(VideoDownloader LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(VideoDownloader
    src/main.cpp
)

target_include_directories(VideoDownloader PRIVATE
    ${CMAKE_SOURCE_DIR}/include
)

# IMPORTANT : EXE autonome (Windows MSVC)
if(MSVC)
    set_property(TARGET VideoDownloader PROPERTY
        MSVC_RUNTIME_LIBRARY "MultiThreaded"
    )
endif()