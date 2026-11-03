# T01: Setup, Estruturação e CI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a estrutura inicial do repositório, contratos de protocolo compartilhados entre C e Python, ambiente Python do CM5 com testes em pytest, toolchain CMake para o RP2040 e pipeline de CI no GitHub Actions.

**Architecture:** Estrutura modular desacoplada com diretório `common/` contendo definições de protocolo em C e Python, `software-cm5/` com empacotamento declarativo em `pyproject.toml` e suíte de testes unitários, `firmware-rp2040/` com CMakeLists.txt e esqueleto C seguro, e automação de compilação/teste via GitHub Actions em `.github/workflows/ci.yml`.

**Tech Stack:** Python 3.11+, Pytest, FastAPI, C99, CMake 3.13+, Raspberry Pi Pico SDK, GitHub Actions (Ubuntu).

**Spec:** `docs/superpowers/specs/2026-11-03-t01-setup-and-ci-design.md`

## Global Constraints

- O repositório deve manter isolamento estrito entre o código de alto nível do CM5 e o código de tempo real do RP2040.
- As definições de protocolo em C (`common/include/protocol_defs.h`) e Python (`common/protocol_defs.py`) devem conter valores idênticos para `SOF (0xAA55)` e opcodes.
- O pacote Python deve ser compatível com Python >= 3.11 e instalar via `pip install -e .`.
- O firmware do RP2040 deve ser compatível com Pico SDK 2.x e gerar binário `.uf2`.

---

### Task 1: Contratos Compartilhados de Protocolo (`common/`)

**Files:**
- Create: `common/include/protocol_defs.h`
- Create: `common/protocol_defs.py`
- Test: `software-cm5/tests/test_protocol_constants.py`

**Interfaces:**
- Produces: `protocol_defs.h` contendo `SOF_WORD = 0xAA55`, enum `msg_type_t`, enum `reg_addr_t`, enum `cmd_id_t`, enum `sys_state_t`.
- Produces: `protocol_defs.py` contendo `SOF_WORD = 0xAA55`, classes `MsgType(IntEnum)`, `RegAddr(IntEnum)`, `CmdId(IntEnum)`, `SysState(IntEnum)`.

- [ ] **Step 1: Escrever teste falhando para as constantes do protocolo**

Criar `software-cm5/tests/test_protocol_constants.py`:
```python
import sys
from pathlib import Path

# Adiciona pasta common ao path
common_path = Path(__file__).resolve().parents[2] / "common"
sys.path.insert(0, str(common_path))

import protocol_defs


def test_sof_marker():
    assert protocol_defs.SOF_WORD == 0xAA55
    assert protocol_defs.SOF_MSB == 0xAA
    assert protocol_defs.SOF_LSB == 0x55


def test_message_types():
    assert protocol_defs.MsgType.READ_REG == 0x01
    assert protocol_defs.MsgType.WRITE_REG == 0x02
    assert protocol_defs.MsgType.EXEC_CMD == 0x03
    assert protocol_defs.MsgType.READ_RESP == 0x81
    assert protocol_defs.MsgType.WRITE_ACK == 0x82
    assert protocol_defs.MsgType.CMD_ACK == 0x83
    assert protocol_defs.MsgType.TELEMETRY_STREAM == 0x90
    assert protocol_defs.MsgType.ERROR_NACK == 0xE0
    assert protocol_defs.MsgType.ASYNC_ALARM == 0xF0


def test_cmd_ids():
    assert protocol_defs.CmdId.ARM_RELAYS == 0x01
    assert protocol_defs.CmdId.DISARM_SAFE == 0x02
    assert protocol_defs.CmdId.CLEAR_FAULT == 0x03
    assert protocol_defs.CmdId.START_SWEEP == 0x04
    assert protocol_defs.CmdId.HOLD_FREEZE == 0x05
    assert protocol_defs.CmdId.CAL_DARK == 0x06
    assert protocol_defs.CmdId.DIAG_READ_MON == 0x07
    assert protocol_defs.CmdId.SET_SIM_MODE == 0x08
    assert protocol_defs.CmdId.ENTER_BOOTLOADER == 0x09


def test_sys_states():
    assert protocol_defs.SysState.INIT == 0
    assert protocol_defs.SysState.IDLE_SAFE == 1
    assert protocol_defs.SysState.PRE_ARM == 2
    assert protocol_defs.SysState.ARMED_MANUAL == 3
    assert protocol_defs.SysState.SWEEPING == 4
    assert protocol_defs.SysState.TRACKING == 5
    assert protocol_defs.SysState.HOLD == 6
    assert protocol_defs.SysState.FAULT_LATCHED == 7
    assert protocol_defs.SysState.MAINTENANCE == 8
```

