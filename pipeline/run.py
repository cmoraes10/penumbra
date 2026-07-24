"""
Orquestrador do pipeline da Penumbra.

Roda os coletores na ordem certa, monta o indice e grava os dois artefatos que o
site consome. Tambem escreve um pequeno relatorio de qualidade, dizendo quantos
municipios ficaram sem cada dado, para ninguem confiar no numero as cegas.

Uso, a partir da pasta pipeline:

    python run.py
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.build_index import constroi_indice
from src.comum import DADOS_PROCESSADOS, carrega_config
from src.export import exporta_geojson, exporta_indice
from src.fetch_backbone import coleta_municipios
from src.fetch_ibge_sidra import coleta_censo_e_pib
from src.fetch_inep_ideb import coleta_ideb
from src.fetch_ipea import coleta_idhm_mortalidade
from src.fetch_siconfi import coleta_financas
from src.geometry import calcula_distancias, malha_simplificada


FONTES = [
    {"nome": "IBGE, Localidades e Malhas", "url": "https://servicodados.ibge.gov.br", "ano": "2024"},
    {"nome": "IBGE, Censo 2022 e PIB dos Municipios (SIDRA)", "url": "https://sidra.ibge.gov.br", "ano": "2021 a 2022"},
    {"nome": "IPEA, Atlas do Desenvolvimento Humano", "url": "http://www.ipeadata.gov.br", "ano": "2010"},
    {"nome": "INEP, IDEB", "url": "https://www.gov.br/inep", "ano": "2023"},
    {"nome": "Tesouro Nacional, SICONFI", "url": "https://apidatalake.tesouro.gov.br", "ano": "2022"},
]


def _relatorio_qualidade(df: pd.DataFrame) -> None:
    """Conta valores ausentes por indicador e grava um csv de acompanhamento."""
    colunas = [
        "populacao_2022",
        "pib_per_capita",
        "idhm_2010",
        "mortalidade_infantil_2010",
        "ideb_ai_2023",
        "autonomia_fiscal",
        "investimento_pc",
        "distancia_capital_km",
    ]
    presentes = [c for c in colunas if c in df.columns]
    faltantes = df[presentes].isna().sum()
    relatorio = pd.DataFrame({"faltando": faltantes, "total": len(df)})
    DADOS_PROCESSADOS.mkdir(parents=True, exist_ok=True)
    relatorio.to_csv(DADOS_PROCESSADOS / "relatorio_qualidade.csv")
    print("\nqualidade dos dados (municipios sem o indicador):")
    print(relatorio.to_string())


def main() -> None:
    config = carrega_config("fontes.json")
    pesos = carrega_config("pesos.json")

    print("1/7 municipios (backbone)")
    base = coleta_municipios(config)

    print("2/7 populacao, area, densidade e PIB (IBGE)")
    censo_pib = coleta_censo_e_pib(config)

    print("3/7 IDHM e mortalidade (IPEA)")
    ipea = coleta_idhm_mortalidade(config)

    print("4/7 IDEB (INEP)")
    ideb = coleta_ideb(config)

    print("5/7 financas municipais (SICONFI)")
    financas = coleta_financas(config)

    print("6/7 geometria e distancia ate a capital")
    distancias = calcula_distancias(config)
    malha = malha_simplificada(config)

    print("7/7 montando o indice e exportando")
    df = constroi_indice(base, censo_pib, ipea, ideb, financas, distancias, pesos)

    gerado_em = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    caminho_indice = exporta_indice(df, pesos, config, gerado_em, FONTES)
    caminho_geojson = exporta_geojson(df, malha)

    _relatorio_qualidade(df)
    print(f"\nindice: {caminho_indice}")
    print(f"geojson: {caminho_geojson}")
    print("\ntop 5 na penumbra:")
    print(df[["nome", "indice_penumbra", "zona_cacaueira"]].head())


if __name__ == "__main__":
    main()
