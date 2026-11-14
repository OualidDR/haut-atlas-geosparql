"""Phase 1 : collecte des entités Wikidata (sommets, refuges) dans la zone d'étude."""
import json

from SPARQLWrapper import JSON, SPARQLWrapper

from config import BBOX, RAW_DIR, USER_AGENT, WIKIDATA_URL


def build_query() -> str:
    s, w, n, e = BBOX                 # ordre Overpass : (sud, ouest, nord, est)
    south_west = f"Point({w} {s})"    # ordre WKT : Point(longitude latitude)
    north_east = f"Point({e} {n})"

    return f"""
    SELECT ?item ?itemLabel ?type ?typeLabel ?altitude ?coord WHERE {{
      SERVICE wikibase:box {{
        ?item wdt:P625 ?coord .
        bd:serviceParam wikibase:cornerSouthWest "{south_west}"^^geo:wktLiteral .
        bd:serviceParam wikibase:cornerNorthEast "{north_east}"^^geo:wktLiteral .
      }}
      VALUES ?type {{ wd:Q8502 wd:Q207326 wd:Q182676 }}   # montagne, sommet, refuge
      ?item wdt:P31 ?type .
      OPTIONAL {{ ?item wdt:P2044 ?altitude . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en". }}
    }}
    """


def main():
    sparql = SPARQLWrapper(WIKIDATA_URL, agent=USER_AGENT)
    sparql.setQuery(build_query())
    sparql.setReturnFormat(JSON)
    data = sparql.queryAndConvert()

    rows = data["results"]["bindings"]
    items = {row["item"]["value"] for row in rows}
    print(f"Lignes renvoyées   : {len(rows)}")
    print(f"Entités distinctes : {len(items)}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RAW_DIR / "wikidata_entities.json"
    out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sauvegardé dans : {out_file}")


if __name__ == "__main__":
    main()
