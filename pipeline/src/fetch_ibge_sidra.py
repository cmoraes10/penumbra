"""
IBGE SIDRA collector.

Fetches population, area, and density from the 2022 Census and municipal GDP
from the national accounts. GDP per capita is not available pre-computed in the
API, so it is derived here by dividing GDP by population. Density is also
recalculated from population and area for consistency with the Census year.
"""

from __future__ import annotations

import pandas as pd

from .comum import load_config, ibge_code, get_json

BASE = "https://servicodados.ibge.gov.br/api/v3/agregados"


def _url_agregado(agregado: str, periodo: str, variaveis: str, uf_codigo: str) -> str:
    localidades = f"N6[N3[{uf_codigo}]]"
    return f"{BASE}/{agregado}/periodos/{periodo}/variaveis/{variaveis}?localidades={localidades}"


def _extrai_series(resposta: list, periodo: str) -> dict[str, dict[str, float]]:
    """Reads the aggregates response and returns {variable_id: {ibge_code: value}}."""
    saida: dict[str, dict[str, float]] = {}
    for variavel in resposta:
        valores: dict[str, float] = {}
        for serie in variavel["resultados"][0]["series"]:
            cod = ibge_code(serie["localidade"]["id"])
            bruto = serie["serie"].get(periodo)
            valores[cod] = _para_numero(bruto)
        saida[str(variavel["id"])] = valores
    return saida


def _para_numero(valor) -> float | None:
    """Converts a SIDRA text value to a number, handling empty markers."""
    if valor in (None, "-", "...", "..", "X"):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def fetch_census_and_gdp(config: dict) -> pd.DataFrame:
    """Returns population, area, density, GDP, and GDP per capita by municipality."""
    uf_codigo = config["uf_codigo"]
    censo = config["ibge"]["sidra_censo2022"]
    pib = config["ibge"]["sidra_pib"]

    resp_censo = get_json(_url_agregado(censo["agregado"], censo["periodo"], censo["variaveis"], uf_codigo))
    series_censo = _extrai_series(resp_censo, censo["periodo"])

    resp_pib = get_json(_url_agregado(pib["agregado"], pib["periodo"], pib["variavel"], uf_codigo))
    series_pib = _extrai_series(resp_pib, pib["periodo"])

    # aggregate 4714 variables: 93 population, 6318 area, 614 density
    populacao = series_censo.get("93", {})
    area = series_censo.get("6318", {})
    densidade = series_censo.get("614", {})
    pib_total = series_pib.get(pib["variavel"], {})

    linhas = []
    for cod, pop in populacao.items():
        a = area.get(cod)
        pib_mil = pib_total.get(cod)
        # SIDRA GDP is in thousands of BRL; per capita is in full BRL
        pib_pc = (pib_mil * 1000 / pop) if (pib_mil and pop) else None
        dens = densidade.get(cod)
        if dens is None and pop and a:
            dens = pop / a
        linhas.append(
            {
                "cod_ibge": cod,
                "populacao_2022": pop,
                "area_km2": a,
                "densidade_hab_km2": dens,
                "pib_per_capita": round(pib_pc, 2) if pib_pc is not None else None,
            }
        )

    return pd.DataFrame(linhas).set_index("cod_ibge")


if __name__ == "__main__":
    config = load_config("fontes.json")
    tabela = fetch_census_and_gdp(config)
    print(f"rows: {len(tabela)}")
    print(f"missing population: {tabela['populacao_2022'].isna().sum()}")
    print(f"missing gdp per capita: {tabela['pib_per_capita'].isna().sum()}")
    print(tabela.sort_values("pib_per_capita", ascending=False).head(3))
    print(tabela.sort_values("pib_per_capita").head(3))
