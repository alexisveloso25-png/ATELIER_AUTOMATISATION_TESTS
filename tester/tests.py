from tester.client import get

BASE_METEO     = "https://api.open-meteo.com/v1"
BASE_COUNTRIES = "https://restcountries.com/v3.1"
BASE_POKE      = "https://pokeapi.co/api/v2"
BASE_JOKE      = "https://v2.jokeapi.dev"
BASE_DOG       = "https://dog.ceo/api"


def _pass(name, latency_ms, details=""):
    return {"name": name, "status": "PASS", "latency_ms": latency_ms, "details": details}

def _fail(name, latency_ms, details=""):
    return {"name": name, "status": "FAIL", "latency_ms": latency_ms, "details": details}

def _error(name, details=""):
    return {"name": name, "status": "ERROR", "latency_ms": None, "details": details}


# ── OPEN-METEO ────────────────────────────────────────────────────────────────

def test_meteo_status_200():
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 48.85, "longitude": 2.35, "current_weather": "true"})
    if r["error"]: return _error("meteo_status_200", r["error"])
    if r["status"] == 200: return _pass("meteo_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("meteo_status_200", r["latency_ms"], f"Attendu 200, reçu {r['status']}")

def test_meteo_champs_obligatoires():
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 48.85, "longitude": 2.35, "current_weather": "true"})
    if r["error"]: return _error("meteo_champs_obligatoires", r["error"])
    missing = [k for k in ["latitude", "longitude", "current_weather"] if k not in (r["json"] or {})]
    if not missing: return _pass("meteo_champs_obligatoires", r["latency_ms"], "Tous les champs présents")
    return _fail("meteo_champs_obligatoires", r["latency_ms"], f"Manquants : {missing}")

def test_meteo_current_weather_types():
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 48.85, "longitude": 2.35, "current_weather": "true"})
    if r["error"]: return _error("meteo_current_weather_types", r["error"])
    cw = (r["json"] or {}).get("current_weather", {})
    errors = [f"'{f}' invalide" for f in ["temperature", "windspeed", "weathercode"] if not isinstance(cw.get(f), (int, float))]
    if not errors: return _pass("meteo_current_weather_types", r["latency_ms"], str(cw))
    return _fail("meteo_current_weather_types", r["latency_ms"], "; ".join(errors))

def test_meteo_coordonnees_invalides():
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 999, "longitude": 999, "current_weather": "true"})
    if r["error"]: return _error("meteo_coordonnees_invalides", r["error"])
    if r["status"] == 400: return _pass("meteo_coordonnees_invalides", r["latency_ms"], "400 reçu comme attendu")
    return _fail("meteo_coordonnees_invalides", r["latency_ms"], f"Attendu 400, reçu {r['status']}")

def test_meteo_latitude_type():
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 48.85, "longitude": 2.35, "current_weather": "true"})
    if r["error"]: return _error("meteo_latitude_type", r["error"])
    lat = (r["json"] or {}).get("latitude")
    if isinstance(lat, (int, float)): return _pass("meteo_latitude_type", r["latency_ms"], f"latitude={lat}")
    return _fail("meteo_latitude_type", r["latency_ms"], f"Type inattendu : {type(lat).__name__}")

def test_meteo_sans_current_weather():
    r = get(f"{BASE_METEO}/forecast", params={"latitude": 48.85, "longitude": 2.35})
    if r["error"]: return _error("meteo_sans_current_weather", r["error"])
    if r["status"] != 200: return _fail("meteo_sans_current_weather", r["latency_ms"], f"HTTP {r['status']}")
    if (r["json"] or {}).get("current_weather") is None:
        return _pass("meteo_sans_current_weather", r["latency_ms"], "current_weather absent comme attendu")
    return _fail("meteo_sans_current_weather", r["latency_ms"], "current_weather présent non demandé")


# ── RESTCOUNTRIES ─────────────────────────────────────────────────────────────

def test_countries_status_200():
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]: return _error("countries_status_200", r["error"])
    if r["status"] == 200: return _pass("countries_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("countries_status_200", r["latency_ms"], f"Attendu 200, reçu {r['status']}")

def test_countries_champs_obligatoires():
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]: return _error("countries_champs_obligatoires", r["error"])
    data = r["json"]
    if not isinstance(data, list) or not data: return _fail("countries_champs_obligatoires", r["latency_ms"], "Réponse vide")
    missing = [k for k in ["name", "capital", "population", "region"] if k not in data[0]]
    if not missing: return _pass("countries_champs_obligatoires", r["latency_ms"], "Tous les champs présents")
    return _fail("countries_champs_obligatoires", r["latency_ms"], f"Manquants : {missing}")

