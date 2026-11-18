# Circuitos de simulação no LTspice

Abra o esquema `.asc` correspondente e execute Run. As etiquetas de rede indicadas na tabela identificam os sinais a selecionar no gráfico. Os arquivos `.cir` registram a descrição textual do circuito. Os símbolos `.asy` são locais à pasta `LTspice`.

| Ensaio | Circuito | Grandezas principais |
| --- | --- | --- |
| 01 | TIA com corrente em patamares | TIA_OUT, PHOTO_ADC |
| 02 | Entrada com senoide de 17 Hz | GER, TIA_OUT, PHOTO_ADC |
| 03 | Resposta AC do filtro | PHOTO_ADC/TIA_OUT, módulo e fase |
| 04 | Transferência do driver I | DAC_I, DRV_I, BIAS_OUT_I |
| 05 | Três canais de BIAS | BIAS_OUT_I, BIAS_OUT_Q, BIAS_OUT_PHI |
| 06 | Comparação de cargas | Saídas com 1 TΩ, 10 kΩ e 50 Ω |
| 07 | Desarme da saída | ENABLE, BIAS_F_I, BIAS_OUT_I |
| 08 | Janela analógica | MON_I, VLO, VHI, FAULT_N |
| 09 | Supervisão das fontes | P11, N11, FAULT_N |
| 10 | Watchdog | CM5_HEARTBEAT, WD_CM5, ENABLE, BIAS_OUT_I |
| 11 | Referências | REF_ADC, VDARK, VMID_DAC |
| 12 | Alimentações funcionais | P11, N11, AVDD5 |
| 13 | Estágio buck com PWM fixo | V5SYS, BUCK_SW, I(L200) |
| 14 | MZM ideal em malha aberta | BIAS_OUT_I, POTENCIA_OPTICA, PHOTO_ADC |

Os amplificadores usam macromodelos TI nos ensaios correspondentes. DAC, relés, comparadores e watchdog empregam representações funcionais. O buck é um estágio de potência com PWM fixo; o ensaio óptico utiliza os parâmetros didáticos declarados no circuito. A análise detalhada está no relatório LTspice em `docs/relatorios`.
