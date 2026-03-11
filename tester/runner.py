"""
runner.py — Exécute tous les tests et calcule les métriques QoS
"""

import datetime
import statistics
from tester.tests import ALL_TESTS


def run_all() -> dict:
    """Lance tous les tests et retourne un rapport complet."""
    results = []
    api_groups = {}

    for api_name, test_fn in ALL_TESTS:
        result = test_fn()
        result["api"] = api_name
        results.append(result)
        api_groups.setdefault(api_name, []).append(result)

    # ── Métriques globales ──
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    latencies = [r["latency_ms"] for r in results if r["latency_ms"] is not None]
    avg_latency = round(statistics.mean(latencies)) if latencies else None
    p95_latency = round(statistics.quantiles(latencies, n=20)[18]) if len(latencies) >= 5 else (max(latencies) if latencies else None)
    error_rate = round((failed + errors) / total, 4) if total else 0

    # ── Métriques par API ──
    per_api = {}
    for api_name, api_results in api_groups.items():
        api_lat = [r["latency_ms"] for r in api_results if r["latency_ms"] is not None]
        per_api[api_name] = {
            "total": len(api_results),
            "passed": sum(1 for r in api_results if r["status"] == "PASS"),
            "failed": sum(1 for r in api_results if r["status"] == "FAIL"),
            "errors": sum(1 for r in api_results if r["status"] == "ERROR"),
            "latency_avg_ms": round(statistics.mean(api_lat)) if api_lat else None,
            "latency_p95_ms": round(statistics.quantiles(api_lat, n=20)[18]) if len(api_lat) >= 5 else (max(api_lat) if api_lat else None),
        }

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "error_rate": error_rate,
            "latency_ms_avg": avg_latency,
            "latency_ms_p95": p95_latency,
            "availability": round(passed / total, 4) if total else 0,
        },
        "per_api": per_api,
        "tests": results,
    }
