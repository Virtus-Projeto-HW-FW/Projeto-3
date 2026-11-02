# Especificação de Requisitos de Firmware — Projeto 3 (Controle Automático de BIAS para MZM/IQ)

> **Status do Documento:** Versão 1.0 (Itens não definidos nos documentos de origem estão explicitamente marcados como **`[PROPOSTA / A CONFIRMAR]`** para validação da equipe).
> **Fontes de Referência:**
> - Especificação Acadêmica: `docs/referencia/Propostas_Projetos_PCB_Fotonica_v1_1.pdf` (Seções 1–4 e 7–11)
> - Hardware Revisão R6 (Somente Leitura): `../Projeto 3 - HW/Projeto3-CM5-RP2040-MZM/` (`Relatorio_CM5_RP2040_MZM.docx`, `Ensaios_de_Bancada_CM5_Photonic_Bias.docx`, `Relatorio_LTspice_CM5_RP2040_MZM.docx`, `Conectividade_pinos_R6.csv`, `BOM_PCB_R6.csv`)

---

## 1. Visão Geral e Divisão de Responsabilidades

O sistema de controle automático de ponto de operação (*BIAS*) para moduladores eletro-ópticos Mach-Zehnder (MZM simples de 1 canal no escopo **Mínimo** e modulador IQ de 3 canais — $I$, $Q$ e $\Phi$ — no escopo **Recomendado**) utiliza uma arquitetura heterogênea composta por:

- **Responsável A — Software de Supervisão no Raspberry Pi CM5 (`MOD_CM5` — Linux):**
  Responsável por inicialização coordenada, geração de *heartbeat* do supervisor (`GPIO4`), solicitação de arme (`GPIO17`), comunicação UART (`GPIO14/15`), interface gráfica/remota (GUI/Web), API de controle e configuração, perfis de calibração/operação em eMMC, registro contínuo de telemetria (*datalogging* em CSV/SQLite), supervisão térmica/cooler (`J104`) e driver de display I2C opcional (`J103`).
- **Responsável B — Firmware de Tempo Real no RP2040 (`U300` — Raspberry Pi Pico):**
  Responsável pelo determinismo de tempo real: geração de *heartbeat* (`GP5`), controle de arme e estado seguro (`GP4`), monitoramento por interrupção de falha de hardware (`GP6`), drivers SPI0 compartilhados para o DAC de 16 bits (`DAC80504`, `U600`) e o ADC de 24 bits (`ADS1256`, `U400`), síntese digital de *dither* senoidal e soma ao comando DC de BIAS, aquisição sincronizada do fotodetector (`AIN0`), demodulação síncrona (*lock-in* em $1f$ e $2f$), varredura de busca inicial, malha de controle PI/PID com *anti-windup*, *hold* óptico e máquina de estados de segurança.

---

## 2. Restrições de Hardware que Impactam o Firmware

Todas as restrições abaixo foram extraídas dos esquemáticos e relatórios da Revisão R6 (`CM5_Projeto3_R6.PrjPcb`) e são mandatórias para o código:

1. **Obrigatoriedade do Buffer Interno do ADC (`ADS1256`):**
   Os canais de monitoramento `MON_I/Q/PHI` (`AIN1..AIN3`) possuem impedância de Thévenin de $\approx 10,014\text{ k}\Omega$ (`R1110..R1120`) compartilhada diretamente com as entradas dos comparadores de janela `LM339B` (`U1101`, `U1102`). Sem o buffer interno do `ADS1256` ($Z_{\text{in}} \approx 150\text{ k}\Omega$ a 1000 SPS), o ADC carrega o divisor em $\approx 6,26\%$ e altera o limiar de disparo de `FAULT_N`. Portanto, o firmware **deve obrigatoriamente** configurar `STATUS = 0x06` (`ORDER=0, ACAL=1, BUFEN=1`) e `ADCON = 0x00` (`PGA=1`).
2. **Teto Operacional de Tensão no ADC (`0 V` a `2,60 V`):**
   Com `BUFEN = 1`, a faixa de entrada permitida pelo `ADS1256` é de `GND` até `AVDD5 - 2,0 V`. Considerando a tolerância mínima de `AVDD5` ($4,75\text{ V}$), o limite físico é $2,75\text{ V}$. O firmware deve impor um teto operacional de segurança em **`2,60 V`** ($I_{\text{PD}} \le 10,69\ \mu\text{A}$, com faixa recomendada de $0$ a $10\ \mu\text{A} \Rightarrow V_{\text{TIA}} \in [0,2478\text{ V};\ 2,4478\text{ V}]$).
3. **Janela Analógica de Hardware Mais Estreita que a Excursão do DAC:**
   O amplificador diferencial de BIAS (`OPA197`, ganho $6,34\times$ sobre $V_{\text{DAC}} - 1,25\text{ V}$) permite excursão nominal a vazio de **$-7,925\text{ V}$ a $+7,925\text{ V}$**. Contudo, os comparadores `LM339B` (`VLO = 0,2731 V`, `VHI = 2,2269 V`) desarmam `FAULT_N` em **$-7,877\text{ V}$ e $+7,849\text{ V}$**. Assim, comandar códigos de DAC próximos de `0x0000` ou `0xFFFF` provocará falha imediata de hardware. O firmware **nunca** deve permitir comandos totais ($\text{BIAS}_{\text{DC}} + A_{\text{dither}}$) fora da faixa de segurança de software (padrão proposto: **$\pm 7,50\text{ V}$** absolutos, ou mais estreito conforme o MZM).
4. **Tempo de Assentamento (*Settling Time*) do MUX do `ADS1256`:**
   O `ADS1256` utiliza filtro digital $\text{sinc}^5$ que exige 5 ciclos de conversão (~4,1 ms a 1000 SPS) ao trocar o canal do multiplexador (`MUX`). Durante o rastreamento em malha fechada (*lock-in*), o MUX deve permanecer fixo em `AIN0` (`PHOTO_ADC`) para garantir amostragem estritamente uniforme, realizando leituras de `AIN1..AIN3` (`MON_I/Q/PHI`) apenas na inicialização, em modo manual/diagnóstico, na varredura inicial ou imediatamente após uma falha. **`[PROPOSTA / A CONFIRMAR]`**