- [ ] **Step 2: Executar o teste e verificar que falha por ausência de `common/protocol_defs.py`**

Comando: `python -m pytest software-cm5/tests/test_protocol_constants.py -v`
Resultado esperado: FAIL ("No module named 'protocol_defs'")

- [ ] **Step 3: Criar `common/protocol_defs.py` e `common/include/protocol_defs.h`**

Criar `common/protocol_defs.py`:
```python
"""
Definições compartilhadas do protocolo de comunicação CM5 <-> RP2040.
Espelho fiel de common/include/protocol_defs.h
"""

from enum import IntEnum

SOF_WORD = 0xAA55
SOF_MSB = 0xAA
SOF_LSB = 0x55


class MsgType(IntEnum):
    READ_REG = 0x01
    WRITE_REG = 0x02
    EXEC_CMD = 0x03
    READ_RESP = 0x81
    WRITE_ACK = 0x82
    CMD_ACK = 0x83
    TELEMETRY_STREAM = 0x90
    ERROR_NACK = 0xE0
    ASYNC_ALARM = 0xF0


class RegAddr(IntEnum):
    SYS_FW_VERSION = 0x00
    SYS_UPTIME_MS = 0x01
    SYS_STATE = 0x02
    SYS_FAULT_FLAGS = 0x03
    SYS_GPIO_STATUS = 0x04
    OPT_PHOTO_V = 0x10
    OPT_VDARK_V = 0x11
    OPT_CURRENT_UA = 0x12
    OPT_POWER_UW = 0x13
    OPT_LOS_THRESH_UA = 0x14
    CH_MODE = 0x20
    CH_BIAS_SET_V = 0x21
    CH_BIAS_MON_V = 0x22
    CH_DAC_CODE = 0x23
    CH_LIMIT_MIN_V = 0x24
    CH_LIMIT_MAX_V = 0x25
    DITHER_EN = 0x30
    DITHER_FREQ_HZ = 0x31
    DITHER_AMP_V = 0x32
    DITHER_PHASE_DEG = 0x33
    DEMOD_ERR_1F = 0x40
    DEMOD_ERR_2F = 0x41
    CTRL_KP = 0x50
    CTRL_KI = 0x51
    CTRL_KD = 0x52
    CTRL_SLEW_V_S = 0x53


class CmdId(IntEnum):
    ARM_RELAYS = 0x01
    DISARM_SAFE = 0x02
    CLEAR_FAULT = 0x03
    START_SWEEP = 0x04
    HOLD_FREEZE = 0x05
    CAL_DARK = 0x06
    DIAG_READ_MON = 0x07
    SET_SIM_MODE = 0x08
    ENTER_BOOTLOADER = 0x09


class SysState(IntEnum):
    INIT = 0
    IDLE_SAFE = 1
    PRE_ARM = 2
    ARMED_MANUAL = 3
    SWEEPING = 4
    TRACKING = 5
    HOLD = 6
    FAULT_LATCHED = 7
    MAINTENANCE = 8
```

