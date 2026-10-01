"""
IDEB collector (INEP).

Downloads the early primary IDEB results by municipality from a compressed file
distributed by INEP, then extracts the public-school score for each municipality
in the configured state. The file is large, so it is cached locally to avoid
re-downloading on every run.
"""

from __future__ import annotations

import zipfile

import pandas as pd

from .comum import RAW_DATA, download_file, load_config, ibge_code


def _abre_planilha(config: dict) -> pd.DataFrame:
    """Downloads the IDEB zip, finds the xlsx inside, and reads the municipality tab."""
    destino = RAW_DATA / "ideb_anos_iniciais_2023.zip"
    download_file(config["inep"]["ideb_ai_zip"], destino)

    with zipfile.ZipFile(destino) as pacote:
        nome_xlsx = next(n for n in pacote.namelist() if n.lower().endswith(".xlsx"))
        with pacote.open(nome_xlsx) as planilha:
            # the technical header starts on the tenth row of the tab
            return pd.read_excel(
                planilha,
                sheet_name=config["inep"]["aba"],
                skiprows=9,
                engine="openpyxl",
            )


def fetch_ideb(config: dict) -> pd.DataFrame:
    """Returns the early primary public-school IDEB by municipality for the configured state.

    IDEB enriches the service deprivation signal but is not required. If the
    INEP server is unavailable during the run, the function returns an empty
    table and the index continues with the remaining indicators rather than
    halting the whole pipeline over a single missing source.
    """
    try:
        bruto = _abre_planilha(config)
    except (OSError, zipfile.BadZipFile) as erro:
        print(f"  warning: IDEB unavailable ({erro}); continuing without it.")
        return pd.DataFrame(columns=["ideb_ai_2023"]).rename_axis("cod_ibge")

    coluna = config["inep"]["coluna_valor"]
    filtro = (bruto["SG_UF"] == config["uf"]) & (bruto["REDE"].str.strip() == "Pública")
    recorte = bruto.loc[filtro, ["CO_MUNICIPIO", coluna]].copy()

    recorte["cod_ibge"] = recorte["CO_MUNICIPIO"].map(ibge_code)
    recorte["ideb_ai_2023"] = pd.to_numeric(recorte[coluna], errors="coerce")

    return recorte.set_index("cod_ibge")[["ideb_ai_2023"]]


if __name__ == "__main__":
    config = load_config("fontes.json")
    bruto = _abre_planilha(config)
    print("available school types:", sorted(bruto["REDE"].dropna().str.strip().unique().tolist()))
    tabela = fetch_ideb(config)
    print(f"public-school rows for BA: {len(tabela)}")
    print(f"missing ideb: {tabela['ideb_ai_2023'].isna().sum()}")
    print("lowest IDEB:")
    print(tabela.sort_values("ideb_ai_2023").head(3))
