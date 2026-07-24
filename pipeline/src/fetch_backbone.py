"""
Coletor da espinha dorsal da Penumbra.

Puxa da API de localidades do IBGE a lista de municipios da UF configurada e
monta a tabela base do projeto, indexada pelo codigo IBGE. Todas as outras
fontes vao pendurar seus indicadores nessa tabela. Aqui tambem marcamos quais
municipios pertencem a zona cacaueira, o recorte que da nome e alma ao projeto.
"""

from __future__ import annotations

import pandas as pd

from .comum import carrega_config, codigo_ibge, get_json


def coleta_municipios(config: dict) -> pd.DataFrame:
    """Devolve um DataFrame com um municipio por linha, indexado pelo codigo IBGE."""
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
                "cod_ibge": codigo_ibge(item["id"]),
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
    config = carrega_config("fontes.json")
    tabela = coleta_municipios(config)
    print(f"municipios: {len(tabela)}")
    print(f"na zona cacaueira: {int(tabela['zona_cacaueira'].sum())}")
    print(tabela.head())
    print("\nmicrorregioes com cacau marcado:")
    print(tabela[tabela["zona_cacaueira"]]["microrregiao"].value_counts())