5. **Barramento `SPI0` Compartilhado entre `ADS1256` (`U400`) e `DAC80504` (`U600`):**
   Ambos os CIs compartilham `SPI_MISO` (`GP16`), `SPI_SCLK` (`GP18`) e `SPI_MOSI` (`GP19`), com Chip Selects independentes (`ADC_CS_N = GP17`, `DAC_CS_N = GP20`). O clock SPI deve respeitar $f_{\text{SCLK}} \le f_{\text{CLKIN}}/4 = 1,92\text{ MHz}$ durante acessos ao `ADS1256` (cristal de $7,68\text{ MHz}$) e o atraso $t_6 \ge 6,5\ \mu\text{s}$ entre comando e leitura de dados no ADC. Todas as transações SPI devem ser atômicas (protegidas por seção crítica/mutex ou concentradas em um único núcleo do RP2040).
6. **Comparadores sem *Latch* Físico (`FAULT_N`):**
   Os comparadores `LM339B` operam em tempo contínuo sem *latch* em hardware: se a tensão de BIAS retornar para dentro da janela, `FAULT_N` volta a `1`. Para evitar batimento de relé (*chattering*), o firmware do RP2040 deve tratar a borda de descida em `FAULT_N` (`GP6`) via interrupção de alta prioridade, derrubando `MCU_ARM` (`GP4 = 0`) em menos de $100\ \mu\text{s}$ e mantendo o sistema em estado `FAULT_LATCHED` até rearme explícito.
7. **Ausência de Leitura Direta de `RELAY_EN`, `WD_CM5` e Pós-Relé:**
   Os sinais `MON_I/Q/PHI` medem a tensão **antes** dos relés (`BIAS_F_x`), e não há GPIO de retorno para `RELAY_EN` ou `WD_CM5` no RP2040. O status de presença do CM5 deve ser inferido pelo RP2040 via pacotes UART válidos dentro da janela de timeout e pelo pino `ARM_REQUEST` (`GP7`).
8. **Dependência de Carga na Saída (`R704/804/904 = 220 Ω`):**
   O resistor série de proteção de $220\ \Omega$ fica fora da malha de realimentação do `OPA197`. Para cargas de impedância finita $R_L$, $V_{\text{OUT}} = V_{\text{DRV}} \cdot \frac{R_L}{220\ \Omega + R_L}$ (fator $0,9785$ para $10\text{ k}\Omega$). O firmware deve permitir configurar a impedância de carga $R_L$ (padrão $\infty$ / alta impedância ou $10\text{ k}\Omega$) para compensar a conversão entre Volts desejados no eletrodo (`BIAS_OUT_x`) e código do DAC.
9. **Atualização de Firmware do RP2040:**
   O conector USB do módulo Pico (`U300`) e o botão `SW300` (`MCU_RUN`) não estão roteados para o CM5. A atualização do RP2040 deve ser suportada via cabo micro-USB conectado ao Pico (com comando UART que invoca `reset_usb_boot(0, 0)` no RP2040 para entrar em modo `BOOTSEL` sem precisar abrir o gabinete para pressionar botão) ou via bootloader serial. **`[PROPOSTA / A CONFIRMAR]`**

---

## 3. Requisitos Funcionais (RF)

### 3.1. Microcontrolador de Tempo Real — RP2040 (Responsável B)

