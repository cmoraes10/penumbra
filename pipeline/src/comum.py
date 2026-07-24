"""
Utilidades compartilhadas pelo pipeline da Penumbra.

Concentra o que todos os coletores precisam: leitura da configuracao, um cliente
HTTP com repeticao e espera progressiva para aguentar instabilidade de API, o
cache em disco dos downloads brutos e a padronizacao do codigo IBGE, que e a
chave que costura todas as fontes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config"
DADOS_BRUTOS = RAIZ / "data" / "raw"
DADOS_PROCESSADOS = RAIZ / "data" / "processed"

# alguns servidores publicos recusam requisicao sem um agente de navegador
CABECALHO = {"User-Agent": "Mozilla/5.0 (Penumbra pipeline de dados abertos)"}


def carrega_config(nome: str) -> dict:
    """Le um arquivo JSON da pasta de configuracao."""
    with open(CONFIG / nome, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def codigo_ibge(valor: Any) -> str:
    """Padroniza qualquer codigo de municipio para string de sete digitos.

    A API de localidades devolve o codigo como numero inteiro, enquanto as
    demais fontes usam texto. Sem essa padronizacao o cruzamento entre as
    tabelas falha em silencio.
    """
    return str(valor).strip().zfill(7)


def get_json(
    url: str,
    params: dict | None = None,
    tentativas: int = 4,
    espera_base: float = 1.5,
    timeout: int = 60,
) -> Any:
    """Faz um GET e devolve JSON, repetindo com espera progressiva em caso de falha.

    Erros de rede ou respostas 429 e 5xx sao tratados como temporarios e a
    funcao tenta de novo, dobrando a espera a cada rodada. Um 404 e definitivo e
    sobe na hora.
    """
    ultimo_erro: Exception | None = None
    for tentativa in range(tentativas):
        try:
            resposta = requests.get(url, params=params, headers=CABECALHO, timeout=timeout)
            if resposta.status_code == 404:
                resposta.raise_for_status()
            if resposta.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"status temporario {resposta.status_code}")
            resposta.raise_for_status()
            return resposta.json()
        except (requests.RequestException, ValueError) as erro:
            ultimo_erro = erro
            if tentativa < tentativas - 1:
                time.sleep(espera_base * (2 ** tentativa))
    raise RuntimeError(f"falha ao buscar {url}: {ultimo_erro}")


def baixa_arquivo(url: str, destino: Path, forcar: bool = False, timeout: int = 180) -> Path:
    """Baixa um arquivo grande para o cache local, reaproveitando se ja existir."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not forcar:
        return destino
    with requests.get(url, headers=CABECALHO, timeout=timeout, stream=True) as resposta:
        resposta.raise_for_status()
        with open(destino, "wb") as saida:
            for pedaco in resposta.iter_content(chunk_size=1 << 16):
                saida.write(pedaco)
    return destino


def salva_json(dados: Any, destino: Path) -> None:
    """Grava JSON legivel, preservando acentos."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as saida:
        json.dump(dados, saida, ensure_ascii=False, indent=2)
