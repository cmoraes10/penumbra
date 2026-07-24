"""
Exportacao dos artefatos da Penumbra.

O front nao fala com nenhum banco. Ele le dois arquivos estaticos que este
modulo gera. O indice.json traz a ficha completa de cada municipio, com nota,
subescores, indicadores brutos e sinalizacoes. O municipios.geojson traz o
desenho simplificado de cada municipio ja com a nota, para o mapa colorir sem
peso.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from .comum import RAIZ, salva_json

SAIDA = RAIZ.parent / "app" / "public" / "data"

SUBESCORES = [
    "carencia_renda",
    "carencia_servico",
    "gap_capacidade_orcamentaria",
    "distancia_capital",
    "densidade_baixa",
    "populacao_pequena",
]


def _num(valor) -> float | None:
    """Converte para numero nativo, virando None quando o dado nao existe."""
    if valor is None:
        return None
    try:
        f = float(valor)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _municipio(cod: str, linha: pd.Series) -> dict:
    return {
        "cod_ibge": cod,
        "nome": linha["nome"],
        "microrregiao": linha["microrregiao"],
        "mesorregiao": linha["mesorregiao"],
        "regiao_imediata": linha.get("regiao_imediata"),
        "regiao_intermediaria": linha.get("regiao_intermediaria"),
        "zona_cacaueira": bool(linha["zona_cacaueira"]),
        "populacao_2022": _num(linha.get("populacao_2022")),
        "area_km2": _num(linha.get("area_km2")),
        "densidade_hab_km2": _num(linha.get("densidade_hab_km2")),
        "pib_per_capita": _num(linha.get("pib_per_capita")),
        "idhm_2010": _num(linha.get("idhm_2010")),
        "ideb_ai_2023": _num(linha.get("ideb_ai_2023")),
        "mortalidade_infantil_2010": _num(linha.get("mortalidade_infantil_2010")),
        "autonomia_fiscal": _num(linha.get("autonomia_fiscal")),
        "investimento_pc": _num(linha.get("investimento_pc")),
        "distancia_capital_km": _num(linha.get("distancia_capital_km")),
        "enviou_dca": bool(linha.get("enviou_dca")),
        "indice_penumbra": _num(linha["indice_penumbra"]),
        "indice_penumbra_pesos_iguais": _num(linha["indice_penumbra_pesos_iguais"]),
        "rank_penumbra": int(linha["rank_penumbra"]),
        "subescores": {s: _num(linha[f"sub_{s}"]) for s in SUBESCORES},
        "imputados": list(linha["imputados"]),
    }


def exporta_indice(df: pd.DataFrame, pesos: dict, config: dict, gerado_em: str, fontes: list[dict]) -> Path:
    """Grava o indice.json com metadados e a lista de municipios."""
    dados = {
        "meta": {
            "versao": "1.0.0",
            "gerado_em": gerado_em,
            "uf": config["uf"],
            "n_municipios": int(len(df)),
            "pesos": pesos,
            "fontes": fontes,
        },
        "municipios": [_municipio(cod, linha) for cod, linha in df.iterrows()],
    }
    destino = SAIDA / "indice.json"
    salva_json(dados, destino)
    return destino


def exporta_geojson(df: pd.DataFrame, malha: dict) -> Path:
    """Enriquece a malha simplificada com a nota e grava o municipios.geojson."""
    indexado = df
    features = []
    for feature in malha["features"]:
        cod = feature["properties"]["cod_ibge"]
        if cod not in indexado.index:
            continue
        linha = indexado.loc[cod]
        feature["properties"] = {
            "cod_ibge": cod,
            "nome": linha["nome"],
            "indice_penumbra": _num(linha["indice_penumbra"]),
            "rank_penumbra": int(linha["rank_penumbra"]),
            "populacao_2022": _num(linha.get("populacao_2022")),
            "zona_cacaueira": bool(linha["zona_cacaueira"]),
        }
        features.append(feature)

    malha["features"] = features
    destino = SAIDA / "municipios.geojson"
    salva_json(malha, destino)
    return destino
