
"""
tests.py — Tests pour Open-Meteo, RestCountries et PokéAPI
Chaque test retourne un dict : {name, status, latency_ms, details}
"""

from tester.client import get

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _pass(name, latency_ms, details=""):
    return {"name": name, "status": "PASS", "latency_ms": latency_ms, "details": details}

def _fail(name, latency_ms, details=""):
    return {"name": name, "status": "FAIL", "latency_ms": latency_ms, "details": details}

def _error(name, details=""):
    return {"name": name, "status": "ERROR", "latency_ms": None, "details": details}


# ─────────────────────────────────────────────
#  OPEN-METEO (météo, no auth)
#  Base : https://api.open-meteo.com/v1
# ─────────────────────────────────────────────

BASE_METEO = "https://api.open-meteo.com/v1"

def test_meteo_status_200():
    """GET /forecast doit retourner 200"""
    r = get(f"{BASE_METEO}/forecast", params={
        "latitude": 48.85, "longitude": 2.35, "current_weather": "true"
    })
    if r["error"]:
        return _error("meteo_status_200", r["error"])
    if r["status"] == 200:
        return _pass("meteo_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("meteo_status_200", r["latency_ms"], f"HTTP {r['status']} attendu 200")

def test_meteo_champs_obligatoires():
    """La réponse doit contenir latitude, longitude, current_weather"""
    r = get(f"{BASE_METEO}/forecast", params={
        "latitude": 48.85, "longitude": 2.35, "current_weather": "true"
    })
    if r["error"]:
        return _error("meteo_champs_obligatoires", r["error"])
    required = ["latitude", "longitude", "current_weather"]
    missing = [k for k in required if k not in (r["json"] or {})]
    if not missing:
        return _pass("meteo_champs_obligatoires", r["latency_ms"], "Tous les champs présents")
    return _fail("meteo_champs_obligatoires", r["latency_ms"], f"Champs manquants : {missing}")

def test_meteo_current_weather_types():
    """current_weather doit contenir temperature (float/int) et windspeed (float/int)"""
    r = get(f"{BASE_METEO}/forecast", params={
        "latitude": 48.85, "longitude": 2.35, "current_weather": "true"
    })
    if r["error"]:
        return _error("meteo_current_weather_types", r["error"])
    cw = (r["json"] or {}).get("current_weather", {})
    errors = []
    for field in ["temperature", "windspeed", "weathercode"]:
        if field not in cw:
            errors.append(f"'{field}' manquant")
        elif not isinstance(cw[field], (int, float)):
            errors.append(f"'{field}' devrait être un nombre, got {type(cw[field]).__name__}")
    if not errors:
        return _pass("meteo_current_weather_types", r["latency_ms"], str(cw))
    return _fail("meteo_current_weather_types", r["latency_ms"], "; ".join(errors))

def test_meteo_coordonnees_invalides():
    """Latitude invalide (999) → doit retourner 400"""
    r = get(f"{BASE_METEO}/forecast", params={
        "latitude": 999, "longitude": 999, "current_weather": "true"
    })
    if r["error"]:
        return _error("meteo_coordonnees_invalides", r["error"])
    if r["status"] == 400:
        return _pass("meteo_coordonnees_invalides", r["latency_ms"], "400 reçu comme attendu")
    return _fail("meteo_coordonnees_invalides", r["latency_ms"], f"Attendu 400, reçu {r['status']}")

def test_meteo_latitude_type():
    """La latitude retournée doit être un float"""
    r = get(f"{BASE_METEO}/forecast", params={
        "latitude": 48.85, "longitude": 2.35, "current_weather": "true"
    })
    if r["error"]:
        return _error("meteo_latitude_type", r["error"])
    lat = (r["json"] or {}).get("latitude")
    if isinstance(lat, (int, float)):
        return _pass("meteo_latitude_type", r["latency_ms"], f"latitude={lat}")
    return _fail("meteo_latitude_type", r["latency_ms"], f"Type inattendu : {type(lat).__name__}")

def test_meteo_sans_current_weather():
    """Sans paramètre current_weather → 200 mais pas de current_weather dans la réponse"""
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 48.85, "longitude": 2.35})
    if r["error"]:
        return _error("meteo_sans_current_weather", r["error"])
    if r["status"] != 200:
        return _fail("meteo_sans_current_weather", r["latency_ms"], f"HTTP {r['status']}")
    cw = (r["json"] or {}).get("current_weather")
    if cw is None:
        return _pass("meteo_sans_current_weather", r["latency_ms"], "current_weather absent comme attendu")
    return _fail("meteo_sans_current_weather", r["latency_ms"], "current_weather présent alors que non demandé")


# ─────────────────────────────────────────────
#  RESTCOUNTRIES (pays, no auth)
#  Base : https://restcountries.com/v3.1
# ─────────────────────────────────────────────