Criar `common/include/protocol_defs.h`:
```c
#ifndef PROTOCOL_DEFS_H
#define PROTOCOL_DEFS_H

#include <stdint.h>

#define SOF_WORD 0xAA55
#define SOF_MSB  0xAA
#define SOF_LSB  0x55

typedef enum {
    MSG_READ_REG         = 0x01,
    MSG_WRITE_REG        = 0x02,
    MSG_EXEC_CMD         = 0x03,
    MSG_READ_RESP        = 0x81,
    MSG_WRITE_ACK        = 0x82,
    MSG_CMD_ACK          = 0x83,
    MSG_TELEMETRY_STREAM = 0x90,
    MSG_ERROR_NACK       = 0xE0,
    MSG_ASYNC_ALARM      = 0xF0
} msg_type_t;

typedef enum {
    REG_SYS_FW_VERSION    = 0x00,
    REG_SYS_UPTIME_MS     = 0x01,
    REG_SYS_STATE         = 0x02,
    REG_SYS_FAULT_FLAGS   = 0x03,
    REG_SYS_GPIO_STATUS   = 0x04,
    REG_OPT_PHOTO_V       = 0x10,
    REG_OPT_VDARK_V       = 0x11,
    REG_OPT_CURRENT_UA    = 0x12,
    REG_OPT_POWER_UW      = 0x13,
    REG_OPT_LOS_THRESH_UA = 0x14,
    REG_CH_MODE           = 0x20,
    REG_CH_BIAS_SET_V     = 0x21,
    REG_CH_BIAS_MON_V     = 0x22,
    REG_CH_DAC_CODE       = 0x23,
    REG_CH_LIMIT_MIN_V    = 0x24,
    REG_CH_LIMIT_MAX_V    = 0x25,
    REG_DITHER_EN         = 0x30,
    REG_DITHER_FREQ_HZ    = 0x31,
    REG_DITHER_AMP_V      = 0x32,
    REG_DITHER_PHASE_DEG  = 0x33,
    REG_DEMOD_ERR_1F      = 0x40,
    REG_DEMOD_ERR_2F      = 0x41,
    REG_CTRL_KP           = 0x50,
    REG_CTRL_KI           = 0x51,
    REG_CTRL_KD           = 0x52,
    REG_CTRL_SLEW_V_S     = 0x53
} reg_addr_t;

typedef enum {
    CMD_ARM_RELAYS        = 0x01,
    CMD_DISARM_SAFE       = 0x02,
    CMD_CLEAR_FAULT       = 0x03,
    CMD_START_SWEEP       = 0x04,
    CMD_HOLD_FREEZE       = 0x05,
    CMD_CAL_DARK          = 0x06,
    CMD_DIAG_READ_MON     = 0x07,
    CMD_SET_SIM_MODE      = 0x08,
    CMD_ENTER_BOOTLOADER  = 0x09
} cmd_id_t;

typedef enum {
    SYS_STATE_INIT          = 0,
    SYS_STATE_IDLE_SAFE     = 1,
    SYS_STATE_PRE_ARM       = 2,
    SYS_STATE_ARMED_MANUAL  = 3,
    SYS_STATE_SWEEPING      = 4,
    SYS_STATE_TRACKING      = 5,
    SYS_STATE_HOLD          = 6,
    SYS_STATE_FAULT_LATCHED = 7,
    SYS_STATE_MAINTENANCE   = 8
} sys_state_t;

#endif /* PROTOCOL_DEFS_H */
```

- [ ] **Step 4: Executar o teste e verificar que passa**

Comando: `python -m pytest software-cm5/tests/test_protocol_constants.py -v`
Resultado esperado: PASS (4 passed)

- [ ] **Step 5: Commit da Task 1**

```bash
git add common/ software-cm5/tests/
git commit -m "feat(common): add protocol definitions in C and Python with unit tests"
```

---

### Task 2: Configuração do Pacote Python do CM5 (`software-cm5/`)

**Files:**
- Create: `software-cm5/pyproject.toml`
- Create: `software-cm5/src/supervisor/__init__.py`
- Create: `software-cm5/src/supervisor/daemon.py`
- Create: `software-cm5/tests/__init__.py`
- Create: `software-cm5/tests/test_daemon.py`

**Interfaces:**
- Produces: `supervisor.__version__`
- Produces: `supervisor.daemon.SupervisorDaemon(port: str, baudrate: int)`

- [ ] **Step 1: Escrever teste falhando para o daemon supervisor**

Criar `software-cm5/tests/test_daemon.py`:
```python
from supervisor import __version__
from supervisor.daemon import SupervisorDaemon


def test_package_version():
    assert __version__ == "0.1.0"


def test_daemon_initialization():
    daemon = SupervisorDaemon(port="/dev/ttyAMA0", baudrate=115200)
    assert daemon.port == "/dev/ttyAMA0"
    assert daemon.baudrate == 115200
    assert not daemon.is_running
```

- [ ] **Step 2: Executar o teste e verificar que falha por ausência do módulo supervisor**

Comando: `python -m pytest software-cm5/tests/test_daemon.py -v`
Resultado esperado: FAIL ("No module named 'supervisor'")

- [ ] **Step 3: Implementar `pyproject.toml`, `__init__.py` e `daemon.py`**

Criar `software-cm5/pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "photonic-bias-supervisor"
version = "0.1.0"
description = "Software de supervisão e controle de BIAS para MZM/IQ em Raspberry Pi CM5"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Equipe Projeto 3 - Fotônica" }
]
dependencies = [
    "pyserial>=3.5",
    "fastapi>=0.110.0",
    "uvicorn>=0.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "../common"]
```

