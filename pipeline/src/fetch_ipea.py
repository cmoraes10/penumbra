"""
Coletor do IPEA Data (Atlas do Desenvolvimento Humano).

Traz por municipio o IDHM e a taxa de mortalidade infantil, ambos da base do
Atlas, cuja referencia municipal consolidada mais recente e o Censo de 2010. A
API do IPEA devolve o pais inteiro numa serie so, entao a filtragem por Bahia e
por ano acontece aqui.
"""

from __future__ import annotations

import pandas as pd

from .comum import carrega_config, codigo_ibge, get_json


def _serie_municipal(url: str, uf_codigo: str, ano: str) -> dict[str, float]:
    """Baixa uma serie do IPEA e devolve {cod_ibge: valor} para a UF e o ano pedidos."""
    bruto = get_json(url)
    valores: dict[str, float] = {}
    for registro in bruto.get("value", []):
        if registro.get("NIVNOME") != "Municípios":
            continue
        cod = codigo_ibge(registro.get("TERCODIGO"))
        if not cod.startswith(uf_codigo):
            continue
        data = str(registro.get("VALDATA", ""))
        if not data.startswith(ano):
            continue
        valor = registro.get("VALVALOR")
        if valor is not None:
            valores[cod] = float(valor)
    return valores


def coleta_idhm_mortalidade(config: dict) -> pd.DataFrame:
    """Devolve IDHM e mortalidade infantil por municipio da UF."""
    ipea = config["ipea"]
    uf_codigo = config["uf_codigo"]
    ano = ipea["ano"]

    idhm = _serie_municipal(
        ipea["base"].format(serie=ipea["series"]["idhm"]), uf_codigo, ano
    )
    mortalidade = _serie_municipal(
        ipea["base"].format(serie=ipea["series"]["mortalidade_infantil"]), uf_codigo, ano
    )

    codigos = set(idhm) | set(mortalidade)
    linhas = [
        {
            "cod_ibge": cod,
            "idhm_2010": idhm.get(cod),
            "mortalidade_infantil_2010": mortalidade.get(cod),
        }
        for cod in codigos
    ]
    return pd.DataFrame(linhas).set_index("cod_ibge")


if __name__ == "__main__":
    config = carrega_config("fontes.json")
    tabela = coleta_idhm_mortalidade(config)
    print(f"linhas: {len(tabela)}")
    print(f"faltando idhm: {tabela['idhm_2010'].isna().sum()}")
    print(f"faltando mortalidade: {tabela['mortalidade_infantil_2010'].isna().sum()}")
    print("menores IDHM:")
    print(tabela.sort_values("idhm_2010").head(3))
