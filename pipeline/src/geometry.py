"""
Geometria dos municipios para a Penumbra.

Usa a malha do IBGE para duas coisas. Primeiro calcula, para cada municipio, a
distancia ate a capital do estado, que entra no indice como um dos sinais de
invisibilidade, a ideia de que quem esta longe da capital some do radar.
Segundo prepara uma versao simplificada do desenho de cada municipio, leve o
bastante para o mapa carregar rapido no navegador.
"""

from __future__ import annotations

import math

from shapely.geometry import shape

from .comum import carrega_config, codigo_ibge, get_json


def _malha(config: dict) -> dict:
    """Baixa o GeoJSON com o contorno de cada municipio da UF."""
    url = config["ibge"]["malha_geojson"].format(uf=config["uf"])
    return get_json(url, timeout=120)


def _ponto_interno(geometria) -> tuple[float, float]:
    """Devolve um ponto (longitude, latitude) garantidamente dentro do municipio.

    O centro geometrico as vezes cai fora de formas recortadas, entao usamos o
    ponto representativo do shapely, que sempre fica dentro do poligono.
    """
    ponto = shape(geometria).representative_point()
    return ponto.x, ponto.y


def _haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia em quilometros entre dois pontos (longitude, latitude)."""
    lon1, lat1 = a
    lon2, lat2 = b
    raio = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    sen = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * raio * math.asin(math.sqrt(sen))


def calcula_distancias(config: dict) -> dict[str, float]:
    """Devolve {cod_ibge: distancia em km ate a capital}."""
    malha = _malha(config)
    capital = codigo_ibge(config["capital_codigo"])

    pontos: dict[str, tuple[float, float]] = {}
    for feature in malha["features"]:
        cod = codigo_ibge(feature["properties"]["codarea"])
        pontos[cod] = _ponto_interno(feature["geometry"])

    ponto_capital = pontos[capital]
    return {cod: round(_haversine(p, ponto_capital), 1) for cod, p in pontos.items()}


def malha_simplificada(config: dict, tolerancia: float = 0.01) -> dict:
    """Devolve o GeoJSON com a geometria simplificada, pronto para enriquecer.

    A tolerancia controla o quanto o contorno e suavizado. Valores maiores
    deixam o arquivo mais leve ao custo de menos detalhe na borda.
    """
    malha = _malha(config)
    for feature in malha["features"]:
        cod = codigo_ibge(feature["properties"]["codarea"])
        simplificada = shape(feature["geometry"]).simplify(tolerancia, preserve_topology=True)
        feature["geometry"] = simplificada.__geo_interface__
        feature["properties"] = {"cod_ibge": cod}
    return malha


if __name__ == "__main__":
    config = carrega_config("fontes.json")
    distancias = calcula_distancias(config)
    print(f"municipios com distancia: {len(distancias)}")
    ordenado = sorted(distancias.items(), key=lambda x: x[1])
    print("mais perto da capital:", ordenado[:3])
    print("mais longe da capital:", ordenado[-3:])