| ID | Prioridade | Resp. | Descrição do Requisito | Critério de Aceitação Verificável |
| :--- | :---: | :---: | :--- | :--- |
| **RF-001** | Mínimo | B | **Inicialização Segura e Estado Padrão de Boot:** Configurar todos os GPIOs do RP2040 no boot com `MCU_ARM = 0` (`GP4`), `DAC_CS_N = 1` (`GP20`), `ADC_CS_N = 1` (`GP17`), `DAC_LDAC_N = 1` (`GP21`) e inicializar o `DAC80504` em *mid-scale* (`D = 32768` $\Rightarrow V_{\text{DAC}} = 1,250\text{ V} \Rightarrow V_{\text{BIAS}} = 0,000\text{ V}$). | No osciloscópio/multímetro (Ensaio E05/E12), ao energizar a placa sem comando de arme, `MCU_ARM = 0 V`, relés permanecem desenergizados (`BIAS_OUT_x` em $0\text{ V}$ via $1\text{ k}\Omega$) e `BIAS_F_x` mede $0,00\text{ V} \pm 50\text{ mV}$. |
| **RF-002** | Mínimo | B | **Geração de Heartbeat do MCU (`MCU_HEARTBEAT`):** Gerar onda quadrada contínua de $10\text{ Hz}$ ($T = 100\text{ ms}$, duty cycle $50\%$) no pino `GP5`, condicionada à execução saudável do loop de tempo real e do watchdog interno do RP2040. | Medição em `GP5` (Ensaio E06) apresenta $10,0\text{ Hz} \pm 0,5\text{ Hz}$ ($3,3\text{ Vpp}$), mantendo `WD_MCU = 5 V`. Se o loop principal travar, os pulsos cessam e `WD_MCU` cai a $0\text{ V}$ em $\le 450\text{ ms}$. |
| **RF-003** | Mínimo | B | **Driver SPI do DAC (`DAC80504`):** Implementar driver determinístico em `SPI0` para escrita de códigos de 16 bits nos canais `OUT0` (`DAC_I`), `OUT1` (`DAC_Q`), `OUT2` (`DAC_PHI`) e `OUT3` (`DAC_SPARE`), com atualização síncrona via pulso em `DAC_LDAC_N` (`GP21`) e leitura de verificação de registradores via `SDO`. | Comandar códigos de teste correspondentes a $-5\text{ V}, -2,5\text{ V}, 0\text{ V}, +2,5\text{ V}, +5\text{ V}$ (Ensaio E07) produz tensões em `TP700` com erro absoluto $\le 20\text{ mV}$ e monotonicidade garantida. |
| **RF-004** | Mínimo | B | **Driver SPI do ADC (`ADS1256`):** Implementar driver em `SPI0` com inicialização obrigatória `STATUS = 0x06` (`ACAL=1, BUFEN=1`), `ADCON = 0x00` (`PGA=1`), autocalibração (`SELFOCAL`), seleção de taxa (`DRATE = 0x72` / 60 SPS para DC e `DRATE = 0xA1` / 1000 SPS para dinâmico) e leitura de 24 bits orientada por interrupção na borda de descida de `ADC_DRDY_N` (`GP22`). | Leitura de `AIN0` no escuro (`VDARK`, Ensaio E09) retorna $0,2478\text{ V} \pm 10\text{ mV}$ com ruído RMS $\le 1\text{ mV}$; leitura de `AIN1..AIN3` não altera os limiares de `FAULT_N`. |
| **RF-005** | Mínimo | B | **Conversão de Unidades, Calibração e Compensação de Carga:** Converter entre tensão de BIAS desejada ($V_{\text{BIAS}}$ em Volts), código de DAC ($0..65535$), tensão monitorada ($V_{\text{MON}}$ em Volts) e fotocorrente/potência óptica ($I_{\text{PD}}$ em $\mu\text{A}$ e $P_{\text{opt}}$ em $\mu\text{W}/\text{dBm}$), aplicando ganhos/offsets de calibração (incluindo tara de escuro `VDARK` e fator de carga $R_L / (220\ \Omega + R_L)$). | Após calibração de offset de escuro e ganho, o erro entre o BIAS comandado e o lido em `MON_I` é $\le 1\%$ da escala, e a corrente $I_{\text{PD}}$ calculada para $5\ \mu\text{A}$ injetados apresenta erro $\le 1\%$ (Ensaio E10). |
| **RF-006** | Mínimo | B | **Geração Digital de Dither (1 Canal MZM):** Sintetizar em ponto fixo ou ponto flutuante (via tabela LUT/NCO de alta resolução) um sinal senoidal de baixa frequência configurável (padrão: $f_{\text{dither}} = 17\text{ Hz}$, amplitude padrão $A_{\text{dither}} = 20\text{ mV}$ pico na saída do driver $\approx \pm 83\text{ LSB}$), somado digitalmente ao BIAS DC do Canal I a uma taxa de atualização síncrona de $1000\text{ Hz}$. | Medição AC em `TP700` (Ensaio E08) mostra senoide de $17,0\text{ Hz} \pm 0,1\text{ Hz}$ com amplitude de $\approx 39\text{ mVpp}$ a $40\text{ mVpp}$ sobreposta ao nível DC sem degraus espúrios ou *clipping*. |
| **RF-007** | Mínimo | B | **Demodulação Síncrona Lock-In ($1f$ e $2f$) — 1 Canal:** Multiplicar as amostras de `PHOTO_ADC` (`AIN0`, a $1000\text{ SPS}$) pelas referências internas em fase ($\sin(\omega t + \phi_{\text{comp}})$) e em quadratura ($\cos(\omega t + \phi_{\text{comp}})$) na fundamental ($1f$) e no segundo harmônico ($2f$), aplicando filtro passa-baixas digital (IIR/CIC com janela inteira de ciclos de $f_{\text{dither}}$) para extrair o sinal de erro assinado $E_{1f}$, a curvatura/amplitude $E_{2f}$ e a potência óptica média $P_{\text{DC}}$. | Com emulador/MZM na bancada (Ensaio E13), ao variar o BIAS ao redor dos pontos de mínimo, máximo e quadratura, $E_{1f}$ cruza zero nos extremos (onde $|E_{2f}|$ é máximo e muda de sinal entre pico e vale) e é máximo na quadratura. |
| **RF-008** | Mínimo | B | **Varredura Inicial (*Coarse Sweep*) e Identificação da Curva do MZM:** Executar rotina de busca automática varrendo a tensão de BIAS dentro dos limites configurados ($[V_{\text{min}}, V_{\text{max}}]$) em passos configuráveis, registrando a curva $P_{\text{DC}}(V) \times V_{\text{BIAS}}$, estimando $V_\pi$, localizando automaticamente os pontos candidatos de **Mínimo (*Null*)**, **Máximo (*Peak*)**, **Quadratura Positiva ($Q^+$)**, **Quadratura Negativa ($Q^-$)** ou **Valor Específico**, posicionando o BIAS no ponto escolhido e fazendo transição suave (*bumpless transfer*) para o rastreamento. | Em teste integrado (Seção 7.3 — item 2), a varredura identifica corretamente os pontos de operação em $\le 10\text{ s}$ e posiciona o BIAS a menos de $\pm 5\%\text{ de }V_\pi$ do alvo antes de fechar a malha. |
| **RF-009** | Mínimo | B | **Controlador Digital de BIAS (PI/PID com Limites e Anti-Windup):** Executar malha fechada lenta de controle digital (taxa configurável, ex.: $17\text{ Hz}$ a $100\text{ Hz}$) sobre o erro apropriado ao modo selecionado ($E_{1f}$ para Mínimo/Máximo com inversão de sinal conforme a concavidade; $E_{2f}$ ou razão $E_{1f}/E_{2f}$ / setpoint DC para Quadratura), com constantes $K_p, K_i, K_d$ configuráveis em tempo de execução, limitação de taxa de variação (*slew-rate*), saturação em $[V_{\text{min}}, V_{\text{max}}]$ e *anti-windup* por *back-calculation* ou *clamping* condicional. | Diante de perturbação térmica/elétrica de $\pm 0,5\text{ V}$ equivalente no MZM (Ensaio E14 / Seção 7.3 — itens 2 e 3), o controlador recupera o ponto de operação sem *overshoot* destrutivo e sem acumular erro integral quando saturado nos limites. |
| **RF-010** | Mínimo | B | **Detecção de Perda de Sinal Óptico (*Hold*) e Recuperação Automática:** Monitorar continuamente $P_{\text{DC}}$ (`PHOTO_ADC` descontado de `VDARK`). Se a fotocorrente cair abaixo do limiar mínimo configurável ($I_{\text{PD,min}}$, ex.: $0,2\ \mu\text{A}$) durante o rastreamento, congelar imediatamente o integrador e o último valor válido de $V_{\text{BIAS}}$ (estado `HOLD`), retomando o rastreamento suavemente se a luz retornar dentro do tempo limite ou exigindo nova busca se configurado. | Ao desconectar/atenuar a entrada óptica durante o modo `TRACKING`, o BIAS não deriva para os extremos da fonte (variação $\le 10\text{ mV}$ em `HOLD`) e o alarme `OPTICAL_LOS` é reportado ao CM5 em $\le 50\text{ ms}$. |
| **RF-011** | Mínimo | B | **Modos Manual e Automático e Seleção de Ponto de Operação:** Suportar comutação sem sobressaltos (*bumpless*) entre **Modo Manual** (tensão DC fixa comandada pelo usuário, com dither opcionalmente ligado/desligado) e **Modo Automático** (selecionável entre: `MIN_NULL`, `MAX_PEAK`, `QUAD_POS`, `QUAD_NEG`, `CUSTOM_TARGET`). | Ao alternar de Automático para Manual, o setpoint manual assume instantaneamente a tensão de BIAS atual (degrau de transição $\le 2\text{ mV}$). |
| **RF-012** | Mínimo | B | **Máquina de Estados Determinística no RP2040:** Implementar máquina de estados explícita com os estados: `INIT` (boot seguro), `IDLE_SAFE` (relés abertos, DAC em 0 V), `PRE_ARM_CHECK` (verifica `FAULT_N=1`, `MON_x` em 0 V e comunicação CM5 ok), `ARMED_MANUAL`, `SWEEPING` (busca inicial), `TRACKING` (lock-in fechado), `HOLD` (perda de luz), `FAULT_LATCHED` (falha travada com relés abertos) e `MAINTENANCE_CAL` (calibração/diagnóstico). | Todas as transições inválidas (ex.: entrar em `TRACKING` sem passar por `PRE_ARM_CHECK` ou com `FAULT_N=0`) são rejeitadas com código de erro explícito na UART (Seção 7.2 / Seção 10). |
| **RF-013** | Mínimo | B | **Simulador Interno de Função de Transferência do MZM (*Hardware-in-the-Loop / Mock*):** Implementar no RP2040 (e em biblioteca compartilhada C/Python) um modo de simulação selecionável onde a resposta óptica $P_{\text{out}}(t) = \frac{P_{\text{in}}}{2}\left[1 + \cos\left(\frac{\pi (V_{\text{BIAS}}(t) - V_{\text{drift}}(t))}{V_\pi} + \phi_0\right)\right]$ é calculada internamente com deriva térmica sintética e ruído configuráveis, permitindo validar toda a cadeia de dither, lock-in, varredura e controle antes da chegada do MZM físico ou da PCB montada. | Com modo simulador ativo, a busca inicial, a demodulação $1f/2f$ e o rastreamento em Mínimo, Máximo e Quadratura convergem e rejeitam derivas sintéticas de $V_{\text{drift}}(t)$ exatamente como na bancada óptica. |
| **RF-014** | Recomendado | B | **Controle Simultâneo de 3 Canais (Modulador IQ: $I$, $Q$ e $\Phi$):** Expandir geração de dither, demodulação síncrona e malhas de controle para operar simultaneamente nos 3 canais (`DAC_I`, `DAC_Q`, `DAC_PHI`), utilizando frequências de dither distintas e ortogonais dentro da banda do filtro Sallen-Key ($232\text{ Hz}$) e fora de harmônicos da rede elétrica (proposta padrão: **$f_I = 17\text{ Hz}$, $f_Q = 23\text{ Hz}$, $f_\Phi = 29\text{ Hz}$**, configuráveis **`[PROPOSTA / A CONFIRMAR]`**). | Com 3 canais ativos (Seção 7.1/7.2), o *crosstalk* entre os erros demodulados dos canais $I, Q, \Phi$ é $\le -40\text{ dB}$ após filtragem, e os 3 canais mantêm seus respectivos pontos de operação simultaneamente. |