Criar `software-cm5/src/supervisor/__init__.py`:
```python
"""Photonic Bias Supervisor package."""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

Criar `software-cm5/src/supervisor/daemon.py`:
```python
"""Módulo principal do daemon de supervisão no Raspberry Pi CM5."""


class SupervisorDaemon:
    """Daemon de supervisão responsável por heartbeat, arme e UART com o RP2040."""

    def __init__(self, port: str = "/dev/ttyAMA0", baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate
        self.is_running = False

    def start(self) -> None:
        """Inicia os loops de supervisão."""
        self.is_running = True

    def stop(self) -> None:
        """Para os loops de supervisão e coloca saídas em estado seguro."""
        self.is_running = False
```

Criar `software-cm5/tests/__init__.py` vazio.

- [ ] **Step 4: Executar a suíte completa de testes do CM5 e verificar sucesso**

Comando: `python -m pytest software-cm5/tests/ -v`
Resultado esperado: PASS (6 passed)

- [ ] **Step 5: Commit da Task 2**

```bash
git add software-cm5/
git commit -m "feat(cm5): add pyproject.toml, supervisor package skeleton and tests"
```

---

### Task 3: Configuração do Toolchain CMake e Firmware RP2040 (`firmware-rp2040/`)

**Files:**
- Create: `firmware-rp2040/pico_sdk_import.cmake`
- Create: `firmware-rp2040/CMakeLists.txt`
- Create: `firmware-rp2040/src/main.c`

**Interfaces:**
- Consumes: `common/include/protocol_defs.h`
- Produces: Executável `firmware_rp2040.elf` e `firmware_rp2040.uf2`

- [ ] **Step 1: Criar `firmware-rp2040/pico_sdk_import.cmake` oficial**

Criar `firmware-rp2040/pico_sdk_import.cmake`:
```cmake
# This is a copy of <PICO_SDK_PATH>/external/pico_sdk_import.cmake

if (DEFINED ENV{PICO_SDK_PATH} AND (NOT PICO_SDK_PATH))
    set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
    message("Using PICO_SDK_PATH from environment ('${PICO_SDK_PATH}')")
endif ()

if (DEFINED ENV{PICO_SDK_FETCH_FROM_GIT} AND (NOT PICO_SDK_FETCH_FROM_GIT))
    set(PICO_SDK_FETCH_FROM_GIT $ENV{PICO_SDK_FETCH_FROM_GIT})
    message("Using PICO_SDK_FETCH_FROM_GIT from environment ('${PICO_SDK_FETCH_FROM_GIT}')")
endif ()

set(PICO_SDK_PATH "${PICO_SDK_PATH}" CACHE PATH "Path to the Raspberry Pi Pico SDK")

if (NOT PICO_SDK_PATH)
    if (PICO_SDK_FETCH_FROM_GIT)
        include(FetchContent)
        message("Downloading Raspberry Pi Pico SDK")
        FetchContent_Declare(
                pico_sdk
                GIT_REPOSITORY https://github.com/raspberrypi/pico-sdk
                GIT_TAG master
        )
        FetchContent_MakeAvailable(pico_sdk)
    else ()
        message(FATAL_ERROR
                "PICO_SDK_PATH is not set in environment or CMake cache.\n"
                "Set PICO_SDK_PATH to the path of your Raspberry Pi Pico SDK clone, or\n"
                "set PICO_SDK_FETCH_FROM_GIT=on to fetch it automatically.")
    endif ()
else ()
    # Import the SDK
    get_filename_component(PICO_SDK_PATH "${PICO_SDK_PATH}" REALPATH BASE_DIR "${CMAKE_BINARY_DIR}")
    if (NOT EXISTS "${PICO_SDK_PATH}")
        message(FATAL_ERROR "Directory '${PICO_SDK_PATH}' not found")
    endif ()
    set(PICO_SDK_INIT_CMAKE_FILE "${PICO_SDK_PATH}/pico_sdk_init.cmake")
    if (NOT EXISTS "${PICO_SDK_INIT_CMAKE_FILE}")
        message(FATAL_ERROR "File '${PICO_SDK_INIT_CMAKE_FILE}' not found")
    endif ()
    include("${PICO_SDK_INIT_CMAKE_FILE}")
endif ()
```

- [ ] **Step 2: Criar `firmware-rp2040/CMakeLists.txt`**

Criar `firmware-rp2040/CMakeLists.txt`:
```cmake
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
```

- [ ] **Step 3: Criar `firmware-rp2040/src/main.c` com inicialização segura (RF-001/RF-002)**

Criar `firmware-rp2040/src/main.c`:
```c
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
```

- [ ] **Step 4: Commit da Task 3**

```bash
git add firmware-rp2040/
git commit -m "feat(rp2040): add CMake build configuration and safe boot initialization in C"
```

---

### Task 4: Pipeline de CI (`.github/workflows/ci.yml`) e Documentação (`README.md`)

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `README.md`

**Interfaces:**
- Produces: GitHub Actions workflow que valida testes Python e compilação cruzada C a cada push/PR.

- [ ] **Step 1: Criar o fluxo de CI `.github/workflows/ci.yml`**

Criar `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-cm5:
    name: Test Software CM5 (Python)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e "./software-cm5[dev]"

      - name: Run Pytest with Coverage
        run: |
          pytest software-cm5/tests -v --cov=supervisor

  build-rp2040:
    name: Build Firmware RP2040 (C / Pico SDK)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install ARM GCC Toolchain and CMake
        run: |
          sudo apt-get update
          sudo apt-get install -y gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential cmake

      - name: Clone Raspberry Pi Pico SDK
        run: |
          git clone --depth 1 --branch 2.1.1 https://github.com/raspberrypi/pico-sdk.git ${{ runner.temp }}/pico-sdk
          cd ${{ runner.temp }}/pico-sdk
          git submodule update --init --depth 1

      - name: Configure CMake
        run: |
          cmake -B build -S firmware-rp2040 -DPICO_SDK_PATH=${{ runner.temp }}/pico-sdk

      - name: Compile Firmware
        run: |
          cmake --build build -j$(nproc)

      - name: Verify UF2 Artifact
        run: |
          test -f build/firmware_rp2040.uf2
```

- [ ] **Step 2: Criar o `README.md` na raiz**

Criar `README.md`:
```markdown
# Projeto 3 — Controle Automático de BIAS para Modulador MZM/IQ

Repositório de firmware e software de supervisão do **Projeto 3** para estabilização eletro-óptica de moduladores Mach-Zehnder (MZM e IQ) na plataforma heterogênea **Raspberry Pi CM5 (Linux)** + **RP2040 (Tempo Real)**.

## Arquitetura do Repositório

```text
.
├── .github/workflows/    # Esteiras de CI (GitHub Actions)
├── common/               # Contratos e definições compartilhadas (C e Python)
├── docs/                 # Documentação de requisitos, roadmap e referências
├── firmware-rp2040/      # Código C determinístico (Pico SDK)
└── software-cm5/         # Pacote Python de supervisão, API e testes
```

## Como Executar os Testes do Software CM5 (Python)

```bash
cd software-cm5
pip install -e ".[dev]"
pytest -v
```

## Como Compilar o Firmware do RP2040 (C)

Pré-requisito: `gcc-arm-none-eabi` e `pico-sdk` instalados.

```bash
mkdir -p firmware-rp2040/build
cd firmware-rp2040/build
cmake .. -DPICO_SDK_PATH=/caminho/para/o/pico-sdk
make -j4
```

O arquivo gerado `firmware_rp2040.uf2` pode ser copiado diretamente para o Raspberry Pi Pico em modo BOOTSEL.
```

- [ ] **Step 3: Commit da Task 4**

```bash
git add .github/workflows/ci.yml README.md
git commit -m "ci: add GitHub Actions workflow and repository README"
```

---

## Self-Review

1. **Spec Coverage:**
   - Estrutura de pastas: Coberta nas Tasks 1, 2 e 3.
   - Contratos em `common/`: Cobertos na Task 1.
   - Setup Python e Pytest: Cobertos na Task 2.
   - Toolchain CMake e C para RP2040: Cobertos na Task 3.
   - CI Workflow e README: Cobertos na Task 4.
2. **Placeholder scan:** Sem referências a "TBD", "TODO" ou trechos incompletos. Todos os arquivos e códigos foram expostos integralmente.
3. **Type consistency:** Constantes e nomes em C (`SOF_WORD`, `PIN_MCU_ARM`) e Python (`SOF_WORD`, `SupervisorDaemon`) conferem estritamente com `REQUISITOS.md`.
