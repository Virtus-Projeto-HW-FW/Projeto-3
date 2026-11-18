> Histórico do projeto. A correção de 14 de novembro e os resultados mais recentes estão em [Revisão de R900](Revisao_R900.md).

# Serigrafia e antenas da placa CM5–RP2040–MZM

**Placa compacta de 120 × 90 mm · 13 de novembro de 2026**

## Leitura da Bottom

Com a placa vista por baixo, os 59 designadores horizontais ficam legíveis da esquerda para a direita. Os 65 verticais têm o início da inscrição na parte de baixo e podem ser lidos no mesmo sentido dos verticais da Top. As 124 inscrições giraram 180° em torno dos próprios centros. A representação em polígonos da serigrafia e o texto correspondente no registro do componente receberam a mesma transformação. A montagem dos componentes e a marca de pino 1 mantêm suas coordenadas.

Os 227 designadores continuam nas mesmas caixas de impressão, dentro do contorno da placa. Na Bottom, a menor distância calculada entre um designador e os obstáculos de impressão verificados foi de 0,350 mm. A conferência considerou as aberturas de máscara dos pads, a serigrafia dos footprints, as legendas funcionais e os demais designadores. A regra de serigrafia do projeto pede 0,254 mm.

## Antenas identificadas pelo Altium

O DRC que acompanha o pedido foi executado às 17h52 de 13 de novembro, sobre a placa Alinhada. Informou zero avisos, zero violações de serigrafia, zero curtos e zero redes sem roteamento. As 16 violações estavam na regra Net Antennae, com tolerância de zero. Nove ocorrências eram de trilha e sete de via.

As 16 coordenadas foram localizadas no arquivo nativo e os ramais foram examinados até o ponto onde voltavam ao circuito. Ao todo, a revisão retirou 33 segmentos de trilha e sete vias em 13 redes. Os 24 segmentos adicionais pertenciam aos ramais encontrados a partir das ocorrências. O arquivo agora contém 4.944 segmentos de cobre e 547 vias. As regras do Altium, os 905 pads e as 21 regiões de cobre internas do GND mantêm os mesmos dados da edição de entrada.

Na rede +5V_SYS, os dois ramais apontados no DRC chegavam à mesma posição pela Bottom e pela camada interna, sem uma via naquele ponto. Os caminhos existentes mantêm os 26 pads da alimentação conectados depois da remoção. As sete vias apontadas ligavam uma trilha em uma única camada. A tabela Antenas_do_DRC.csv identifica os objetos pelas coordenadas do Altium. Trechos_retirados.csv detalha todos os segmentos que saíram.

## Conferência da conectividade

As cópias anterior e corrigida foram reabertas com o importador Altium do KiCad. As relações de conectividade entre os 692 pads com rede atribuída foram comparadas nas 122 redes. Nas 13 redes alteradas, existe um caminho contínuo entre todos os respectivos pads. Os 214 pads de GND foram conferidos também com a geometria das 21 regiões de cobre internas do arquivo Altium. Eles pertencem a uma única conexão. A importação do KiCad, isoladamente, desconsidera essas regiões na contagem de conexões pendentes.

O arquivo corrigido passou ainda por uma comparação dos registros de cobre e modelos 3D com os da placa de entrada. Os 46 modelos incorporados e as duas tabelas de corpos 3D são idênticos. O alinhamento dos componentes entre modelos e pads segue o mesmo da revisão anterior. As novas imagens mostram a serigrafia atual e o GLB usa os componentes detalhados da montagem com a nova geometria da placa.

**Pendente:** executar o DRC nativo sobre CM5_RP2040_MZM_Serigrafia.PcbDoc. O relatório das 17h52 pertence ao arquivo anterior. A verificação de bancada também continua pendente.

Na pasta Vistas estão a face inferior corrigida, o comparativo no mesmo ângulo e a montagem 3D. Os relatórios anteriores permanecem como histórico do projeto.