---

### 3.2. Computador de Supervisão — Raspberry Pi CM5 (Responsável A)

| ID | Prioridade | Resp. | Descrição do Requisito | Critério de Aceitação Verificável |
| :--- | :---: | :---: | :--- | :--- |
| **RF-101** | Mínimo | A | **Serviço de Supervisão, Heartbeat (`CM5_HEARTBEAT`) e Arme (`CM5_ARM_REQ`):** Executar daemon/serviço Linux (`systemd`) que gera onda quadrada de $10\text{ Hz}$ em `GPIO4` apenas enquanto o processo supervisor e a comunicação com o RP2040 estiverem íntegros, e controla o pino `GPIO17` (`CM5_ARM_REQ`) para autorizar ou revogar o acionamento dos relés. | Ao encerrar ou travar o daemon no CM5 (Ensaio E06/E12), `GPIO4` para de pulsar, `WD_CM5` vai a $0\text{ V}$ em $\le 450\text{ ms}$ e os relés `K700..K900` desarmam automaticamente sem depender do RP2040. |
| **RF-102** | Mínimo | A | **Driver de Comunicação Serial e API de Controle no CM5:** Implementar camada de comunicação UART (`115200 bps, 8N1` em `/dev/ttyAMA0` — `GPIO14/15`) com verificação de CRC-16, timeout, retransmissão e expor API local/remota (REST/WebSocket via FastAPI ou equivalente **`[PROPOSTA / A CONFIRMAR]`**) para leitura de telemetria e envio de comandos ao RP2040. | Pacotes corrompidos (erro de bit injetado) são descartados em $100\%$ dos casos pelo verificador de CRC; latência de ida e volta (*round-trip*) de comando + ACK pela UART é $\le 20\text{ ms}$. |
| **RF-103** | Mínimo | A | **Interface Gráfica / Remota de Operação (GUI / Web Dashboard):** Prover interface de usuário (acessível localmente ou via navegador na rede Wi-Fi/USB do CM5) permitindo: selecionar modo Manual/Automático, escolher ponto de operação (Mínimo, Máximo, Quadratura, Específico), ajustar limites e ganhos ($K_p, K_i, K_d$, amplitude/frequência de dither), comandar busca inicial, armar/desarmar relés e visualizar gráficos em tempo real de $V_{\text{BIAS}}$, erros $1f/2f$, potência óptica $P_{\text{DC}}$, curva de varredura e estado/alarmes. | Operador consegue executar todos os ensaios de bancada E06 a E18 exclusivamente pela interface, com atualização visual contínua ($\ge 10\text{ Hz}$) de tensões, erros demodulados e alarmes. |
| **RF-104** | Mínimo | A | **Registro Contínuo de Dados (*Datalogging*) e Exportação:** Registrar em armazenamento não-volátil (eMMC de 16 GB do CM5) séries temporais com *timestamp* ISO-8601 contendo: tensões de BIAS ($I, Q, \Phi$), erros demodulados ($1f, 2f$), fotocorrente/potência óptica, estado da máquina, eventos de alarme e parâmetros de controle, com rotação de arquivos e exportação em formato CSV/JSON. | Durante teste de estabilidade de 1 hora (Seção 7.3 — item 3), o log grava amostras sem perda de registros, permitindo plotar a evolução temporal completa do BIAS, do erro e da potência óptica. |
| **RF-105** | Mínimo | A | **Persistência de Configuração e Perfis de Calibração:** Armazenar em arquivo de configuração validado (JSON/TOML com checksum na eMMC) as constantes de calibração de fábrica/bancada (`VDARK`, ganhos de DAC/ADC, $R_L$), limites de segurança de tensão e ganhos do controlador, recarregando-os automaticamente na inicialização e enviando-os ao RP2040 antes do arme. | Após reinicialização completa da placa (power cycle), todas as constantes de calibração e parâmetros salvos são restaurados no RP2040 sem intervenção manual. |
| **RF-106** | Recomendado | A | **Interface para Display Local I2C (`J103`) e Controle de Ventoinha (`J104`):** Implementar módulo opcional no CM5 para exibir status resumido (Estado, $V_{\text{BIAS I/Q/\Phi}}$, $P_{\text{opt}}$, IP e Alarmes) em display OLED I2C conectado em `J103` (`GPIO2/SDA1`, `GPIO3/SCL1`, ex.: `SSD1306` `0x3C` **`[PROPOSTA / A CONFIRMAR]`**) e monitorar temperatura da CPU do CM5 + rotação da ventoinha PWM em `J104`. | Se o display I2C estiver presente no barramento `i2c-1`, as telas de status são atualizadas a $2\text{ Hz}$; se ausente, o serviço registra aviso no log e opera normalmente sem falha. |

