"""
Construcao do Indice de Penumbra.

Aqui as pecas se juntam. Todos os indicadores coletados sao costurados pelo
codigo IBGE, viram os seis subescores da metodologia, e a soma ponderada deles
produz a nota final de 0 a 100. Quanto maior a nota, mais fundo o municipio
esta na penumbra.

Duas decisoes importantes moram neste modulo. Um subindicador ausente recebe o
escore mediano de 0.5, para nao punir a cidade pela falta do dado. Ja o
municipio que nao prestou contas ao Tesouro recebe escore alto no sinal de gap,
porque nao ser transparente e, em si, um sinal de penumbra.
"""

from __future__ import annotations

import pandas as pd

from .normalize import MAIOR_PIOR, MENOR_PIOR, escore, media_disponivel, minmax

# escore de gap para quem nao enviou a declaracao de contas ao Tesouro
OPACIDADE = 0.85


def constroi_indice(
    base: pd.DataFrame,
    censo_pib: pd.DataFrame,
    ipea: pd.DataFrame,
    ideb: pd.DataFrame,
    financas: pd.DataFrame,
    distancias: dict[str, float],
    pesos: dict[str, float],
) -> pd.DataFrame:
    """Devolve a tabela final dos municipios com indice, subescores e sinalizacoes."""
    df = base.join([censo_pib, ipea, ideb, financas], how="left")
    df["distancia_capital_km"] = pd.Series(distancias)

    sub = pd.DataFrame(index=df.index)
    sub["carencia_renda"] = escore(df["pib_per_capita"], MENOR_PIOR, log=True)

    servico = pd.DataFrame(
        {
            "idhm": escore(df.get("idhm_2010"), MENOR_PIOR),
            "mortalidade": escore(df.get("mortalidade_infantil_2010"), MAIOR_PIOR),
            "ideb": escore(df["ideb_ai_2023"], MENOR_PIOR)
            if "ideb_ai_2023" in df.columns
            else pd.Series(index=df.index, dtype=float),
        }
    )
    sub["carencia_servico"] = media_disponivel(servico)

    gap = escore(df.get("autonomia_fiscal"), MENOR_PIOR)
    enviou = df["enviou_dca"].fillna(False).astype(bool)
    sub["gap_capacidade_orcamentaria"] = gap.mask(~enviou, OPACIDADE)

    sub["distancia_capital"] = minmax(df["distancia_capital_km"])
    sub["densidade_baixa"] = escore(df["densidade_hab_km2"], MENOR_PIOR)
    sub["populacao_pequena"] = escore(df["populacao_2022"], MENOR_PIOR, log=True)

    # registra o que ficou ausente antes de imputar, para transparencia
    ausentes = sub.isna()
    df["imputados"] = ausentes.apply(lambda linha: [c for c in sub.columns if linha[c]], axis=1)
    sub = sub.fillna(0.5)

    ip_bruto = sum(sub[col] * peso for col, peso in pesos.items())
    df["indice_penumbra"] = _escala_0_100(ip_bruto)

    ip_iguais = sub[list(pesos)].mean(axis=1)
    df["indice_penumbra_pesos_iguais"] = _escala_0_100(ip_iguais)

    # method "first" garante posicoes unicas de 1 a N, sem empate nem furo
    df["rank_penumbra"] = df["indice_penumbra"].rank(ascending=False, method="first").astype(int)

    for col in sub.columns:
        df[f"sub_{col}"] = sub[col].round(4)

    return df.sort_values("rank_penumbra")


def _escala_0_100(serie: pd.Series) -> pd.Series:
    """Reescala uma serie para o intervalo de 0 a 100."""
    baixo, alto = serie.min(), serie.max()
    if alto == baixo:
        return pd.Series(50.0, index=serie.index)
    return (100 * (serie - baixo) / (alto - baixo)).round(2)