def test_countries_population_type():
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]: return _error("countries_population_type", r["error"])
    data = r["json"]
    if not isinstance(data, list) or not data: return _fail("countries_population_type", r["latency_ms"], "Réponse invalide")
    pop = data[0].get("population")
    if isinstance(pop, int) and pop > 0: return _pass("countries_population_type", r["latency_ms"], f"population={pop}")
    return _fail("countries_population_type", r["latency_ms"], f"population invalide : {pop}")

def test_countries_pays_invalide():
    r = get(f"{BASE_COUNTRIES}/name/xyzinexistant123")
    if r["error"]: return _error("countries_pays_invalide", r["error"])
    if r["status"] == 404: return _pass("countries_pays_invalide", r["latency_ms"], "404 reçu comme attendu")
    return _fail("countries_pays_invalide", r["latency_ms"], f"Attendu 404, reçu {r['status']}")

def test_countries_region_string():
    r = get(f"{BASE_COUNTRIES}/name/germany")
    if r["error"]: return _error("countries_region_string", r["error"])
    data = r["json"]
    if not isinstance(data, list) or not data: return _fail("countries_region_string", r["latency_ms"], "Réponse invalide")
    region = data[0].get("region")
    if isinstance(region, str) and len(region) > 0: return _pass("countries_region_string", r["latency_ms"], f"region='{region}'")
    return _fail("countries_region_string", r["latency_ms"], f"region invalide : {region}")

def test_countries_code_alpha():
    r = get(f"{BASE_COUNTRIES}/alpha/FR")
    if r["error"]: return _error("countries_code_alpha", r["error"])
    if r["status"] != 200: return _fail("countries_code_alpha", r["latency_ms"], f"HTTP {r['status']}")
    data = r["json"]
    if not isinstance(data, list) or not data: return _fail("countries_code_alpha", r["latency_ms"], "Réponse invalide")
    cca2 = data[0].get("cca2")
    if cca2 == "FR": return _pass("countries_code_alpha", r["latency_ms"], f"cca2='{cca2}'")
    return _fail("countries_code_alpha", r["latency_ms"], f"cca2 inattendu : {cca2}")

def test_countries_liste_response_type():
    r = get(f"{BASE_COUNTRIES}/name/france")
    if r["error"]: return _error("countries_liste_response_type", r["error"])
    if isinstance(r["json"], list): return _pass("countries_liste_response_type", r["latency_ms"], f"{len(r['json'])} résultat(s)")
    return _fail("countries_liste_response_type", r["latency_ms"], f"Type reçu : {type(r['json']).__name__}")


# ── POKÉAPI ───────────────────────────────────────────────────────────────────

def test_poke_status_200():
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]: return _error("poke_status_200", r["error"])
    if r["status"] == 200: return _pass("poke_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("poke_status_200", r["latency_ms"], f"Attendu 200, reçu {r['status']}")

def test_poke_champs_obligatoires():
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]: return _error("poke_champs_obligatoires", r["error"])
    missing = [k for k in ["id", "name", "base_experience", "height", "weight", "abilities", "types"] if k not in (r["json"] or {})]
    if not missing: return _pass("poke_champs_obligatoires", r["latency_ms"], "Tous les champs présents")
    return _fail("poke_champs_obligatoires", r["latency_ms"], f"Manquants : {missing}")

def test_poke_id_entier():
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]: return _error("poke_id_entier", r["error"])
    pid = (r["json"] or {}).get("id")
    if pid == 25: return _pass("poke_id_entier", r["latency_ms"], f"id={pid}")
    return _fail("poke_id_entier", r["latency_ms"], f"id inattendu : {pid}")

def test_poke_pokemon_invalide():
    r = get(f"{BASE_POKE}/pokemon/xxxxxxinexistant")
    if r["error"]: return _error("poke_pokemon_invalide", r["error"])
    if r["status"] == 404: return _pass("poke_pokemon_invalide", r["latency_ms"], "404 reçu comme attendu")
    return _fail("poke_pokemon_invalide", r["latency_ms"], f"Attendu 404, reçu {r['status']}")

def test_poke_types_liste():
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]: return _error("poke_types_liste", r["error"])
    types = (r["json"] or {}).get("types")
    if isinstance(types, list) and len(types) > 0:
        noms = [t.get("type", {}).get("name", "?") for t in types]
        return _pass("poke_types_liste", r["latency_ms"], f"types={noms}")
    return _fail("poke_types_liste", r["latency_ms"], f"types invalide : {types}")