---

## 4. Requisitos Não Funcionais (RNF)

| ID | Prioridade | Resp. | Categoria | Descrição e Critério de Aceitação Verificável |
| :--- | :---: | :---: | :--- | :--- |
| **RNF-001** | Mínimo | B | **Determinismo e Taxa de Amostragem** | A geração de dither no DAC e a aquisição de `PHOTO_ADC` (`AIN0`) devem ocorrer a uma taxa estritamente periódica de **$1000\text{ Hz}$** (1 ms), com *jitter* máximo de amostragem $\le 50\ \mu\text{s}$ (garantido pelo sinal `ADC_DRDY_N` derivado do cristal de $7,68\text{ MHz}$ e execução dedicada no Core 0 do RP2040). |
| **RNF-002** | Mínimo | B | **Latência de Proteção e Estado Seguro** | Ao detectar borda de descida em `FAULT_N` (`GP6`), o firmware do RP2040 deve forçar `MCU_ARM = 0` (`GP4`) por ISR em **$\le 100\ \mu\text{s}$** e comandar os DACs para *mid-scale* ($0\text{ V}$) em **$\le 2\text{ ms}$**. O hardware (`U1001` + `Q1000` + `K700..900`) corta `RELAY_EN` em $< 1\ \mu\text{s}$ e abre os contatos mecânicos dos relés em $\le 5\text{ ms}$ (Ensaio E11). |
| **RNF-003** | Mínimo | A/B | **Estado Seguro na Inicialização e Perda de Comunicação** | Na energização, reset ou perda de comunicação UART por mais de **$300\text{ ms}$** (ou ausência de pulsos de *heartbeat* por **$\approx 450\text{ ms}$** no `CD74HCT123`), os relés `K700..K900` devem obrigatoriamente permanecer ou retornar ao estado desenergizado (`BIAS_OUT_x` aterrado via $1\text{ k}\Omega$), e `MCU_ARM` deve ir para `0`. |
| **RNF-004** | Mínimo | A/B | **Watchdog Duplo Independente** | Além do watchdog externo em hardware (`U1000`, $t_W \approx 450\text{ ms}$), o RP2040 deve habilitar seu periférico de watchdog interno de hardware (timeout de $200\text{ ms}$), alimentado apenas se ambas as tarefas (Core 0: DSP/Controle e Core 1: UART/Segurança) reportarem execução saudável. |
| **RNF-005** | Mínimo | B | **Segurança de Limites de Tensão (*Clamping* Duplo)** | O firmware deve validar qualquer comando de tensão em duas camadas: (1) limite operacional configurável pelo usuário ($[V_{\text{min}}, V_{\text{max}}]$, padrão $\pm 5,0\text{ V}$) e (2) limite rígido de segurança de software em **$\pm 7,50\text{ V}$** (considerando a soma $|\text{BIAS}_{\text{DC}}| + A_{\text{dither}} \le 7,50\text{ V}$), garantindo margem de $\ge 340\text{ mV}$ antes do limiar de desarme dos comparadores `LM339B` ($-7,877\text{ V} / +7,849\text{ V}$). |
| **RNF-006** | Mínimo | A/B | **Testabilidade e Testes Unitários/Integrados** | Os drivers (ADC, DAC, UART, GPIO) e algoritmos (NCO de dither, demodulador lock-in, filtro IIR, controlador PID, máquina de estados) devem ser desacoplados do hardware via camada HAL (*Hardware Abstraction Layer*), permitindo execução de testes unitários automatizados no host (CI/GitHub Actions) com cobertura de $100\%$ das transições da máquina de estados e dos limites de saturação. |
| **RNF-007** | Mínimo | A/B | **Atualização Segura de Software/Firmware** | Qualquer procedimento de atualização de software no CM5 ou de firmware no RP2040 deve exigir que a máquina de estados esteja previamente em `IDLE_SAFE` (`MCU_ARM = 0`, relés desenergizados), garantindo que as saídas `BIAS_OUT_x` permaneçam em $0\text{ V}$ durante todo o processo de gravação e reinicialização. |
| **RNF-008** | Mínimo | A/B | **Orçamento Térmico e Consumo** | O software no CM5 não deve exceder uso médio de CPU de $40\%$ em regime contínuo de telemetria e GUI, mantendo o consumo total da placa na linha de $+15\text{ V}$ (`J200`) dentro do orçamento projetado ($I_{\text{in}} \le 1,5\text{ A}$ nominal, fusível de $3\text{ A}$). |

