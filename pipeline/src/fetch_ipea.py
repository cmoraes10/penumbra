"""
IPEA Data collector (Human Development Atlas).

Fetches HDI and infant mortality by municipality from the Atlas database, whose
most recent consolidated municipal reference is the 2010 Census. The IPEA API
returns the whole country in a single series, so filtering by state and year
happens here.
"""

from __future__ import annotations

import pandas as pd

from .comum import load_config, ibge_code, get_json


def _serie_municipal(url: str, uf_codigo: str, ano: str) -> dict[str, float]:
    """Fetches a series from IPEA and returns {ibge_code: value} for the given state and year."""
    bruto = get_json(url)
    valores: dict[str, float] = {}
    for registro in bruto.get("value", []):
        if registro.get("NIVNOME") != "Municípios":
            continue
        cod = ibge_code(registro.get("TERCODIGO"))
        if not cod.startswith(uf_codigo):
            continue
        data = str(registro.get("VALDATA", ""))
        if not data.startswith(ano):
            continue
        valor = registro.get("VALVALOR")
        if valor is not None:
            valores[cod] = float(valor)
    return valores


def fetch_hdi_mortality(config: dict) -> pd.DataFrame:
    """Returns HDI and infant mortality by municipality for the configured state."""
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
    config = load_config("fontes.json")
    tabela = fetch_hdi_mortality(config)
    print(f"rows: {len(tabela)}")
    print(f"missing hdi: {tabela['idhm_2010'].isna().sum()}")
    print(f"missing infant mortality: {tabela['mortalidade_infantil_2010'].isna().sum()}")
    print("lowest HDI:")
    print(tabela.sort_values("idhm_2010").head(3))
