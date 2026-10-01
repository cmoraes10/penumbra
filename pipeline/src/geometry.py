"""
Municipality geometry for Penumbra.

Uses the IBGE mesh for two purposes. First it computes, for each municipality,
the distance to the state capital, which enters the index as one of the
visibility signals: being far from the capital means falling off the radar.
Second it prepares a simplified version of each municipality outline, light
enough for the map to load quickly in the browser.
"""

from __future__ import annotations

import math

from shapely.geometry import shape

from .comum import load_config, ibge_code, get_json


def _fetch_mesh(config: dict) -> dict:
    """Downloads the GeoJSON with the outline of each municipality in the state."""
    url = config["ibge"]["malha_geojson"].format(uf=config["uf"])
    return get_json(url, timeout=120)


def _interior_point(geometry) -> tuple[float, float]:
    """Returns a point (longitude, latitude) guaranteed to be inside the municipality.

    The geometric centroid can fall outside concave or fragmented shapes, so the
    shapely representative point is used instead, which always lands inside the
    polygon.
    """
    point = shape(geometry).representative_point()
    return point.x, point.y


def _haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distance in kilometres between two (longitude, latitude) points."""
    lon1, lat1 = a
    lon2, lat2 = b
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    h = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(h))


def compute_distances(config: dict) -> dict[str, float]:
    """Returns {ibge_code: distance in km to the state capital}."""
    mesh = _fetch_mesh(config)
    capital = ibge_code(config["capital_codigo"])

    points: dict[str, tuple[float, float]] = {}
    for feature in mesh["features"]:
        cod = ibge_code(feature["properties"]["codarea"])
        points[cod] = _interior_point(feature["geometry"])

    capital_point = points[capital]
    return {cod: round(_haversine(p, capital_point), 1) for cod, p in points.items()}


def simplified_mesh(config: dict, tolerance: float = 0.01) -> dict:
    """Returns a GeoJSON with simplified geometry, ready to be enriched.

    tolerance controls how much the outline is smoothed. Higher values produce
    a smaller file at the cost of less border detail.
    """
    mesh = _fetch_mesh(config)
    for feature in mesh["features"]:
        cod = ibge_code(feature["properties"]["codarea"])
        simplified = shape(feature["geometry"]).simplify(tolerance, preserve_topology=True)
        feature["geometry"] = simplified.__geo_interface__
        feature["properties"] = {"cod_ibge": cod}
    return mesh


if __name__ == "__main__":
    config = load_config("fontes.json")
    distances = compute_distances(config)
    print(f"municipalities with distance: {len(distances)}")
    ordered = sorted(distances.items(), key=lambda x: x[1])
    print("closest to capital:", ordered[:3])
    print("furthest from capital:", ordered[-3:])
