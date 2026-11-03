cmake_minimum_required(VERSION 3.13)

# Inicializa o Raspberry Pi Pico SDK
include(pico_sdk_import.cmake)

project(firmware_rp2040 C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(firmware_rp2040
    src/main.c
)

target_include_directories(firmware_rp2040 PRIVATE
    include
    ${CMAKE_CURRENT_SOURCE_DIR}/../common/include
)

target_link_libraries(firmware_rp2040 PRIVATE
    pico_stdlib
    hardware_gpio
    hardware_spi
    hardware_uart
)

pico_enable_stdio_uart(firmware_rp2040 1)
pico_enable_stdio_usb(firmware_rp2040 0)

pico_add_extra_outputs(firmware_rp2040)
