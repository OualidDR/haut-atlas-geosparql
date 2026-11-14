"""Phase 1 : collecte des données OpenStreetMap via l'API Overpass."""
import json
import time

import requests

from config import BBOX, OVERPASS_URL, RAW_DIR, USER_AGENT

# Une requête Overpass par couche. {bbox} sera remplacé automatiquement.
LAYERS = {
    "huts": """
        (
          node["tourism"="alpine_hut"]({bbox});
          way["tourism"="alpine_hut"]({bbox});
        );
        out center;
    """,
    "peaks": """
        node["natural"="peak"]({bbox});
        out;
    """,
    "water": """
        (
          node["natural"="spring"]({bbox});
          node["amenity"="drinking_water"]({bbox});
        );
        out;
    """,
    "villages": """
        node["place"~"^(village|hamlet)$"]({bbox});
        out;
    """,
    "trails": """
        way["highway"~"^(path|footway|track)$"]({bbox});
        out geom;
    """,
    "hiking_routes": """
        relation["route"="hiking"]({bbox});
        out geom;
    """,
    "park": """
        way["boundary"="national_park"]({bbox});
        out geom;
    """,
}


def run_overpass(query: str, max_retries: int = 4) -> dict:
    """Envoie une requête Overpass, en réessayant si le serveur est surchargé."""
    for attempt in range(1, max_retries + 1):
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers={"User-Agent": USER_AGENT},
            timeout=180,
        )
        # Erreurs temporaires : on attend de plus en plus longtemps, puis on réessaie
        if response.status_code in (429, 502, 503, 504):
            wait = 15 * attempt
            print(f"  Serveur occupé ({response.status_code}), "
                  f"nouvel essai dans {wait} s ({attempt}/{max_retries})")
            time.sleep(wait)
            continue
        # Toute autre erreur est définitive : on s'arrête
        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"Overpass indisponible après {max_retries} tentatives")


def main():
    s, w, n, e = BBOX
    bbox = f"{s},{w},{n},{e}"
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for name, template in LAYERS.items():
        query = "[out:json][timeout:90];" + template.format(bbox=bbox)
        data = run_overpass(query)

        out_file = RAW_DIR / f"{name}.json"
        out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{name:<15} {len(data['elements']):>5} éléments -> {out_file.name}")

        time.sleep(2)  # politesse : on n'enchaîne pas les requêtes trop vite


if __name__ == "__main__":
    main()