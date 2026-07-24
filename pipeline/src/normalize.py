"""
Normalizacao dos indicadores da Penumbra.

Cada indicador bruto vive numa escala diferente, reais, anos de estudo, pessoas
por quilometro quadrado. Para somar tudo num indice unico e preciso primeiro
colocar todos na mesma regua, entre 0 e 1, onde 1 significa mais fundo na
penumbra. E o que estas funcoes fazem.

A regua padrao e o percentil dentro do conjunto de municipios, que e robusto a
valores extremos como o de Salvador. Para indicadores de cauda longa, como
populacao e renda, aplica-se o logaritmo antes, para que a diferenca entre uma
cidade minuscula e uma media conte tanto quanto a diferenca entre uma media e
uma gigante.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MENOR_PIOR = "menor_pior"
MAIOR_PIOR = "maior_pior"


def percentil(serie: pd.Series, log: bool = False) -> pd.Series:
    """Converte os valores em seu percentil dentro do conjunto, de 0 a 1.

    Valores ausentes continuam ausentes e sao tratados depois. Com log ligado, a
    transformacao so vale para valores positivos.
    """
    valores = serie.astype(float)
    if log:
        valores = np.log(valores.where(valores > 0))
    return valores.rank(pct=True)


def escore(serie: pd.Series, direcao: str, log: bool = False) -> pd.Series:
    """Devolve o escore de penumbra de um indicador, entre 0 e 1.

    Quando valores menores sao piores, como renda baixa, o escore e o inverso do
    percentil. Quando valores maiores sao piores, como distancia, o escore e o
    proprio percentil.
    """
    p = percentil(serie, log=log)
    return (1 - p) if direcao == MENOR_PIOR else p


def minmax(serie: pd.Series) -> pd.Series:
    """Reescala linearmente para o intervalo de 0 a 1."""
    valores = serie.astype(float)
    baixo, alto = valores.min(), valores.max()
    if not np.isfinite(baixo) or alto == baixo:
        return pd.Series(0.5, index=valores.index)
    return (valores - baixo) / (alto - baixo)


def media_disponivel(quadro: pd.DataFrame) -> pd.Series:
    """Media linha a linha ignorando os valores ausentes.

    Serve para combinar subindicadores quando nem todos existem para todo
    municipio. Se um municipio nao tem nenhum dos subindicadores, o resultado
    fica ausente e a imputacao cuida disso depois.
    """
    return quadro.mean(axis=1, skipna=True)