def test_poke_par_id():
    r = get(f"{BASE_POKE}/pokemon/1")
    if r["error"]: return _error("poke_par_id", r["error"])
    if r["status"] != 200: return _fail("poke_par_id", r["latency_ms"], f"HTTP {r['status']}")
    name = (r["json"] or {}).get("name")
    if name == "bulbasaur": return _pass("poke_par_id", r["latency_ms"], f"name='{name}'")
    return _fail("poke_par_id", r["latency_ms"], f"name inattendu : {name}")

def test_poke_ability_structure():
    r = get(f"{BASE_POKE}/pokemon/pikachu")
    if r["error"]: return _error("poke_ability_structure", r["error"])
    abilities = (r["json"] or {}).get("abilities", [])
    if not abilities: return _fail("poke_ability_structure", r["latency_ms"], "abilities vide")
    a = abilities[0]
    errors = []
    if not isinstance(a.get("ability", {}).get("name"), str): errors.append("ability.name non string")
    if not isinstance(a.get("is_hidden"), bool): errors.append("is_hidden non bool")
    if not errors: return _pass("poke_ability_structure", r["latency_ms"], f"ability='{a['ability']['name']}'")
    return _fail("poke_ability_structure", r["latency_ms"], "; ".join(errors))


# ── JOKEAPI ───────────────────────────────────────────────────────────────────

