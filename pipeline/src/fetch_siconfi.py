"""
Coletor das financas municipais no SICONFI (Tesouro Nacional).

Para cada municipio busca a Declaracao de Contas Anuais e extrai duas coisas.
Do anexo de receitas tira a receita total e a receita tributaria propria, cuja
razao mede a autonomia fiscal, o quanto a cidade se sustenta sem depender de
repasse. Do anexo de despesas tira o investimento, a fatia do orcamento que
vira obra e servico novo.

Sao dois pedidos por municipio, entao cada resposta fica guardada em cache. Um
municipio que nao enviou a declaracao ao Tesouro volta vazio, e essa ausencia e
tratada mais adiante como sinal de opacidade, nao como erro.
"""

from __future__ import annotations

import json
import time

import pandas as pd

from .comum import DADOS_BRUTOS, carrega_config, codigo_ibge, get_json

CACHE = DADOS_BRUTOS / "siconfi"

CONTA_RECEITA_TOTAL = "ReceitasExcetoIntraOrcamentarias"
CONTA_RECEITA_PROPRIA = "RO1.1.0.0.00.0.0"  # Impostos, Taxas e Contribuicoes de Melhoria
CONTA_INVESTIMENTO = "DO4.4.00.00.00.00"  # 4.4.00.00.00 - Investimentos
COLUNA_RECEITA = "Receitas Brutas Realizadas"
COLUNAS_DESPESA = ("Despesas Liquidadas", "Despesas Pagas", "Despesas Empenhadas")


def coleta_entes_uf(config: dict) -> dict[str, float]:
    """Devolve {cod_ibge: populacao} apenas dos municipios da UF configurada."""
    bruto = get_json(config["siconfi"]["entes"], params={"uf": config["uf"]})
    uf_codigo = config["uf_codigo"]
    entes = {}
    for item in bruto.get("items", []):
        if item.get("esfera") != "M":
            continue
        cod = codigo_ibge(item.get("cod_ibge"))
        if cod.startswith(uf_codigo):
            entes[cod] = item.get("populacao")
    return entes


def _dca(config: dict, id_ente: str, anexo: str, rotulo: str) -> list[dict]:
    """Busca um anexo da DCA de um municipio, com cache em disco."""
    CACHE.mkdir(parents=True, exist_ok=True)
    arquivo = CACHE / f"{rotulo}_{id_ente}.json"
    if arquivo.exists():
        with open(arquivo, encoding="utf-8") as f:
            return json.load(f)

    dados = get_json(
        config["siconfi"]["dca"],
        params={"an_exercicio": config["siconfi"]["ano"], "no_anexo": anexo, "id_ente": id_ente},
        timeout=90,
    )
    items = dados.get("items", [])
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
    time.sleep(0.15)  # gentileza com a API
    return items


def _valor(items: list[dict], cod_conta: str, colunas) -> float | None:
    """Encontra o valor de uma conta, testando as colunas na ordem de preferencia."""
    if isinstance(colunas, str):
        colunas = (colunas,)
    for coluna in colunas:
        for item in items:
            if item.get("cod_conta") == cod_conta and item.get("coluna") == coluna:
                try:
                    return float(item["valor"])
                except (TypeError, ValueError):
                    return None
    return None


def coleta_financas(config: dict, municipios: list[str] | None = None) -> pd.DataFrame:
    """Devolve receita, autonomia fiscal e investimento per capita por municipio."""
    entes = coleta_entes_uf(config)
    codigos = municipios or list(entes)

    conf = config["siconfi"]
    linhas = []
    for i, cod in enumerate(codigos, 1):
        receitas = _dca(config, cod, conf["anexo_receitas"], "ic")
        despesas = _dca(config, cod, conf["anexo_despesas"], "id")

        receita_total = _valor(receitas, CONTA_RECEITA_TOTAL, COLUNA_RECEITA)
        receita_propria = _valor(receitas, CONTA_RECEITA_PROPRIA, COLUNA_RECEITA)
        investimento = _valor(despesas, CONTA_INVESTIMENTO, COLUNAS_DESPESA)
        populacao = entes.get(cod)

        enviou = bool(receitas)
        autonomia = (receita_propria / receita_total) if (receita_propria and receita_total) else None
        investimento_pc = (investimento / populacao) if (investimento and populacao) else None

        linhas.append(
            {
                "cod_ibge": cod,
                "enviou_dca": enviou,
                "receita_total": receita_total,
                "autonomia_fiscal": round(autonomia, 4) if autonomia is not None else None,
                "investimento_pc": round(investimento_pc, 2) if investimento_pc is not None else None,
            }
        )
        if i % 50 == 0:
            print(f"  siconfi {i}/{len(codigos)}")

    return pd.DataFrame(linhas).set_index("cod_ibge")


if __name__ == "__main__":
    config = carrega_config("fontes.json")
    amostra = ["2913606", "2900306", "2916500"]  # Ilheus, Acajutiba, um de baixo IDHM
    tabela = coleta_financas(config, amostra)
    print(tabela)
