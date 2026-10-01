"""
Backbone collector for Penumbra.

Pulls the municipality list for the configured state from the IBGE localities
API and builds the base table the project is indexed on. All other sources hang
their indicators off this table. This module also flags which municipalities
belong to the cocoa zone, the regional focus that gives the project its name.
"""

from __future__ import annotations

import pandas as pd

from .comum import load_config, ibge_code, get_json


def fetch_municipalities(config: dict) -> pd.DataFrame:
    """Returns a DataFrame with one municipality per row, indexed by IBGE code."""
    url = config["ibge"]["localidades_municipios"].format(uf=config["uf"])
    bruto = get_json(url)

    cacau = set(config["zona_cacaueira"]["microrregioes"])
    linhas = []
    for item in bruto:
        micro = item["microrregiao"]
        meso = micro["mesorregiao"]
        imediata = item.get("regiao-imediata", {}) or {}
        intermediaria = imediata.get("regiao-intermediaria", {}) or {}
        nome_micro = micro["nome"]
        linhas.append(
            {
                "cod_ibge": ibge_code(item["id"]),
                "nome": item["nome"],
                "microrregiao": nome_micro,
                "mesorregiao": meso["nome"],
                "regiao_imediata": imediata.get("nome"),
                "regiao_intermediaria": intermediaria.get("nome"),
                "zona_cacaueira": nome_micro in cacau,
            }
        )

    tabela = pd.DataFrame(linhas).set_index("cod_ibge").sort_values("nome")
    return tabela


if __name__ == "__main__":
    config = load_config("fontes.json")
    tabela = fetch_municipalities(config)
    print(f"municipalities: {len(tabela)}")
    print(f"in cocoa zone: {int(tabela['zona_cacaueira'].sum())}")
    print(tabela.head())
    print("\nmicro-regions with cocoa flag:")
    print(tabela[tabela["zona_cacaueira"]]["microrregiao"].value_counts())
