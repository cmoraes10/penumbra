"""
Pipeline orchestrator for Penumbra.

Runs the collectors in the right order, builds the index, and writes the two
artifacts the site consumes. Also writes a small quality report showing how
many municipalities are missing each indicator, so no one trusts the numbers
blindly.

Usage, from the pipeline directory:

    python run.py
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.build_index import build_index
from src.comum import PROCESSED_DATA, load_config
from src.export import export_geojson, export_index
from src.fetch_backbone import fetch_municipalities
from src.fetch_ibge_sidra import fetch_census_and_gdp
from src.fetch_inep_ideb import fetch_ideb
from src.fetch_ipea import fetch_hdi_mortality
from src.fetch_siconfi import fetch_finances
from src.geometry import compute_distances, simplified_mesh


FONTES = [
    {"nome": "IBGE, Localidades e Malhas", "url": "https://servicodados.ibge.gov.br", "ano": "2024"},
    {"nome": "IBGE, Censo 2022 e PIB dos Municipios (SIDRA)", "url": "https://sidra.ibge.gov.br", "ano": "2021 a 2022"},
    {"nome": "IPEA, Atlas do Desenvolvimento Humano", "url": "http://www.ipeadata.gov.br", "ano": "2010"},
    {"nome": "INEP, IDEB", "url": "https://www.gov.br/inep", "ano": "2023"},
    {"nome": "Tesouro Nacional, SICONFI", "url": "https://apidatalake.tesouro.gov.br", "ano": "2022"},
]


def _quality_report(df: pd.DataFrame) -> None:
    """Counts missing values per indicator and writes a tracking CSV."""
    columns = [
        "populacao_2022",
        "pib_per_capita",
        "idhm_2010",
        "mortalidade_infantil_2010",
        "ideb_ai_2023",
        "autonomia_fiscal",
        "investimento_pc",
        "distancia_capital_km",
    ]
    present = [c for c in columns if c in df.columns]
    missing = df[present].isna().sum()
    report = pd.DataFrame({"missing": missing, "total": len(df)})
    PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
    report.to_csv(PROCESSED_DATA / "relatorio_qualidade.csv")
    print("\ndata quality (municipalities missing each indicator):")
    print(report.to_string())


def main() -> None:
    config = load_config("fontes.json")
    pesos = load_config("pesos.json")

    print("1/7 municipalities (backbone)")
    base = fetch_municipalities(config)

    print("2/7 population, area, density, and GDP (IBGE)")
    censo_pib = fetch_census_and_gdp(config)

    print("3/7 HDI and infant mortality (IPEA)")
    ipea = fetch_hdi_mortality(config)

    print("4/7 IDEB (INEP)")
    ideb = fetch_ideb(config)

    print("5/7 municipal finances (SICONFI)")
    financas = fetch_finances(config)

    print("6/7 geometry and distance to capital")
    distancias = compute_distances(config)
    malha = simplified_mesh(config)

    print("7/7 building index and exporting")
    df = build_index(base, censo_pib, ipea, ideb, financas, distancias, pesos)

    gerado_em = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    caminho_indice = export_index(df, pesos, config, gerado_em, FONTES)
    caminho_geojson = export_geojson(df, malha)

    _quality_report(df)
    print(f"\nindex: {caminho_indice}")
    print(f"geojson: {caminho_geojson}")
    print("\ntop 5 in penumbra:")
    print(df[["nome", "indice_penumbra", "zona_cacaueira"]].head())


if __name__ == "__main__":
    main()