---

## 5. Proposta de Interface de Comunicação CM5 $\leftrightarrow$ RP2040 **`[PROPOSTA / A CONFIRMAR]`**

> **Nota:** A camada física está fixada no hardware e no plano de bancada (`UART0` em `115200 bps, 8N1`, mais os sinais discretos `CM5_ARM_REQ` em `GPIO17 -> GP7`, `CM5_HEARTBEAT` em `GPIO4` e `MCU_HEARTBEAT` em `GP5`). O protocolo de quadros e o mapa de registradores abaixo constituem a **proposta de engenharia** para validação da equipe.

### 5.1. Formato do Quadro Binário (Frame UART)

Protocolo mestre-escravo (CM5 = Mestre de comandos/configuração; RP2040 = Escravo que responde a comandos e também pode emitir quadros assíncronos de telemetria/alarme a taxa configurável, ex.: $20\text{ Hz}$), em formato *little-endian*:

| Campo | Tamanho | Valor / Descrição |
| :--- | :---: | :--- |
| `SOF` (Start of Frame) | 2 bytes | `0xAA 0x55` |
| `MSG_TYPE` | 1 byte | `0x01`=READ_REG, `0x02`=WRITE_REG, `0x03`=EXEC_CMD, `0x81`=READ_RESP, `0x82`=WRITE_ACK, `0x83`=CMD_ACK, `0x90`=TELEMETRY_STREAM, `0xE0`=ERROR/NACK, `0xF0`=ASYNC_ALARM |
| `SEQ` | 1 byte | Contador sequencial ($0..255$) para correlação requisição/resposta e detecção de perda |
| `REG_OR_CMD` | 1 byte | Endereço do registrador inicial ou ID do comando |
| `LEN` | 1 byte | Tamanho do `PAYLOAD` em bytes ($0..64$) |
| `PAYLOAD` | $N$ bytes | Dados em formato *little-endian* |
| `CRC16` | 2 bytes | `CRC-16/CCITT-FALSE` (polinômio `0x1021`, init `0xFFFF`) calculado de `MSG_TYPE` até o fim do `PAYLOAD` |

*(Nota: Para facilitar o uso manual no terminal serial durante os ensaios de bancada E06–E14, o RP2040 também poderá aceitar um modo CLI ASCII simples terminado por `\n`, ex.: `STATUS?`, `ARM 1`, `BIAS I -2.500`, `DITHER I 1 17.0 0.020`, `MODE I AUTO QUAD_POS`, selecionável automaticamente pelo primeiro byte da linha).* **`[PROPOSTA / A CONFIRMAR]`**

### 5.2. Mapa de Registradores Lógicos (RP2040)

