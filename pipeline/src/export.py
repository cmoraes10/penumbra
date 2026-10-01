"""
Penumbra artifact exporter.

The front end does not talk to any database. It reads two static files that
this module generates. indice.json carries the full profile of each
municipality: score, sub-scores, raw indicators, and flags. municipios.geojson
carries the simplified outline of each municipality already with the score, so
the map can colour it without extra weight.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from .comum import ROOT, save_json

OUTPUT = ROOT.parent / "app" / "public" / "data"

SUBESCORES = [
    "carencia_renda",
    "carencia_servico",
    "gap_capacidade_orcamentaria",
    "distancia_capital",
    "densidade_baixa",
    "populacao_pequena",
]


def _num(valor) -> float | None:
    """Converts to a native float, returning None when the value is missing."""
    if valor is None:
        return None
    try:
        f = float(valor)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _municipality(cod: str, row: pd.Series) -> dict:
    return {
        "cod_ibge": cod,
        "nome": row["nome"],
        "microrregiao": row["microrregiao"],
        "mesorregiao": row["mesorregiao"],
        "regiao_imediata": row.get("regiao_imediata"),
        "regiao_intermediaria": row.get("regiao_intermediaria"),
        "zona_cacaueira": bool(row["zona_cacaueira"]),
        "populacao_2022": _num(row.get("populacao_2022")),
        "area_km2": _num(row.get("area_km2")),
        "densidade_hab_km2": _num(row.get("densidade_hab_km2")),
        "pib_per_capita": _num(row.get("pib_per_capita")),
        "idhm_2010": _num(row.get("idhm_2010")),
        "ideb_ai_2023": _num(row.get("ideb_ai_2023")),
        "mortalidade_infantil_2010": _num(row.get("mortalidade_infantil_2010")),
        "autonomia_fiscal": _num(row.get("autonomia_fiscal")),
        "investimento_pc": _num(row.get("investimento_pc")),
        "distancia_capital_km": _num(row.get("distancia_capital_km")),
        "enviou_dca": bool(row.get("enviou_dca")),
        "indice_penumbra": _num(row["indice_penumbra"]),
        "indice_penumbra_pesos_iguais": _num(row["indice_penumbra_pesos_iguais"]),
        "rank_penumbra": int(row["rank_penumbra"]),
        "subescores": {s: _num(row[f"sub_{s}"]) for s in SUBESCORES},
        "imputados": list(row["imputados"]),
    }


def export_index(df: pd.DataFrame, pesos: dict, config: dict, gerado_em: str, fontes: list[dict]) -> Path:
    """Writes indice.json with metadata and the full municipality list."""
    dados = {
        "meta": {
            "versao": "1.0.0",
            "gerado_em": gerado_em,
            "uf": config["uf"],
            "n_municipalitys": int(len(df)),
            "pesos": pesos,
            "fontes": fontes,
        },
        "municipios": [_municipality(cod, row) for cod, row in df.iterrows()],
    }
    dest = OUTPUT / "indice.json"
    save_json(dados, dest)
    return dest


def export_geojson(df: pd.DataFrame, malha: dict) -> Path:
    """Enriches the simplified mesh with the score and writes municipios.geojson."""
    indexado = df
    features = []
    for feature in malha["features"]:
        cod = feature["properties"]["cod_ibge"]
        if cod not in indexado.index:
            continue
        row = indexado.loc[cod]
        feature["properties"] = {
            "cod_ibge": cod,
            "nome": row["nome"],
            "indice_penumbra": _num(row["indice_penumbra"]),
            "rank_penumbra": int(row["rank_penumbra"]),
            "populacao_2022": _num(row.get("populacao_2022")),
            "zona_cacaueira": bool(row["zona_cacaueira"]),
        }
        features.append(feature)

    malha["features"] = features
    dest = OUTPUT / "municipios.geojson"
    save_json(malha, dest)
    return dest