def test_joke_status_200():
    r = get(f"{BASE_JOKE}/joke/Any", params={"safe-mode": ""})
    if r["error"]: return _error("joke_status_200", r["error"])
    if r["status"] == 200: return _pass("joke_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("joke_status_200", r["latency_ms"], f"Attendu 200, reçu {r['status']}")

def test_joke_champ_error_false():
    r = get(f"{BASE_JOKE}/joke/Any", params={"safe-mode": ""})
    if r["error"]: return _error("joke_champ_error_false", r["error"])
    error = (r["json"] or {}).get("error")
    if error is False: return _pass("joke_champ_error_false", r["latency_ms"], "error=false comme attendu")
    return _fail("joke_champ_error_false", r["latency_ms"], f"error inattendu : {error}")

def test_joke_category_string():
    r = get(f"{BASE_JOKE}/joke/Programming", params={"safe-mode": ""})
    if r["error"]: return _error("joke_category_string", r["error"])
    category = (r["json"] or {}).get("category")
    if isinstance(category, str) and category == "Programming":
        return _pass("joke_category_string", r["latency_ms"], f"category='{category}'")
    return _fail("joke_category_string", r["latency_ms"], f"category inattendu : {category}")

def test_joke_id_entier():
    r = get(f"{BASE_JOKE}/joke/Any", params={"safe-mode": ""})
    if r["error"]: return _error("joke_id_entier", r["error"])
    jid = (r["json"] or {}).get("id")
    if isinstance(jid, int) and jid >= 0:
        return _pass("joke_id_entier", r["latency_ms"], f"id={jid}")
    return _fail("joke_id_entier", r["latency_ms"], f"id invalide : {jid}")

def test_joke_categorie_invalide():
    r = get(f"{BASE_JOKE}/joke/CategorieQuiNExistePas")
    if r["error"]: return _error("joke_categorie_invalide", r["error"])
    if r["status"] == 400:
        return _pass("joke_categorie_invalide", r["latency_ms"], "400 reçu comme attendu")
    error_field = (r["json"] or {}).get("error")
    if error_field is True:
        return _pass("joke_categorie_invalide", r["latency_ms"], "error=true reçu comme attendu")
    return _fail("joke_categorie_invalide", r["latency_ms"], f"Attendu erreur, reçu status={r['status']}")

def test_joke_flags_objet():
    r = get(f"{BASE_JOKE}/joke/Any", params={"safe-mode": ""})
    if r["error"]: return _error("joke_flags_objet", r["error"])
    flags = (r["json"] or {}).get("flags")
    if isinstance(flags, dict) and len(flags) > 0:
        return _pass("joke_flags_objet", r["latency_ms"], f"flags={list(flags.keys())}")
    return _fail("joke_flags_objet", r["latency_ms"], f"flags invalide : {flags}")


# ── DOG CEO API ───────────────────────────────────────────────────────────────

def test_dog_status_200():
    r = get(f"{BASE_DOG}/breeds/image/random")
    if r["error"]: return _error("dog_status_200", r["error"])
    if r["status"] == 200: return _pass("dog_status_200", r["latency_ms"], f"HTTP {r['status']}")
    return _fail("dog_status_200", r["latency_ms"], f"Attendu 200, reçu {r['status']}")

def test_dog_status_success():
    r = get(f"{BASE_DOG}/breeds/image/random")
    if r["error"]: return _error("dog_status_success", r["error"])
    status = (r["json"] or {}).get("status")
    if status == "success": return _pass("dog_status_success", r["latency_ms"], "status='success'")
    return _fail("dog_status_success", r["latency_ms"], f"status inattendu : {status}")

def test_dog_message_url():
    r = get(f"{BASE_DOG}/breeds/image/random")
    if r["error"]: return _error("dog_message_url", r["error"])
    msg = (r["json"] or {}).get("message", "")
    if isinstance(msg, str) and msg.startswith("https://"):
        return _pass("dog_message_url", r["latency_ms"], f"URL valide : {msg[:50]}...")
    return _fail("dog_message_url", r["latency_ms"], f"message invalide : {msg}")

def test_dog_liste_races():
    r = get(f"{BASE_DOG}/breeds/list/all")
    if r["error"]: return _error("dog_liste_races", r["error"])
    if r["status"] != 200: return _fail("dog_liste_races", r["latency_ms"], f"HTTP {r['status']}")
    msg = (r["json"] or {}).get("message", {})
    if isinstance(msg, dict) and len(msg) > 0:
        return _pass("dog_liste_races", r["latency_ms"], f"{len(msg)} races trouvées")
    return _fail("dog_liste_races", r["latency_ms"], f"message invalide : {type(msg)}")

def test_dog_race_specifique():
    r = get(f"{BASE_DOG}/breed/husky/images/random")
    if r["error"]: return _error("dog_race_specifique", r["error"])
    if r["status"] == 200:
        msg = (r["json"] or {}).get("message", "")
        if "husky" in msg:
            return _pass("dog_race_specifique", r["latency_ms"], "URL contient 'husky'")
    return _fail("dog_race_specifique", r["latency_ms"], f"HTTP {r['status']} ou URL incorrecte")

def test_dog_race_invalide():
    r = get(f"{BASE_DOG}/breed/racexxinexistante/images/random")
    if r["error"]: return _error("dog_race_invalide", r["error"])
    if r["status"] == 404:
        return _pass("dog_race_invalide", r["latency_ms"], "404 reçu comme attendu")
    status_field = (r["json"] or {}).get("status")
    if status_field == "error":
        return _pass("dog_race_invalide", r["latency_ms"], "status='error' reçu comme attendu")
    return _fail("dog_race_invalide", r["latency_ms"], f"Attendu erreur, reçu {r['status']}")


# ── REGISTRE ──────────────────────────────────────────────────────────────────

ALL_TESTS = [
    ("Open-Meteo",     test_meteo_status_200),
    ("Open-Meteo",     test_meteo_champs_obligatoires),
    ("Open-Meteo",     test_meteo_current_weather_types),
    ("Open-Meteo",     test_meteo_coordonnees_invalides),
    ("Open-Meteo",     test_meteo_latitude_type),
    ("Open-Meteo",     test_meteo_sans_current_weather),
    ("RestCountries",  test_countries_status_200),
    ("RestCountries",  test_countries_champs_obligatoires),
    ("RestCountries",  test_countries_population_type),
    ("RestCountries",  test_countries_pays_invalide),
    ("RestCountries",  test_countries_region_string),
    ("RestCountries",  test_countries_code_alpha),
    ("RestCountries",  test_countries_liste_response_type),
    ("PokéAPI",        test_poke_status_200),
    ("PokéAPI",        test_poke_champs_obligatoires),
    ("PokéAPI",        test_poke_id_entier),
    ("PokéAPI",        test_poke_pokemon_invalide),
    ("PokéAPI",        test_poke_types_liste),
    ("PokéAPI",        test_poke_par_id),
    ("PokéAPI",        test_poke_ability_structure),
    ("JokeAPI",        test_joke_status_200),
    ("JokeAPI",        test_joke_champ_error_false),
    ("JokeAPI",        test_joke_category_string),
    ("JokeAPI",        test_joke_id_entier),
    ("JokeAPI",        test_joke_categorie_invalide),
    ("JokeAPI",        test_joke_flags_objet),
    ("Dog CEO",        test_dog_status_200),
    ("Dog CEO",        test_dog_status_success),
    ("Dog CEO",        test_dog_message_url),
    ("Dog CEO",        test_dog_liste_races),
    ("Dog CEO",        test_dog_race_specifique),
    ("Dog CEO",        test_dog_race_invalide),
]
