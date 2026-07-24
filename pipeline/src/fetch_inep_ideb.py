"""
Coletor do IDEB (INEP).

Baixa o resultado do IDEB dos anos iniciais do ensino fundamental por municipio,
distribuido pelo INEP num arquivo compactado, e extrai a nota da rede publica de
cada municipio da UF. O arquivo e grande, entao fica guardado em cache para nao
ser rebaixado a cada execucao.
"""

from __future__ import annotations

import zipfile

import pandas as pd

from .comum import DADOS_BRUTOS, baixa_arquivo, carrega_config, codigo_ibge


def _abre_planilha(config: dict) -> pd.DataFrame:
    """Baixa o zip do IDEB, acha a planilha xlsx dentro e le a aba de municipios."""
    destino = DADOS_BRUTOS / "ideb_anos_iniciais_2023.zip"
    baixa_arquivo(config["inep"]["ideb_ai_zip"], destino)

    with zipfile.ZipFile(destino) as pacote:
        nome_xlsx = next(n for n in pacote.namelist() if n.lower().endswith(".xlsx"))
        with pacote.open(nome_xlsx) as planilha:
            # o cabecalho tecnico fica na decima linha da aba
            return pd.read_excel(
                planilha,
                sheet_name=config["inep"]["aba"],
                skiprows=9,
                engine="openpyxl",
            )


def coleta_ideb(config: dict) -> pd.DataFrame:
    """Devolve o IDEB dos anos iniciais da rede publica por municipio da UF.

    O IDEB enriquece o sinal de carencia de servico, mas nao e obrigatorio. Se o
    servidor do INEP estiver inacessivel no momento da coleta, a funcao devolve
    uma tabela vazia e o indice segue com os demais indicadores, em vez de
    interromper todo o pipeline por causa de uma unica fonte.
    """
    try:
        bruto = _abre_planilha(config)
    except (OSError, zipfile.BadZipFile) as erro:
        print(f"  aviso: IDEB indisponivel agora ({erro}); seguindo sem ele.")
        return pd.DataFrame(columns=["ideb_ai_2023"]).rename_axis("cod_ibge")

    coluna = config["inep"]["coluna_valor"]
    filtro = (bruto["SG_UF"] == config["uf"]) & (bruto["REDE"].str.strip() == "Pública")
    recorte = bruto.loc[filtro, ["CO_MUNICIPIO", coluna]].copy()

    recorte["cod_ibge"] = recorte["CO_MUNICIPIO"].map(codigo_ibge)
    recorte["ideb_ai_2023"] = pd.to_numeric(recorte[coluna], errors="coerce")

    return recorte.set_index("cod_ibge")[["ideb_ai_2023"]]


if __name__ == "__main__":
    config = carrega_config("fontes.json")
    bruto = _abre_planilha(config)
    print("redes disponiveis:", sorted(bruto["REDE"].dropna().str.strip().unique().tolist()))
    tabela = coleta_ideb(config)
    print(f"linhas rede publica BA: {len(tabela)}")
    print(f"faltando ideb: {tabela['ideb_ai_2023'].isna().sum()}")
    print("menores IDEB:")
    print(tabela.sort_values("ideb_ai_2023").head(3))
