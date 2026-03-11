# API Choice

- Étudiant : VELOSO Alexis
- API choisie : Open-Meteo, RestCountries, PokéAPI, JokeAPI, Dog CEO
- URL base :
  - https://api.open-meteo.com/v1
  - https://restcountries.com/v3.1
  - https://pokeapi.co/api/v2
  - https://v2.jokeapi.dev
  - https://dog.ceo/api
- Documentation officielle / README :
  - Open-Meteo : https://open-meteo.com/en/docs
  - RestCountries : https://restcountries.com/
  - PokéAPI : https://pokeapi.co/docs/v2
  - JokeAPI : https://jokeapi.dev/
  - Dog CEO : https://dog.ceo/dog-api/
- Auth : None (aucune clé API requise pour les 5 APIs)
- Endpoints testés :
  - GET https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true
  - GET https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35
  - GET https://api.open-meteo.com/v1/forecast?latitude=999&longitude=999&current_weather=true
  - GET https://restcountries.com/v3.1/name/france
  - GET https://restcountries.com/v3.1/name/germany
  - GET https://restcountries.com/v3.1/alpha/FR
  - GET https://restcountries.com/v3.1/name/xyzinexistant123
  - GET https://pokeapi.co/api/v2/pokemon/pikachu
  - GET https://pokeapi.co/api/v2/pokemon/1
  - GET https://pokeapi.co/api/v2/pokemon/xxxxxxinexistant
  - GET https://v2.jokeapi.dev/joke/Any?safe-mode
  - GET https://v2.jokeapi.dev/joke/Programming?safe-mode
  - GET https://v2.jokeapi.dev/joke/CategorieQuiNExistePas
  - GET https://dog.ceo/api/breeds/image/random
  - GET https://dog.ceo/api/breeds/list/all
  - GET https://dog.ceo/api/breed/husky/images/random
  - GET https://dog.ceo/api/breed/racexxinexistante/images/random
- Hypothèses de contrat (champs attendus, types, codes) :

  ### Open-Meteo
  | Champ | Type | Contrainte |
  |-------|------|------------|
  | latitude | float | présent dans la réponse |
  | longitude | float | présent dans la réponse |
  | current_weather | object | présent si paramètre demandé |
  | current_weather.temperature | float/int | nombre valide |
  | current_weather.windspeed | float/int | nombre valide |
  | current_weather.weathercode | int | présent |
  - HTTP 200 sur coordonnées valides
  - HTTP 400 sur coordonnées hors plage (latitude=999)

  ### RestCountries
  | Champ | Type | Contrainte |
  |-------|------|------------|
  | name | object | présent |
  | capital | list | présent |
  | population | int | strictement positif |
  | region | string | chaîne non vide |
  | cca2 | string | exactement 2 lettres majuscules |
  - HTTP 200 sur pays valide, réponse de type liste
  - HTTP 404 sur pays inexistant

  ### PokéAPI
  | Champ | Type | Contrainte |
  |-------|------|------------|
  | id | int | = 25 pour pikachu |
  | name | string | = "pikachu" |
  | base_experience | int | présent |
  | height | int | présent |
  | weight | int | présent |
  | abilities | list | non vide, ability.name = string, is_hidden = bool |
  | types | list | non vide |
  - HTTP 200 sur pokémon valide (par nom ou par id)
  - HTTP 404 sur pokémon inexistant

  ### JokeAPI
  | Champ | Type | Contrainte |
  |-------|------|------------|
  | error | bool | false sur requête valide |
  | category | string | correspond à la catégorie demandée |
  | id | int | >= 0 |
  | flags | object | dictionnaire non vide |
  - HTTP 200 sur catégorie valide
  - error=true ou HTTP 400 sur catégorie inexistante

  ### Dog CEO
  | Champ | Type | Contrainte |
  |-------|------|------------|
  | status | string | = "success" sur requête valide |
  | message | string | URL commençant par "https://" |
  | message (list) | object | dictionnaire de races non vide |
  - HTTP 200 sur race valide
  - HTTP 404 ou status="error" sur race inexistante
  - L'URL retournée contient le nom de la race demandée

- Limites / rate limiting connu :
  - Open-Meteo : pas de limite documentée, usage raisonnable conseillé (< 10 000 req/jour)
  - RestCountries : aucune limite officielle
  - PokéAPI : fair use, environ 100 req/min recommandé, cache conseillé
  - JokeAPI : 120 requêtes/minute par IP, filtre safe-mode disponible
  - Dog CEO : pas de limite documentée, usage raisonnable attendu
  - Notre solution : maximum 32 requêtes par run, toutes en GET, aucune écriture

- Risques (instabilité, downtime, CORS, etc.) :
  - Open-Meteo : très stable, projet open-source activement maintenu, risque quasi nul
  - RestCountries : hébergement communautaire, peut être lent ponctuellement, pas de SLA
  - PokéAPI : réponses volumineuses (> 100 ko), latence p95 élevée, cache CDN en place
  - JokeAPI : stable, contenu filtré en mode safe, dépend d'un projet communautaire
  - Dog CEO : stable, images hébergées sur un CDN, dépend d'un projet indépendant
  - Mitigation globale : timeout strict à 5s + 1 retry, gestion des codes 429 et 5xx
