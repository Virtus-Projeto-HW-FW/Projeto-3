# Especificação Técnica de Design — Issue #1 (T01): Setup, Toolchain e CI

- **Data:** 2026-11-03
- **Issue:** Virtus-Projeto-HW-FW/Projeto-3 #1 (`[T01] Estruturar repositório, build CMake/Pico SDK, ambiente Python e pipeline CI`)
- **Responsáveis:** Responsável A (Software CM5) e Responsável B (Firmware RP2040)
- **Status:** Aprovado para Planejamento de Implementação

---

## 1. Contexto e Objetivos

O Projeto 3 consiste no sistema de controle automático de BIAS para moduladores eletro-ópticos (MZM/IQ), distribuído entre dois processadores:
1. **RP2040 (Raspberry Pi Pico):** Tempo real, laço determinístico de 1 kHz, síntese de dither, demodulação lock-in (1f/2f) e controle de segurança de hardware.
2. **CM5 (Raspberry Pi Compute Module 5):** Supervisão Linux, daemon de heartbeat (10 Hz), controle de arme de relés, backend API (FastAPI) e interface Web.

A tarefa **T01** estabelece a infraestrutura fundacional do repositório para permitir o trabalho desacoplado e simultâneo de ambos os desenvolvedores, assegurando a compilação cruzada do firmware RP2040 e a execução de testes automatizados em Python através de Integração Contínua (CI).

---

## 2. Estrutura de Diretórios do Repositório

O repositório `Projeto 3 - FW/` será estruturado da seguinte forma:

```text
Projeto 3 - FW/
├── .github/
│   └── workflows/
│       └── ci.yml
├── common/
│   ├── include/
│   │   └── protocol_defs.h
│   └── protocol_defs.py
├── firmware-rp2040/
│   ├── CMakeLists.txt
│   ├── pico_sdk_import.cmake
│   └── src/
│       └── main.c
├── software-cm5/
│   ├── pyproject.toml
│   ├── src/
│   │   └── supervisor/
│   │       ├── __init__.py
│   │       └── daemon.py
│   └── tests/
│       ├── __init__.py
│       └── test_protocol_constants.py
├── docs/
│   ├── REQUISITOS.md
│   ├── ROADMAP.md
│   └── referencia/
└── README.md
```

---

## 3. Especificação dos Componentes

### 3.1. Módulo Compartilhado (`common/`)
- **Objetivo:** Manter a paridade exata de constantes, opcodes e endereços de registradores definidos na Seção 5 de `REQUISITOS.md`.
- **`protocol_defs.h`:**
  - `SOF_MSB = 0xAA`, `SOF_LSB = 0x55`
  - Enum `msg_type_t`: `READ_REG (0x01)`, `WRITE_REG (0x02)`, `EXEC_CMD (0x03)`, `READ_RESP (0x81)`, `WRITE_ACK (0x82)`, `CMD_ACK (0x83)`, `TELEMETRY_STREAM (0x90)`, `ERROR_NACK (0xE0)`, `ASYNC_ALARM (0xF0)`.
  - Enum `reg_addr_t`: Mapeamento de registradores de `0x00` a `0x53`.
  - Enum `cmd_id_t`: Comandos de ação (`CMD_ARM_RELAYS = 0x01`, `CMD_DISARM_SAFE = 0x02`, etc.).
  - Enum `sys_state_t`: Estados da máquina de tempo real (`INIT = 0`, `IDLE_SAFE = 1`, ..., `MAINTENANCE = 8`).
- **`protocol_defs.py`:**
  - Classes `IntEnum` idênticas às definições C para consumo no ambiente Python do CM5.

### 3.2. Firmware RP2040 (`firmware-rp2040/`)
- **`pico_sdk_import.cmake`:** Script padrão Raspberry Pi Pico que busca o SDK local ou o inicializa.
- **`CMakeLists.txt`:**
  - Versão mínima do CMake: 3.13.
  - Alvo: `firmware_rp2040`.
  - Inclusão dos diretórios `include/` e `../common/include/`.
  - Link com bibliotecas padrão do Pico SDK (`pico_stdlib`, `hardware_gpio`, `hardware_spi`, `hardware_uart`).
  - Geração de saídas `.elf`, `.bin` e `.uf2`.
- **`src/main.c`:**
  - Ponto de entrada com configuração segura inicial (conforme `RF-001`): `MCU_ARM` (`GP4`) em nível baixo, Chip Selects inativos.
  - Laço principal inicial com temporização e sinalização de *heartbeat* em `GP5`.

### 3.3. Software CM5 (`software-cm5/`)
- **`pyproject.toml`:**
  - Metadados do projeto `photonic-bias-supervisor` (versão 0.1.0).
  - Dependências principais: `pyserial>=3.5`, `fastapi>=0.110.0`, `uvicorn>=0.28.0`, `pydantic>=2.0.0`.
  - Dependências de desenvolvimento e teste: `pytest>=8.0.0`, `pytest-cov>=4.1.0`, `pytest-asyncio>=0.23.0`.
  - Configuração do `pytest` com caminho de busca incluindo `src` e `../common`.
- **`src/supervisor/daemon.py`:**
  - Classe `SupervisorDaemon` contendo inicialização com parâmetros de porta serial, taxa de baud (115200) e status de execução.
- **`tests/test_protocol_constants.py`:**
  - Casos de teste que validam as faixas e valores de `SOF`, enums de mensagens, comandos e estados.

### 3.4. Pipeline de Integração Contínua (`.github/workflows/ci.yml`)
- Disparado em eventos de `push` e `pull_request` no branch `main`.
- **Job `test-cm5`:**
  - Runner: `ubuntu-latest`.
  - Python: 3.11.
  - Passos: Instalação das dependências com `pip install -e .[dev]` ou `pip install -r` e execução de `pytest -v --cov=supervisor`.
- **Job `build-rp2040`:**
  - Runner: `ubuntu-latest`.
  - Instalação de pacotes: `gcc-arm-none-eabi`, `libnewlib-arm-none-eabi`, `cmake`, `build-essential`.
  - Checkout do `pico-sdk` (tag estável `2.1.1` ou `1.5.1`).
  - Configuração com `cmake -DPICO_SDK_PATH=...` e compilação com `make`.
  - Validação da existência do arquivo `firmware_rp2040.uf2`.

---

## 4. Critérios de Aceitação da Tarefa T01

1. A árvore de diretórios contém todas as pastas especificadas sem arquivos temporários ou desnecessários.
2. A suíte de testes em `software-cm5` executa com sucesso localmente via `pytest` com 100% de aprovação.
3. O build do firmware RP2040 compila sem erros ou avisos críticos gerando o binário `.uf2`.
4. Os jobs `test-cm5` e `build-rp2040` no GitHub Actions passam com status verde.
