> Histórico do projeto. A correção de 14 de novembro e os resultados mais recentes estão em [Revisão de R900](../Revisao_R900.md).

# Registro de revisão da placa CM5 / RP2040 / MZM

**10 de novembro de 2026.** A identificação impressa sob as marcas EMBRAPII e VIRTUS CC é **CM5 / RP2040 / MZM**. A placa mede 120 × 90 mm e recebe componentes nas duas faces.

## Serigrafia

Foram acrescentadas 27 inscrições funcionais editáveis. As 16 inscrições da face superior identificam módulos, comandos, alimentação, a entrada J500 e as saídas de BIAS. Os conectores com pouca área livre têm uma legenda identificada pelo designador na faixa inferior. As 11 inscrições da face inferior identificam U400 ADC, U600 DAC, U500 TIA, filtro, referências, drivers e supervisão. Consulte Legendas_na_placa.csv para as posições, na referência da vista superior.

Foram reposicionados 114 designadores. O corte de 460 traços de contorno da serigrafia preservou os registros de cobre. A checagem conservadora reservou as caixas dos pads, a expansão geral de máscara de 4 mil e a folga de 10 mil. A menor folga calculada para as **novas legendas** foi de 0,388 mm, após a expansão geral da máscara. Essa verificação geométrica trata apenas das inscrições adicionadas.

43 designadores de origem ficaram na posição anterior para revisão no Altium. O reposicionamento automático os afastaria mais de 4,2 mm da posição original. Relação: R300, C1005, R1100, R801, R202, SW1000, U1000, Q1000, U212, D202, K700, U600, C1001, C205, R204, U1100, C1111, U1102, R702, U300, R1120, R212, R703, R700, R203, R200, R1119, U601, C702, R1007, J200, F201, C208, R210, C213, U800, C300, C206, U220, F220, C220, C221, C223.

## Resultado do DRC fornecido

O Altium informou **0 avisos e 390 violações** no arquivo anterior às novas inscrições. Foram **374 ocorrências de serigrafia contra máscara** e **16 antenas de rede**. As regras de curto e rede sem roteamento retornaram zero. A lista de ocorrências acompanha este registro, com o caminho pessoal do computador omitido. As 16 antenas estão identificadas por rede e coordenadas em Antenas_para_revisao.md. Essas contagens não foram recalculadas pelo Altium para o novo arquivo.

## Verificação desta entrega

O novo PcbDoc foi reaberto por um leitor de PCB independente. Foram conferidos o lado, o espelhamento e as coordenadas de todas as legendas. Permanecem 227 elementos, 905 pads, 122 redes, 4.977 segmentos de cobre e 554 vias. Todos os segmentos de cobre, as vias, os pads e a geometria dos planos coincidem com os do arquivo anterior. Nos planos, apenas o nome interno da região de GND foi atualizado. Permanecem as marcas institucionais e os modelos 3D. Os 17 esquemas elétricos e a biblioteca de footprints foram comparados byte a byte com o projeto de origem.

As três capturas originais do Altium acompanham as vistas do arquivo editado. Elas representam a montagem de referência. As vistas da nova serigrafia mostram o CAD atual; na superior, o CM5 é mostrado pelos conectores expostos. A cor da máscara depende do visualizador.

Ainda faltam o novo DRC nativo, a conferência das antenas, a revisão de montagem, o ERC e os ensaios físicos. O conjunto é uma entrega para revisão de engenharia.
