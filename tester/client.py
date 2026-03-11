import time
import requests

TIMEOUT = 5  # secondes
MAX_RETRIES = 1


def get(url: str, params: dict = None) -> dict:
    """
    Effectue un GET avec timeout, 1 retry et mesure de latence.
    Retourne un dict avec: status, json, latency_ms, error
    """
    for attempt in range(MAX_RETRIES + 1):
        start = time.time()
        try:
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            latency_ms = round((time.time() - start) * 1000)

            # Gestion 429 : on attend et on retente
            if resp.status_code == 429 and attempt < MAX_RETRIES:
                retry_after = int(resp.headers.get("Retry-After", 2))
                time.sleep(retry_after)
                continue

            # Gestion 5xx : retry immédiat
            if resp.status_code >= 500 and attempt < MAX_RETRIES:
                time.sleep(1)
                continue

            try:
                body = resp.json()
            except Exception:
                body = None

            return {
                "status": resp.status_code,
                "json": body,
                "latency_ms": latency_ms,
                "error": None,
            }

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            return {"status": None, "json": None, "latency_ms": None, "error": "Timeout"}

        except requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            return {"status": None, "json": None, "latency_ms": None, "error": f"ConnectionError: {e}"}

        except Exception as e:
            return {"status": None, "json": None, "latency_ms": None, "error": str(e)}
