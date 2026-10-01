"""
Penumbra index builder.

This is where the pieces come together. All collected indicators are joined by
IBGE code, turned into the six sub-scores of the methodology, and their weighted
sum produces the final 0-to-100 score. The higher the score, the deeper the
municipality is in the penumbra.

Two design decisions live here. A missing sub-indicator receives the median
score of 0.5, so the municipality is not penalised for missing data. A
municipality that did not report to the Treasury receives a high score on the
fiscal gap signal, because non-transparency is itself a sign of penumbra.
"""

from __future__ import annotations

import pandas as pd

from .normalize import HIGHER_IS_WORSE, LOWER_IS_WORSE, score, row_mean, minmax

# opacity score assigned to municipalities that did not file a Treasury declaration
OPACITY_SCORE = 0.85


def build_index(
    base: pd.DataFrame,
    census_gdp: pd.DataFrame,
    ipea: pd.DataFrame,
    ideb: pd.DataFrame,
    finances: pd.DataFrame,
    distances: dict[str, float],
    weights: dict[str, float],
) -> pd.DataFrame:
    """Returns the final municipality table with index, sub-scores, and flags."""
    df = base.join([census_gdp, ipea, ideb, finances], how="left")
    df["distancia_capital_km"] = pd.Series(distances)

    sub = pd.DataFrame(index=df.index)
    sub["carencia_renda"] = score(df["pib_per_capita"], LOWER_IS_WORSE, log=True)

    servico = pd.DataFrame(
        {
            "idhm": score(df.get("idhm_2010"), LOWER_IS_WORSE),
            "mortalidade": score(df.get("mortalidade_infantil_2010"), HIGHER_IS_WORSE),
            "ideb": score(df["ideb_ai_2023"], LOWER_IS_WORSE)
            if "ideb_ai_2023" in df.columns
            else pd.Series(index=df.index, dtype=float),
        }
    )
    sub["carencia_servico"] = row_mean(servico)

    gap = score(df.get("autonomia_fiscal"), LOWER_IS_WORSE)
    enviou = df["enviou_dca"].fillna(False).astype(bool)
    sub["gap_capacidade_orcamentaria"] = gap.mask(~enviou, OPACITY_SCORE)

    sub["distancia_capital"] = minmax(df["distancia_capital_km"])
    sub["densidade_baixa"] = score(df["densidade_hab_km2"], LOWER_IS_WORSE)
    sub["populacao_pequena"] = score(df["populacao_2022"], LOWER_IS_WORSE, log=True)

    # record what was missing before imputation, for transparency
    missing = sub.isna()
    df["imputados"] = missing.apply(lambda linha: [c for c in sub.columns if linha[c]], axis=1)
    sub = sub.fillna(0.5)

    raw_score = sum(sub[col] * peso for col, peso in weights.items())
    df["indice_penumbra"] = _scale_0_100(raw_score)

    equal_score = sub[list(weights)].mean(axis=1)
    df["indice_penumbra_pesos_iguais"] = _scale_0_100(equal_score)

    # method "first" guarantees unique ranks 1 to N with no ties or gaps
    df["rank_penumbra"] = df["indice_penumbra"].rank(ascending=False, method="first").astype(int)

    for col in sub.columns:
        df[f"sub_{col}"] = sub[col].round(4)

    return df.sort_values("rank_penumbra")


def _scale_0_100(serie: pd.Series) -> pd.Series:
    """Rescales a series to the 0-to-100 range."""
    baixo, alto = serie.min(), serie.max()
    if alto == baixo:
        return pd.Series(50.0, index=serie.index)
    return (100 * (serie - baixo) / (alto - baixo)).round(2)
