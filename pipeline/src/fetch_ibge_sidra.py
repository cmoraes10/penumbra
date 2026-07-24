"""
Coletor dos indicadores do IBGE via API de agregados (SIDRA).

Traz do Censo de 2022 a populacao, a area e a densidade de cada municipio, e do
levantamento de contas o PIB municipal. O PIB per capita nao existe pronto na
API, entao ele e derivado aqui, dividindo o PIB pela populacao. Densidade
tambem e recalculada a partir de populacao e area para ficar coerente com o ano
do Censo.
"""

from __future__ import annotations

import pandas as pd

from .comum import carrega_config, codigo_ibge, get_json

BASE = "https://servicodados.ibge.gov.br/api/v3/agregados"


def _url_agregado(agregado: str, periodo: str, variaveis: str, uf_codigo: str) -> str:
    localidades = f"N6[N3[{uf_codigo}]]"
    return f"{BASE}/{agregado}/periodos/{periodo}/variaveis/{variaveis}?localidades={localidades}"


def _extrai_series(resposta: list, periodo: str) -> dict[str, dict[str, float]]:
    """Le a resposta de agregados e devolve {variavel_id: {cod_ibge: valor}}."""
    saida: dict[str, dict[str, float]] = {}
    for variavel in resposta:
        valores: dict[str, float] = {}
        for serie in variavel["resultados"][0]["series"]:
            cod = codigo_ibge(serie["localidade"]["id"])
            bruto = serie["serie"].get(periodo)
            valores[cod] = _para_numero(bruto)
        saida[str(variavel["id"])] = valores
    return saida


def _para_numero(valor) -> float | None:
    """Converte o valor textual da SIDRA em numero, tratando os marcadores de vazio."""
    if valor in (None, "-", "...", "..", "X"):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def coleta_censo_e_pib(config: dict) -> pd.DataFrame:
    """Devolve populacao, area, densidade, PIB e PIB per capita por municipio."""
    uf_codigo = config["uf_codigo"]
    censo = config["ibge"]["sidra_censo2022"]
    pib = config["ibge"]["sidra_pib"]

    resp_censo = get_json(_url_agregado(censo["agregado"], censo["periodo"], censo["variaveis"], uf_codigo))
    series_censo = _extrai_series(resp_censo, censo["periodo"])

    resp_pib = get_json(_url_agregado(pib["agregado"], pib["periodo"], pib["variavel"], uf_codigo))
    series_pib = _extrai_series(resp_pib, pib["periodo"])

    # variaveis do agregado 4714: 93 populacao, 6318 area, 614 densidade
    populacao = series_censo.get("93", {})
    area = series_censo.get("6318", {})
    densidade = series_censo.get("614", {})
    pib_total = series_pib.get(pib["variavel"], {})

    linhas = []
    for cod, pop in populacao.items():
        a = area.get(cod)
        pib_mil = pib_total.get(cod)
        # PIB da SIDRA vem em mil reais; per capita em reais cheios
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
    config = carrega_config("fontes.json")
    tabela = coleta_censo_e_pib(config)
    print(f"linhas: {len(tabela)}")
    print(f"faltando populacao: {tabela['populacao_2022'].isna().sum()}")
    print(f"faltando pib per capita: {tabela['pib_per_capita'].isna().sum()}")
    print(tabela.sort_values("pib_per_capita", ascending=False).head(3))
    print(tabela.sort_values("pib_per_capita").head(3))
