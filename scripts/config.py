"""Configuration centrale du projet."""
from pathlib import Path

# Zone d'étude Imlil–Toubkal, au format Overpass : (sud, ouest, nord, est)
BBOX = (31.00, -8.00, 31.18, -7.82)

# Dossiers du projet
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

# Identification auprès des API (politique d'usage Overpass / Wikimedia)
USER_AGENT = "haut-atlas-geosparql/0.1 (https://github.com/OualidDR/haut-atlas-geosparql)"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
