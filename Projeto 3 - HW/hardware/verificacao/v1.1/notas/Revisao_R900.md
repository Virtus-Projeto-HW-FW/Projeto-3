# CM5–RP2040–MZM | Ajuste de R900 no canal de fase

14 de novembro de 2026 · Placa compacta de 120 × 90 mm

O DRC do Altium de 13 de novembro, às 20h33min42s, marcou dois segmentos na camada Bottom do arquivo `CM5_RP2040_MZM_Serigrafia.PcbDoc`. Ambos chegam ao resistor R900. A placa corrigida está em `Altium/CM5_RP2040_MZM_PHI.PcbDoc` e o projeto que a referencia é `Altium/CM5_RP2040_MZM_PHI.PrjPcb`.

## As duas ocorrências no arquivo anterior

| Regra | Extremos do segmento no relatório do Altium (X, Y em mil) | Rede identificada no layout | Terminal |
| --- | --- | --- | --- |
| Net Antennae | (2907.283, 389.764) → (2923.031, 374.016) | VMID_DAC | R900.1 |
| Net Antennae | (2981.299, 374.016) → (3068.724, 374.016) | INV_PHI | R900.2 |

O relatório das 20h33 indicou zero avisos, zero curtos e zero redes sem roteamento. As duas verificações de serigrafia passaram. A tolerância da regra Net Antennae era de 0 mil.

## O que mudou no cobre

| Terminal | Chegada corrigida na Bottom | Pads na mesma rede |
| --- | --- | --- |
| R900.1 · VMID_DAC | Uma trilha de 0,15 mm sai do centro do pad na horizontal e segue a 45° até a via existente. O pequeno retorno dentro do pad foi removido. | U601.2, U601.6, TP601.1, R700.1, R800.1 e R900.1 |
| R900.2 · INV_PHI | A trilha de 0,20 mm entra no centro do pad. O novo percurso preserva a junção entre a entrada inversora do amplificador e o resistor de realimentação. | R900.2, R901.2 e U900.2 |

[Ver o traçado antes e depois](Verificacao/Detalhe_R900.png). A figura usa coordenadas do arquivo nativo e mostra o cobre da Bottom projetado pela face superior. As capturas originais de roteamento nos relatórios documentam a placa antes desse ajuste local.

## Conferência da cópia corrigida

A placa foi reaberta em um leitor independente do formato Altium. A análise de continuidade reuniu os 692 pads atribuídos a redes, as trilhas, as vias e as 21 regiões de cobre dos planos internos de GND. Cada uma das 122 redes apresentou um caminho entre todos os seus pads, antes e depois do ajuste. Os cinco segmentos redesenhados passaram na conferência de extremidades. A placa corrigida tem 4.943 segmentos de cobre, 547 vias e 905 pads no total.

A menor distância medida no cobre da Bottom, entre os segmentos alterados e outra rede, foi de 0,3960 mm em VMID_DAC e 0,1654 mm em INV_PHI. O limite de clearance apresentado no DRC é de 5,906 mil, cerca de 0,150 mm. A distância de 0,1654 mm ocorre junto ao pad 1 de R901, pertencente a DRV_PHI.

A comparação dos arquivos nativos encontrou diferenças nos registros de trilha e na sua contagem. Os registros de regras, pads, vias, serigrafia, componentes e modelos 3D são idênticos nas duas placas.

## Conferência no Altium

Abra a placa que termina em `_PHI.PcbDoc` e execute o Design Rule Check com as regras do projeto. Compare principalmente as contagens de Net Antennae, Short-Circuit, Un-Routed Net e Clearance. O relatório de 13 de novembro documenta a placa anterior. O DRC nativo da placa corrigida e as medições em bancada ainda estão pendentes.
