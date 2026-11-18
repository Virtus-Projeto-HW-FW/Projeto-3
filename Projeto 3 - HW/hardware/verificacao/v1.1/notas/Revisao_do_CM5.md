> Histórico do projeto. A correção de 14 de novembro e os resultados mais recentes estão em [Revisão de R900](Revisao_R900.md).

> Registro da etapa anterior de integração do CM5. A revisão atual está em Revisao_do_layout.md.

# Compute Module 5 na placa CM5 / RP2040 / MZM

O modelo do CM5 está embutido em Altium/CM5_RP2040_MZM_Alinhada.PcbDoc. A placa-base tem 120 × 90 mm. A lista de materiais especifica o Raspberry Pi CM5102016 (SC1588), com Wi-Fi, 2 GB de RAM e 16 GB de eMMC. O módulo participa da supervisão do sistema e está montado acima de J100 e J101. Seu corpo 3D foi associado graficamente a J100 como segundo modelo. Os dois conectores continuam independentes no esquema e no layout.

## O que a vista mostra

O arquivo mecânico de origem é o STEP publicado pela Raspberry Pi para o CM5 com eMMC. Ele representa os encapsulamentos em ambas as faces, o processador BCM2712, o RP1, as memórias, o rádio, o conector da antena, os passivos e os conectores de acoplamento. Na montagem, aplicamos à placa do módulo o acabamento verde. Os anéis dourados e a serigrafia com o nome e a marca do módulo foram representados com base na fotografia do fabricante. As inscrições são referências visuais. Os códigos de lote variam entre unidades.

O arquivo Altium/ALTIUM_EMBEDDED_MODELS/CM5_Montado_AP214.step usa o sistema de coordenadas da placa-base. A pasta Referencias traz o arquivo mecânico de origem exatamente como distribuído pelo fabricante, com a origem e as cores próprias do STEP.

## Conferência do encaixe no CAD

A referência das coordenadas abaixo é o canto inferior esquerdo da placa-base, em vista superior.

| Elemento | Coordenadas ou medida |
| --- | --- |
| Contorno do CM5 | X de 8 a 48 mm, Y de 30 a 85 mm |
| Furos H5 e H6 | (11,5, 81,5) mm e (44,5, 81,5) mm |
| Furos H7 e H8 | (11,5, 33,5) mm e (44,5, 33,5) mm |
| Centro de J100 | X = 11,0 mm e Y = 55,0 mm |
| Centro de J101 | X = 45,0 mm e Y = 55,0 mm |
| Entre os centros de J100 e J101 | 34,0 mm |
| Conectores da BOM | Amphenol 10164227-1004A1RLF |
| Empilhamento nominal entre placas | 4,0 mm |

Comparamos o layout reimportado com o footprint Module1 do projeto CM5IO, revisão 2, da Raspberry Pi. Os centros dos quatro furos e dos 200 pads coincidiram dentro de 0,001 mm, após a rotação e a translação de referenciais. Os dois corpos de conector da face inferior do próprio STEP também coincidiram com os centros de J100 e J101. A comparação verifica as coordenadas nominais. A montagem física e a abertura no Altium Designer continuam para revisão.

No arquivo nativo, 140 dos 144 fluxos internos são idênticos ao arquivo de entrada. Os quatro fluxos alterados são a carga do STEP, o cadastro dos modelos e as duas representações do corpo 3D. A comparação binária confirma os mesmos pads, trilhas, vias, redes, contorno e serigrafia. Os esquemáticos e o conteúdo das listas de materiais também são idênticos aos originais.

O relatório histórico de DRC na pasta Verificacao é anterior a esta alteração visual. As verificações de fabricação e bancada seguem a situação registrada no projeto original.

## Arquivos para revisão

- Altium contém o projeto editável e os modelos incorporados.
- Vistas contém a placa montada, a ampliação do CM5, a vista superior e o mapa das duas faces.
- O modelo GLB permite girar a placa completa e ampliar os componentes em um visualizador 3D.
- Relatorios reúne as cópias em Word e PDF do relatório principal, das conexões, dos ensaios e da pinagem. A Figura 10 do relatório de conexões mostra a ampliação do CM5.

## Fontes

Raspberry Pi Ltd. Raspberry Pi Compute Module 5, pacote rpi-cm5 3D_STEP, RP-007222-DD-2. https://pip.raspberrypi.com/categories/1096-design-files

Raspberry Pi Ltd. Raspberry Pi Compute Module 5 Datasheet. Seções 1 e 4.1. https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf

Raspberry Pi Ltd. Raspberry Pi Compute Module 5 IO Board, design files, revisão 2. https://pip.raspberrypi.com/categories/1098-design-files

## Correção do corpo 3D do CM5

O STEP do CM5 foi regravado em AP214 com o conjunto completo e um novo identificador. No pacote anterior, o registro usava CRC32. Esse valor divergia da soma de verificação usada pelo arquivo da placa. Nesta cópia, a soma calculada sobre o conteúdo incorporado coincide com os registros do modelo e do corpo de J100. A verificação foi repetida para as 46 entradas de modelos e as duas tabelas de corpos 3D.

A releitura do STEP confirmou 1 126 sólidos, 30 536 faces e a mesma distribuição de cores. A conferência geométrica verificou as posições nominais dos quatro furos e dos dois conectores. A vista em Vistas/Placa_3D_Conferida.png foi gerada a partir do PcbDoc corrigido reaberto com o importador de Altium do KiCad. A verificação visual no Altium Designer para Windows ainda depende da instalação do usuário.
