# Controlador de polarização MZM com CM5 e RP2040

**Projeto 3 · Versão V1.1 · UFCG — Departamento de Engenharia Elétrica**

Placa-base com Raspberry Pi Compute Module 5 (CM5) e Raspberry Pi Pico (RP2040) para aquisição do sinal de um fotodiodo, supervisão e geração de três tensões de polarização (**I, Q e PHI**) destinadas a um modulador Mach–Zehnder (MZM).

A versão V1.1 reúne o projeto da **placa compacta de 120 × 90 mm**, com montagem nas duas faces e roteamento em quatro camadas. O repositório mantém também as simulações LTspice e outros recursos originados da `main`.

![Vista da placa compacta montada](docs/imagens/placa_compacta/Placa_CM5_Montada.png)

## Documentação técnica

| Documento | PDF | Word editável |
| --- | --- | --- |
| Relatório principal | [Ler](docs/relatorios/Relatorio_CM5_RP2040_MZM.pdf) | [DOCX](docs/relatorios/Relatorio_CM5_RP2040_MZM.docx) |
| Conexões e imagens 3D | [Ler](docs/relatorios/Relatorio_Conexoes_3D.pdf) | [DOCX](docs/relatorios/Relatorio_Conexoes_3D.docx) |
| Pinagem e interfaces | [Ler](docs/relatorios/Relatorio_Pinagem_CM5_RP2040_MZM.pdf) | [DOCX](docs/relatorios/Relatorio_Pinagem_CM5_RP2040_MZM.docx) |
| Ensaios de bancada | [Ler](docs/relatorios/Ensaios_de_Bancada_CM5_Photonic_Bias.pdf) | [DOCX](docs/relatorios/Ensaios_de_Bancada_CM5_Photonic_Bias.docx) |
| Simulações LTspice | [Ler](docs/relatorios/Relatorio_LTspice_CM5_RP2040_MZM.pdf) | [DOCX](docs/relatorios/Relatorio_LTspice_CM5_RP2040_MZM.docx) |
| Apresentação da placa compacta | [Ler slides em PDF](docs/relatorios/Apresentacao_Placa_Compacta_CM5.pdf) | — |

## Arquivos da placa

- **Projeto Altium:** [`hardware/altium/CM5_RP2040_MZM_PHI.PrjPcb`](hardware/altium/CM5_RP2040_MZM_PHI.PrjPcb)
- **Layout da PCB:** [`hardware/altium/CM5_RP2040_MZM_PHI.PcbDoc`](hardware/altium/CM5_RP2040_MZM_PHI.PcbDoc)
- **Biblioteca:** [`hardware/altium/CM5_Projeto_R6.PcbLib`](hardware/altium/CM5_Projeto_R6.PcbLib)
- **Esquemáticos e BOM:** [hardware/altium](hardware/altium)
- **Modelos STEP incorporados ao Altium:** [hardware/altium/ALTIUM_EMBEDDED_MODELS](hardware/altium/ALTIUM_EMBEDDED_MODELS)
- **Imagens da montagem compacta:** [docs/imagens/placa_compacta](docs/imagens/placa_compacta)
- **Visualização 3D GLB:** [docs/modelos_3d](docs/modelos_3d)
- **Verificações técnicas e registros:** [hardware/verificacao/v1.1](hardware/verificacao/v1.1)
- **Simulações existentes no projeto:** [simulacoes](simulacoes)

## Principais interfaces

| Conector | Função |
| --- | --- |
| J100 / J101 | Conexão com Compute Module 5 |
| J102 | USB-C de acesso ao CM5 |
| J103 | Expansão I²C, lógica de 3,3 V |
| J104 | Ventilador de 5 V, tacômetro e PWM |
| J200 | Entrada de alimentação +15 Vcc |
| J500 | Entrada elétrica de fotodiodo externo |
| J700 / J800 / J900 | Saídas de BIAS I, Q e PHI |

A arquitetura usa o **ADS1256 (U400)** para aquisição e o **DAC80504 (U600)** para geração dos comandos analógicos. A documentação da versão considera o ADS1256 com buffer ativado e a faixa prevista de entrada de 0 a 2,6 V.

## Organização e histórico

Os circuitos LTspice, o vídeo de bancada, arquivos históricos da revisão R6 e demais elementos presentes na `main` são preservados quando o conteúdo V1.1 é aplicado sobre a branch. Os novos arquivos estão organizados sem pastas ZIP duplicadas. O histórico detalhado fica em [CHANGELOG.md](CHANGELOG.md), e as informações de terceiros em [THIRD_PARTY.md](THIRD_PARTY.md).

## Autores

Carlos Renan Correia Fidelis · Carlos Elias Fialho de Lima · Pablo Daniel Nascimento Vieira

Universidade Federal de Campina Grande · Engenharia Elétrica · 2026.
