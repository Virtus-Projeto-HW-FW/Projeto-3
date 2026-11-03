#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "protocol_defs.h"

/* Definições de pinos base da Revisão R6 */
#define PIN_MCU_ARM        4
#define PIN_MCU_HEARTBEAT  5
#define PIN_FAULT_N        6
#define PIN_ARM_REQUEST    7
#define PIN_ADC_CS_N      17
#define PIN_DAC_CS_N      20
#define PIN_DAC_LDAC_N    21

static void hw_init_safe(void) {
    /* RF-001: Boot seguro - relés desenergizados e CS inativos */
    gpio_init(PIN_MCU_ARM);
    gpio_set_dir(PIN_MCU_ARM, GPIO_OUT);
    gpio_put(PIN_MCU_ARM, 0);

    gpio_init(PIN_ADC_CS_N);
    gpio_set_dir(PIN_ADC_CS_N, GPIO_OUT);
    gpio_put(PIN_ADC_CS_N, 1);

    gpio_init(PIN_DAC_CS_N);
    gpio_set_dir(PIN_DAC_CS_N, GPIO_OUT);
    gpio_put(PIN_DAC_CS_N, 1);

    gpio_init(PIN_DAC_LDAC_N);
    gpio_set_dir(PIN_DAC_LDAC_N, GPIO_OUT);
    gpio_put(PIN_DAC_LDAC_N, 1);

    /* Entradas com pull-up/pull-down apropriados */
    gpio_init(PIN_FAULT_N);
    gpio_set_dir(PIN_FAULT_N, GPIO_IN);
    gpio_pull_up(PIN_FAULT_N);

    gpio_init(PIN_ARM_REQUEST);
    gpio_set_dir(PIN_ARM_REQUEST, GPIO_IN);

    /* Heartbeat de 10 Hz (RF-002) */
    gpio_init(PIN_MCU_HEARTBEAT);
    gpio_set_dir(PIN_MCU_HEARTBEAT, GPIO_OUT);
    gpio_put(PIN_MCU_HEARTBEAT, 0);
}

int main(void) {
    stdio_init_all();
    hw_init_safe();

    printf("RP2040 Photonic BIAS FW v%d.%d.%d inicializado em estado seguro.\n", 0, 1, 0);

    bool hb_state = false;
    while (true) {
        /* Onda quadrada de 10 Hz (T = 100 ms, 50 ms alto / 50 ms baixo) */
        hb_state = !hb_state;
        gpio_put(PIN_MCU_HEARTBEAT, hb_state);
        sleep_ms(50);
    }

    return 0;
}
