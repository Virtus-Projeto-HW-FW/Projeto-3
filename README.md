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