| Endereço | Nome do Registrador | Tipo / Acesso | Unidade / Escala | Descrição |
| :---: | :--- | :---: | :--- | :--- |
| `0x00` | `SYS_FW_VERSION` | `uint32` (RO) | `Major.Minor.Patch` | Versão do firmware do RP2040 (ex.: `0x00010000` = v1.0.0) |
| `0x01` | `SYS_UPTIME_MS` | `uint32` (RO) | $\text{ms}$ | Tempo de atividade desde o último boot |
| `0x02` | `SYS_STATE` | `uint8` (RO) | Enum (`0..8`) | `0`=INIT, `1`=IDLE_SAFE, `2`=PRE_ARM, `3`=ARMED_MANUAL, `4`=SWEEPING, `5`=TRACKING, `6`=HOLD, `7`=FAULT_LATCHED, `8`=MAINTENANCE |
| `0x03` | `SYS_FAULT_FLAGS` | `uint16` (RO) | Bitmask | `b0`=`FAULT_N_HW`, `b1`=`WIN_I_OV`, `b2`=`WIN_Q_OV`, `b3`=`WIN_PHI_OV`, `b4`=`RAIL_11VA_FAIL`, `b5`=`ADC_OVER_2V6`, `b6`=`OPTICAL_LOS`, `b7`=`CM5_COMM_TIMEOUT`, `b8`=`SPI_ERR`, `b9`=`SW_CLAMP_HIT` |
| `0x04` | `SYS_GPIO_STATUS` | `uint8` (RO) | Bitmask | `b0`=`MCU_ARM (GP4)`, `b1`=`FAULT_N (GP6)`, `b2`=`ARM_REQUEST (GP7)`, `b3`=`SIM_MODE_ACTIVE` |
| `0x10` | `OPT_PHOTO_V` | `float32` (RO) | $\text{V}$ | Tensão medida em `PHOTO_ADC` (`AIN0`, filtrada) |
| `0x11` | `OPT_VDARK_V` | `float32` (R/W) | $\text{V}$ | Pedestal de escuro calibrado (padrão: `0.2478` V) |
| `0x12` | `OPT_CURRENT_UA` | `float32` (RO) | $\mu\text{A}$ | Fotocorrente calculada $I_{\text{PD}} = (V_{\text{PHOTO}} - V_{\text{DARK}}) / 0,22$ |
| `0x13` | `OPT_POWER_UW` | `float32` (RO) | $\mu\text{W}$ | Potência óptica estimada ($I_{\text{PD}} / \mathcal{R}$) |
| `0x14` | `OPT_LOS_THRESH_UA` | `float32` (R/W) | $\mu\text{A}$ | Limiar mínimo de fotocorrente para entrar em `HOLD` (padrão: `0.2` $\mu\text{A}$) |
| `0x20` | `CH_MODE[ch]` ($ch \in \{0=I, 1=Q, 2=\Phi\}$) | `uint8[3]` (R/W) | Enum | `0`=DISABLED, `1`=MANUAL_DC, `2`=AUTO_MIN_NULL, `3`=AUTO_MAX_PEAK, `4`=AUTO_QUAD_POS, `5`=AUTO_QUAD_NEG, `6`=AUTO_CUSTOM |
| `0x21` | `CH_BIAS_SET_V[ch]` | `float32[3]` (R/W) | $\text{V}$ | Tensão DC de BIAS comandada (em Manual) ou atual (em Automático) |
| `0x22` | `CH_BIAS_MON_V[ch]` | `float32[3]` (RO) | $\text{V}$ | Tensão pré-relé reconstruída a partir de `MON_I/Q/PHI` (`AIN1..3`) |
| `0x23` | `CH_DAC_CODE[ch]` | `uint16[3]` (RO) | LSB (`0..65535`) | Código instantâneo enviado ao `DAC80504` |
| `0x24` | `CH_LIMIT_MIN_V[ch]` | `float32[3]` (R/W) | $\text{V}$ | Limite inferior de BIAS por software (padrão: `-5.0` V, mín: `-7.50` V) |
| `0x25` | `CH_LIMIT_MAX_V[ch]` | `float32[3]` (R/W) | $\text{V}$ | Limite superior de BIAS por software (padrão: `+5.0` V, máx: `+7.50` V) |
| `0x30` | `DITHER_EN[ch]` | `uint8[3]` (R/W) | Bool (`0/1`) | Habilita soma de dither no canal |
| `0x31` | `DITHER_FREQ_HZ[ch]` | `float32[3]` (R/W) | $\text{Hz}$ | Frequência do dither (padrão: $I=17\text{ Hz}, Q=23\text{ Hz}, \Phi=29\text{ Hz}$) |
| `0x32` | `DITHER_AMP_V[ch]` | `float32[3]` (R/W) | $\text{V}$ (pico) | Amplitude de pico do dither no driver (padrão: `0.020` V, máx: `0.250` V) |
| `0x33` | `DITHER_PHASE_DEG[ch]` | `float32[3]` (R/W) | Graus ($^\circ$) | Fase de compensação da referência lock-in (padrão: `-5.77`° a $17\text{ Hz}$) |
| `0x40` | `DEMOD_ERR_1F[ch]` | `float32[3]` (RO) | $\text{V}$ ou norm. | Componente demodulado fundamental ($1f$) em fase |
| `0x41` | `DEMOD_ERR_2F[ch]` | `float32[3]` (RO) | $\text{V}$ ou norm. | Componente demodulado de 2º harmônico ($2f$) |
| `0x50` | `CTRL_KP[ch]` | `float32[3]` (R/W) | Ganho | Ganho proporcional $K_p$ da malha de BIAS |
| `0x51` | `CTRL_KI[ch]` | `float32[3]` (R/W) | $\text{s}^{-1}$ | Ganho integral $K_i$ da malha de BIAS |
| `0x52` | `CTRL_KD[ch]` | `float32[3]` (R/W) | $\text{s}$ | Ganho derivativo $K_d$ da malha de BIAS |
| `0x53` | `CTRL_SLEW_V_S[ch]` | `float32[3]` (R/W) | $\text{V/s}$ | Taxa máxima de variação de tensão pelo controlador (padrão: `1.0` V/s) |

### 5.3. Comandos de Ação (`MSG_TYPE = 0x03 EXEC_CMD`)

| CMD ID | Nome do Comando | Descrição e Pré-condições |
| :---: | :--- | :--- |
| `0x01` | `CMD_ARM_RELAYS` | Executa `PRE_ARM_CHECK` (verifica `FAULT_N==1`, `ARM_REQUEST==1` em `GP7`, `BIAS_SET==0V`) e ativa `MCU_ARM = 1` (`GP4`). |
| `0x02` | `CMD_DISARM_SAFE` | Força imediatamente `MCU_ARM = 0` (`GP4`), zera DACs (`32768`) e retorna ao estado `IDLE_SAFE`. |
| `0x03` | `CMD_CLEAR_FAULT` | Limpa o *latch* de falha (`FAULT_LATCHED` $\rightarrow$ `IDLE_SAFE`) se e somente se `FAULT_N == 1` e os canais `MON_I/Q/PHI` estiverem dentro da janela nominal. |
| `0x04` | `CMD_START_SWEEP` | Inicia a varredura automática de busca inicial no(s) canal(is) selecionado(s) e retorna os pontos de Mínimo, Máximo, $Q^+$ e $Q^-$. |
| `0x05` | `CMD_HOLD_FREEZE` | Congela ou descongela manualmente a saída atual do controlador (`TRACKING` $\leftrightarrow$ `HOLD`). |
| `0x06` | `CMD_CAL_DARK` | Mede a média de `AIN0` (`PHOTO_ADC`) em 60 SPS sem luz e atualiza `OPT_VDARK_V`. |
| `0x07` | `CMD_DIAG_READ_MON` | Pausa temporariamente o lock-in (se em `IDLE_SAFE` ou `ARMED_MANUAL`), lê sequencialmente `AIN1..AIN3` (`MON_I/Q/PHI`) a 60 SPS e atualiza `CH_BIAS_MON_V`. |
| `0x08` | `CMD_SET_SIM_MODE` | Ativa/desativa o simulador interno de função de transferência do MZM no RP2040 (configurando $V_\pi$, $\phi_0$ e taxa de deriva térmica). |
| `0x09` | `CMD_ENTER_BOOTLOADER` | Se em `IDLE_SAFE` (`MCU_ARM == 0`), invoca `reset_usb_boot(0, 0)` para atualização de firmware do RP2040 via USB. |

