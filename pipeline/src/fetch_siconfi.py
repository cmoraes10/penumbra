"""
SICONFI collector (National Treasury).

For each municipality, fetches the Annual Account Declaration and extracts two
things. From the revenue annex it takes total revenue and own-source tax
revenue, whose ratio measures fiscal autonomy: how much the municipality
sustains itself without relying on federal transfers. From the expenditure annex
it takes investment, the share of the budget that becomes new works and
services.

Two requests per municipality, so each response is cached to disk. A
municipality that did not file a declaration returns empty, and that absence is
handled downstream as an opacity signal, not an error.
"""

from __future__ import annotations

import json
import time

import pandas as pd

from .comum import RAW_DATA, load_config, ibge_code, get_json

CACHE = RAW_DATA / "siconfi"

CONTA_RECEITA_TOTAL = "ReceitasExcetoIntraOrcamentarias"
CONTA_RECEITA_PROPRIA = "RO1.1.0.0.00.0.0"  # taxes, fees, and improvement contributions
CONTA_INVESTIMENTO = "DO4.4.00.00.00.00"    # 4.4 investments
COLUNA_RECEITA = "Receitas Brutas Realizadas"
COLUNAS_DESPESA = ("Despesas Liquidadas", "Despesas Pagas", "Despesas Empenhadas")


def fetch_state_entities(config: dict) -> dict[str, float]:
    """Returns {ibge_code: population} for municipalities in the configured state."""
    bruto = get_json(config["siconfi"]["entes"], params={"uf": config["uf"]})
    uf_codigo = config["uf_codigo"]
    entes = {}
    for item in bruto.get("items", []):
        if item.get("esfera") != "M":
            continue
        cod = ibge_code(item.get("cod_ibge"))
        if cod.startswith(uf_codigo):
            entes[cod] = item.get("populacao")
    return entes


def _dca(config: dict, id_ente: str, anexo: str, rotulo: str) -> list[dict]:
    """Fetches a DCA annex for a municipality, with disk cache."""
    CACHE.mkdir(parents=True, exist_ok=True)
    arquivo = CACHE / f"{rotulo}_{id_ente}.json"
    if arquivo.exists():
        with open(arquivo, encoding="utf-8") as f:
            return json.load(f)

    dados = get_json(
        config["siconfi"]["dca"],
        params={"an_exercicio": config["siconfi"]["ano"], "no_anexo": anexo, "id_ente": id_ente},
        timeout=90,
    )
    items = dados.get("items", [])
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
    time.sleep(0.15)  # rate-limit courtesy
    return items


def _valor(items: list[dict], cod_conta: str, colunas) -> float | None:
    """Finds the value for an account, trying columns in preference order."""
    if isinstance(colunas, str):
        colunas = (colunas,)
    for coluna in colunas:
        for item in items:
            if item.get("cod_conta") == cod_conta and item.get("coluna") == coluna:
                try:
                    return float(item["valor"])
                except (TypeError, ValueError):
                    return None
    return None


def fetch_finances(config: dict, municipios: list[str] | None = None) -> pd.DataFrame:
    """Returns revenue, fiscal autonomy, and per-capita investment by municipality."""
    entes = fetch_state_entities(config)
    codigos = municipios or list(entes)

    conf = config["siconfi"]
    linhas = []
    for i, cod in enumerate(codigos, 1):
        receitas = _dca(config, cod, conf["anexo_receitas"], "ic")
        despesas = _dca(config, cod, conf["anexo_despesas"], "id")

        receita_total = _valor(receitas, CONTA_RECEITA_TOTAL, COLUNA_RECEITA)
        receita_propria = _valor(receitas, CONTA_RECEITA_PROPRIA, COLUNA_RECEITA)
        investimento = _valor(despesas, CONTA_INVESTIMENTO, COLUNAS_DESPESA)
        populacao = entes.get(cod)

        enviou = bool(receitas)
        autonomia = (receita_propria / receita_total) if (receita_propria and receita_total) else None
        investimento_pc = (investimento / populacao) if (investimento and populacao) else None

        linhas.append(
            {
                "cod_ibge": cod,
                "enviou_dca": enviou,
                "receita_total": receita_total,
                "autonomia_fiscal": round(autonomia, 4) if autonomia is not None else None,
                "investimento_pc": round(investimento_pc, 2) if investimento_pc is not None else None,
            }
        )
        if i % 50 == 0:
            print(f"  siconfi {i}/{len(codigos)}")

    return pd.DataFrame(linhas).set_index("cod_ibge")


if __name__ == "__main__":
    config = load_config("fontes.json")
    amostra = ["2913606", "2900306", "2916500"]  # Ilhéus, Acajutiba, one with low HDI
    tabela = fetch_finances(config, amostra)
    print(tabela)
