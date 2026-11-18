> Histórico do projeto. A correção de 14 de novembro e os resultados mais recentes estão em [Revisão de R900](Revisao_R900.md).

# Revisão do alinhamento e da serigrafia
     
**13 de novembro de 2026 · Placa compacta de 120 × 90 mm**

Na vista inferior anterior, os corpos dos 56 resistores R-0603 apareciam a aproximadamente 1,79 mm do centro do par de pads. O STEP tem origem próxima de um canto. A compensação usada na face superior havia sido aplicada com o sentido incorreto na face inferior. A correção reposiciona somente esses corpos 3D.

Também foi ajustada a orientação de 19 modelos da Bottom. A marca do pino 1 do ADS1256 em U400 agora aponta para o lado do pad 1. Em Q1000, o terminal isolado coincide com o pad 3. Em D700, D800 e D900, a faixa de cátodo corresponde ao pad 1 da rede COIL_5V.

## Conversor U600

O encapsulamento do DAC80504 foi refeito a partir do desenho RTE0016D da Texas Instruments. O modelo representa o corpo de 3,00 × 3,00 mm, com altura de 0,75 mm, passo de 0,50 mm e pad exposto quadrado de 0,80 mm. A marca circular é uma referência gráfica de montagem. A geometria do pad 17 no cobre já correspondia ao desenho. O STEP foi incluído tanto na placa quanto na biblioteca de footprints do pacote.

Texas Instruments. DACx0504. Desenho RTE0016D e exemplo de layout, páginas 47 e 48 do PDF. https://www.ti.com/lit/ds/symlink/dac80504.pdf

## Identificação das duas faces

Os designadores C206 e D202 avançavam 0,68 mm além do contorno, em lados diferentes da Top. Foram reposicionados 57 designadores e três legendas funcionais. Os 227 designadores foram verificados com suas geometrias de impressão. A menor distância entre uma dessas inscrições e o contorno foi de 0,737 mm. As novas posições das legendas funcionais constam em Verificacao/Legendas_na_placa.csv.

## Conferência do arquivo

O PcbDoc editado foi reaberto pelo importador Altium do KiCad. A malha 3D foi comparada com as coordenadas dos pads do layout. Para os 124 componentes montados na Bottom, os 386 pads apresentaram sobreposição geométrica com os contatos na face de assentamento do modelo (tolerância numérica lateral de 0,014 mm). Em cada modelo orientado foi conferida a referência de pino ou polaridade correspondente. Os resultados individuais estão em Verificacao/Alinhamento_Bottom.csv.

Os fluxos nativos de pads, trilhas, vias e redes coincidem byte a byte com os da placa de entrada. Também foram conferidos os 46 registros de modelos incorporados e as duas listas de 211 corpos 3D. As vistas nesta pasta foram geradas a partir da placa reaberta. Na vista GLB, a geometria detalhada do CM5 foi reaproveitada na mesma posição do módulo na placa.

## DRC anterior

O relatório enviado pela equipe em 13 de novembro registrou zero avisos e 177 violações. Dessas, 158 eram de serigrafia contra máscara, três eram entre inscrições de serigrafia e 16 eram antenas de rede. O relatório apontou zero curtos e zero redes sem roteamento. As 16 antenas continuam para análise elétrica. A contagem de violações desta nova cópia depende de um novo DRC no Altium Designer.

As quatro duplas de relatórios em Word e PDF acompanham o pacote como documentação da edição anterior. Para conferir a montagem atual, use as imagens da pasta Vistas e o arquivo Altium/CM5_RP2040_MZM_Alinhada.PcbDoc.