BASE_COUNTRIES = "https://restcountries.com/v3.1"

def test_countries_status_200():
    """GET /name/france → 200"""
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]:
        return _error("countries_status_200", r["error"])
    if r["status"] == 200:
        return _pass("countries_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("countries_status_200", r["latency_ms"], f"HTTP {r['status']} attendu 200")

def test_countries_champs_obligatoires():
    """La France doit avoir name, capital, population, region"""
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]:
        return _error("countries_champs_obligatoires", r["error"])
    data = r["json"]
    if not isinstance(data, list) or len(data) == 0:
        return _fail("countries_champs_obligatoires", r["latency_ms"], "Réponse vide ou non-liste")
    country = data[0]
    required = ["name", "capital", "population", "region"]
    missing = [k for k in required if k not in country]
    if not missing:
        return _pass("countries_champs_obligatoires", r["latency_ms"], "Tous les champs présents")
    return _fail("countries_champs_obligatoires", r["latency_ms"], f"Manquants : {missing}")

def test_countries_population_type():
    """population doit être un entier positif"""
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]:
        return _error("countries_population_type", r["error"])
    data = r["json"]
    if not isinstance(data, list) or not data:
        return _fail("countries_population_type", r["latency_ms"], "Réponse invalide")
    pop = data[0].get("population")
    if isinstance(pop, int) and pop > 0:
        return _pass("countries_population_type", r["latency_ms"], f"population={pop}")
    return _fail("countries_population_type", r["latency_ms"], f"population invalide : {pop}")

def test_countries_pays_invalide():
    """Pays inexistant → 404"""
    r = get(f"{BASE_COUNTRIES}/name/xyzinexistant123")
    if r["error"]:
        return _error("countries_pays_invalide", r["error"])
    if r["status"] == 404:
        return _pass("countries_pays_invalide", r["latency_ms"], "404 reçu comme attendu")
    return _fail("countries_pays_invalide", r["latency_ms"], f"Attendu 404, reçu {r['status']}")

def test_countries_region_string():
    """region doit être une chaîne non vide"""
    r = get(f"{BASE_COUNTRIES}/name/germany")
    if r["error"]:
        return _error("countries_region_string", r["error"])
    data = r["json"]
    if not isinstance(data, list) or not data:
        return _fail("countries_region_string", r["latency_ms"], "Réponse invalide")
    region = data[0].get("region")
    if isinstance(region, str) and len(region) > 0:
        return _pass("countries_region_string", r["latency_ms"], f"region='{region}'")
    return _fail("countries_region_string", r["latency_ms"], f"region invalide : {region}")

def test_countries_code_alpha():
    """GET /alpha/FR → 200 et cca2='FR'"""
    r = get(f"{BASE_COUNTRIES}/alpha/FR")
    if r["error"]:
        return _error("countries_code_alpha", r["error"])
    if r["status"] != 200:
        return _fail("countries_code_alpha", r["latency_ms"], f"HTTP {r['status']}")
    data = r["json"]
    if not isinstance(data, list) or not data:
        return _fail("countries_code_alpha", r["latency_ms"], "Réponse invalide")
    cca2 = data[0].get("cca2")
    if cca2 == "FR":
        return _pass("countries_code_alpha", r["latency_ms"], f"cca2='{cca2}'")
    return _fail("countries_code_alpha", r["latency_ms"], f"cca2 inattendu : {cca2}")

def test_countries_liste_response_type():
    """La réponse de /name/france doit être une liste"""
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]:
        return _error("countries_liste_response_type", r["error"])
    if isinstance(r["json"], list):
        return _pass("countries_liste_response_type", r["latency_ms"], f"{len(r['json'])} résultat(s)")
    return _fail("countries_liste_response_type", r["latency_ms"], f"Type reçu : {type(r['json']).__name__}")


# ─────────────────────────────────────────────
#  POKÉAPI (no auth)
#  Base : https://pokeapi.co/api/v2
# ─────────────────────────────────────────────

BASE_POKE = "https://pokeapi.co/api/v2"

def test_poke_status_200():
    """GET /pokemon/pikachu → 200"""
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]:
        return _error("poke_status_200", r["error"])
    if r["status"] == 200:
        return _pass("poke_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("poke_status_200", r["latency_ms"], f"HTTP {r['status']} attendu 200")

def test_poke_champs_obligatoires():
    """Pikachu doit avoir id, name, base_experience, height, weight, abilities, types"""
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]:
        return _error("poke_champs_obligatoires", r["error"])
    required = ["id", "name", "base_experience", "height", "weight", "abilities", "types"]
    missing = [k for k in required if k not in (r["json"] or {})]
    if not missing:
        return _pass("poke_champs_obligatoires", r["latency_ms"], "Tous les champs présents")
    return _fail("poke_champs_obligatoires", r["latency_ms"], f"Manquants : {missing}")