---

## 6. Matriz de Rastreabilidade

Mapeamento completo entre os requisitos deste documento, as seções do PDF acadêmico (`Propostas_Projetos_PCB_Fotonica_v1_1.pdf`), o Plano Mínimo de Testes (Seção 7.3), a Definição de Projeto Concluído (Seção 10) e os Ensaios de Bancada (`Ensaios_de_Bancada_CM5_Photonic_Bias.docx`):

| ID Requisito | Seção do PDF | Teste da Seção 7.3 (PDF) | Item da Seção 10 — Definição de Concluído (PDF) | Ensaio de Bancada (HW R6) |
| :--- | :---: | :--- | :--- | :---: |
| **RF-001** | 7.2, 8 | 1. Geração de BIAS e dither; 5. Proteções | Software/FW com controle, supervisão e proteção | E05, E11, E12 |
| **RF-002** | 7.2, 8 | 5. Teste de proteções | Tratamento de falhas e desligamento seguro | E06, E12 |
| **RF-003** | 7.2, 8 | 1. Teste de geração de BIAS e dither | Drivers para os periféricos da placa (DAC) | E07, E16 |
| **RF-004** | 7.2, 8 | 1. Geração de BIAS; 2. Busca e estabilização | Drivers para os periféricos da placa (ADC) | E09, E10 |
| **RF-005** | 7.2 | 1. Geração de BIAS; 4. Teste da interface | Calibração, conversão de unidades e filtragem | E07, E09, E10 |
| **RF-006** | 7.1, 7.2 | 1. Teste de geração de BIAS e dither | Funções de controle implementadas (dither) | E08 |
| **RF-007** | 7.1, 7.2 | 2. Teste de busca e estabilização | Demodulação síncrona na fundamental e harmônicos | E13 |
| **RF-008** | 7.2 | 2. Teste de busca e estabilização | Busca inicial do ponto de operação e transição | E13, E14 |
| **RF-009** | 7.1, 7.2 | 2. Busca e estabilização; 3. Estabilidade temporal | Controle automático com limites e anti-windup | E14, E18 |
| **RF-010** | 7.2 | 5. Teste de proteções (perda de sinal óptico) | Hold e recuperação de falha | E12, E14 |
| **RF-011** | 7.2 | 2. Busca e estabilização; 4. Interface | Seleção do ponto (mín, máx, quad) e modo manual/auto | E14 |
| **RF-012** | 7.2 | 2. Busca e estabilização; 5. Proteções | Máquina de estados (init, op, falha, manut, deslig.) | E06, E11, E12 |
| **RF-013** | 7.1, 7.3 | 2. Busca e estabilização (emulação de bancada) | Testes unitários e testes integrados em bancada | Simulações 02, 13, 14 |
| **RF-014** | 7.1, 7.2 | 1, 2 e 3 (expandidos para 3 canais IQ) | Escopo recomendado (3 canais I, Q e fase $\Phi$) | E07, E14, E16 |
| **RF-101** | 7.2, 8 | 5. Teste de proteções | Supervisão no CM5 e estado seguro | E06, E12 |
| **RF-102** | 7.2, 8 | 4. Teste da interface; 5. Proteções | Mapa de registradores/API CM5 $\leftrightarrow$ placa | E06, E13, E14 |
| **RF-103** | 7.2 | 4. Teste da interface | Interface local ou remota para operação e diagnóstico | E13, E14, E18 |
| **RF-104** | 7.2, 7.3 | 3. Teste de estabilidade temporal; 4. Interface | Registro de dados (BIAS, erros, potência óptica) | E14, E18 |
| **RF-105** | 7.2 | 4. Teste da interface | Configuração das constantes e memória | E07, E10 |
| **RF-106** | 7.2 | 4. Teste da interface | Drivers de sensores, display e interfaces | E06, E18 |
| **RNF-001** | 7.2, 8 | 1. Geração de dither; 2. Estabilização | Taxa de amostragem e determinismo | E08, E13 |
| **RNF-002** | 7.2, 8 | 5. Teste de proteções (sobretensão) | Tratamento de falhas e desligamento seguro | E11, E12 |
| **RNF-003** | 7.2, 8 | 5. Teste de proteções (inicialização/comunicação) | Sequenciamento de inicialização e falha de comm | E05, E06, E12 |
| **RNF-004** | 8 | 5. Teste de proteções | Estratégia de watchdog | E06, E12 |
| **RNF-005** | 7.2, 8 | 5. Teste de proteções (saturação e sobretensão) | Controle com limites e segurança da carga | E07, E11, E12 |
| **RNF-006** | 7.2, 10 | Todos os testes (1 a 5) | Testes unitários dos drivers e testes integrados | E01 a E19 |
| **RNF-007** | 8 | 5. Teste de proteções | Estratégia de atualização de software segura | E05, E06 |
| **RNF-008** | 7.2, 10 | 3. Teste de estabilidade temporal | Validação experimental completa em bancada | E03, E04, E18 |
