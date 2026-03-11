# API Choice

- **Étudiant** : [Votre nom]
- **APIs choisies** : Open-Meteo, RestCountries, PokéAPI
- **URL base** :
  - https://api.open-meteo.com/v1
  - https://restcountries.com/v3.1
  - https://pokeapi.co/api/v2
- **Documentation officielle / README** :
  - Open-Meteo : https://open-meteo.com/en/docs
  - RestCountries : https://restcountries.com/
  - PokéAPI : https://pokeapi.co/docs/v2
- **Auth** : None (aucune clé API requise pour les 3 APIs)

---

## Endpoints testés

### Open-Meteo
  - `GET /forecast?latitude=48.85&longitude=2.35&current_weather=true`
  - `GET /forecast?latitude=48.85&longitude=2.35` (sans current_weather)
  - `GET /forecast?latitude=999&longitude=999` (entrée invalide → 400 attendu)

### RestCountries
  - `GET /name/france`
  - `GET /name/germany`
  - `GET /alpha/FR`
  - `GET /name/xyzinexistant123` (entrée invalide → 404 attendu)

### PokéAPI
  - `GET /pokemon/pikachu`
  - `GET /pokemon/1`
  - `GET /pokemon/xxxxxxinexistant` (entrée invalide → 404 attendu)

---

## Hypothèses de contrat (champs attendus, types, codes)

### Open-Meteo
| Champ | Type | Contrainte |
|-------|------|-----------|
| `latitude` | float | présent dans la réponse |
| `longitude` | float | présent dans la réponse |
| `current_weather` | object | présent si demandé |
| `current_weather.temperature` | float/int | nombre valide |
| `current_weather.windspeed` | float/int | nombre valide |
| `current_weather.weathercode` | int | présent |

- HTTP 200 sur requête valide
- HTTP 400 sur coordonnées hors plage (ex: latitude=999)

### RestCountries
| Champ | Type | Contrainte |
|-------|------|-----------|
| `name` | object | présent |
| `capital` | list | présent |
| `population` | int | > 0 |
| `region` | string | non vide |
| `cca2` | string | 2 lettres majuscules |

- HTTP 200 sur pays valide, réponse est une liste
- HTTP 404 sur pays inexistant

### PokéAPI
| Champ | Type | Contrainte |
|-------|------|-----------|
| `id` | int | = 25 pour pikachu |
| `name` | string | = "pikachu" |
| `base_experience` | int | présent |
| `height` | int | présent |
| `weight` | int | présent |
| `abilities` | list | non vide, chaque item a `ability.name` (str) et `is_hidden` (bool) |
| `types` | list | non vide |

- HTTP 200 sur pokémon valide (nom ou id)
- HTTP 404 sur pokémon inexistant

---

## Limites / rate limiting connu

- **Open-Meteo** : Pas de limite documentée sur usage raisonnable. Recommande < 10 000 req/jour.
- **RestCountries** : Aucune limite officielle documentée. Usage respectueux attendu.
- **PokéAPI** : Fair use recommandé, environ 100 req/min max. Cache fortement conseillé.

Notre solution est limitée à **max 21 requêtes par run** (GET uniquement, non destructif).

---

## Risques identifiés

| API | Risque | Mitigation |
|-----|--------|-----------|
| Open-Meteo | Très stable, open-source | Timeout 5s + 1 retry |
| RestCountries | Parfois lent, hébergement communautaire | Timeout 5s + 1 retry |
| PokéAPI | Réponses volumineuses, latence variable | Timeout 5s + 1 retry, tests ciblés sur champs clés |

---

## Planification

> ⚠️ La tâche planifiée automatique (Scheduled Task PythonAnywhere) nécessite un compte payant.
> Le run peut être déclenché **manuellement** via la route `/run` ou `/run/json` depuis le dashboard.

Pour activer la planification avec un compte payant, ajouter dans **Scheduled Tasks** :
```bash
cd /home/<user>/mysite && python -c "from tester.runner import run_all; import storage; storage.save_run(run_all())"
```

---

## Checklist

- [x] Repo GitHub créé
- [x] Tests implémentés (21 tests, ≥ 6 requis)
- [x] Timeout (5s) + 1 retry max
- [x] Gestion 429 (backoff `Retry-After`) et 5xx (retry)
- [x] Enregistrement des runs (SQLite via `storage.py`)
- [x] Dashboard accessible (`/dashboard`)
- [x] Endpoint `/health`
- [x] Export JSON (`/export`)
- [ ] Exécution planifiée (nécessite compte PythonAnywhere payant)