def test_poke_name_string():
    """Le champ name doit être 'pikachu'"""
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]:
        return _error("poke_name_string", r["error"])
    name = (r["json"] or {}).get("name")
    if name == "pikachu":
        return _pass("poke_name_string", r["latency_ms"], f"name='{name}'")
    return _fail("poke_name_string", r["latency_ms"], f"name inattendu : {name}")

def test_poke_id_entier():
    """id de pikachu doit être 25"""
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]:
        return _error("poke_id_entier", r["error"])
    pid = (r["json"] or {}).get("id")
    if pid == 25:
        return _pass("poke_id_entier", r["latency_ms"], f"id={pid}")
    return _fail("poke_id_entier", r["latency_ms"], f"id inattendu : {pid}")

def test_poke_pokemon_invalide():
    """Pokémon inexistant → 404"""
    r = get(f"{BASE_POKE}/pokemon/xxxxxxinexistant")
    if r["error"]:
        return _error("poke_pokemon_invalide", r["error"])
    if r["status"] == 404:
        return _pass("poke_pokemon_invalide", r["latency_ms"], "404 reçu comme attendu")
    return _fail("poke_pokemon_invalide", r["latency_ms"], f"Attendu 404, reçu {r['status']}")

def test_poke_types_liste():
    """types doit être une liste non vide"""
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]:
        return _error("poke_types_liste", r["error"])
    types = (r["json"] or {}).get("types")
    if isinstance(types, list) and len(types) > 0:
        noms = [t.get("type", {}).get("name", "?") for t in types]
        return _pass("poke_types_liste", r["latency_ms"], f"types={noms}")
    return _fail("poke_types_liste", r["latency_ms"], f"types invalide : {types}")

def test_poke_par_id():
    """GET /pokemon/1 (Bulbasaur) → 200 et name='bulbasaur'"""
    r = get(f"{BASE_POKE}/pokemon/1")
    if r["error"]:
        return _error("poke_par_id", r["error"])
    if r["status"] != 200:
        return _fail("poke_par_id", r["latency_ms"], f"HTTP {r['status']}")
    name = (r["json"] or {}).get("name")
    if name == "bulbasaur":
        return _pass("poke_par_id", r["latency_ms"], f"name='{name}'")
    return _fail("poke_par_id", r["latency_ms"], f"name inattendu : {name}")

def test_poke_ability_structure():
    """abilities[0] doit contenir ability.name (str) et is_hidden (bool)"""
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]:
        return _error("poke_ability_structure", r["error"])
    abilities = (r["json"] or {}).get("abilities", [])
    if not abilities:
        return _fail("poke_ability_structure", r["latency_ms"], "abilities vide")
    a = abilities[0]
    errors = []
    if not isinstance(a.get("ability", {}).get("name"), str):
        errors.append("ability.name n'est pas une string")
    if not isinstance(a.get("is_hidden"), bool):
        errors.append("is_hidden n'est pas un bool")
    if not errors:
        return _pass("poke_ability_structure", r["latency_ms"], f"ability='{a['ability']['name']}'")
    return _fail("poke_ability_structure", r["latency_ms"], "; ".join(errors))


# ─────────────────────────────────────────────
#  REGISTRE DE TOUS LES TESTS
# ─────────────────────────────────────────────

ALL_TESTS = [
    # Open-Meteo
    ("Open-Meteo", test_meteo_status_200),
    ("Open-Meteo", test_meteo_champs_obligatoires),
    ("Open-Meteo", test_meteo_current_weather_types),
    ("Open-Meteo", test_meteo_coordonnees_invalides),
    ("Open-Meteo", test_meteo_latitude_type),
    ("Open-Meteo", test_meteo_sans_current_weather),
    # RestCountries
    ("RestCountries", test_countries_status_200),
    ("RestCountries", test_countries_champs_obligatoires),
    ("RestCountries", test_countries_population_type),
    ("RestCountries", test_countries_pays_invalide),
    ("RestCountries", test_countries_region_string),
    ("RestCountries", test_countries_code_alpha),
    ("RestCountries", test_countries_liste_response_type),
    # PokéAPI
    ("PokéAPI", test_poke_status_200),
    ("PokéAPI", test_poke_champs_obligatoires),
    ("PokéAPI", test_poke_name_string),
    ("PokéAPI", test_poke_id_entier),
    ("PokéAPI", test_poke_pokemon_invalide),
    ("PokéAPI", test_poke_types_liste),
    ("PokéAPI", test_poke_par_id),
    ("PokéAPI", test_poke_ability_structure),
]
