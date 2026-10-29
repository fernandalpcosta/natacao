"""Baixa as natações novas da Garmin e grava as métricas em docs/data/."""
import json
import pathlib
import sys

import metricas
from fit_swim import parse
from garmin import Garmin

DATA = pathlib.Path(__file__).resolve().parent.parent / "docs" / "data"
DETAIL = DATA / "swims"
INDEX = DATA / "swims.json"


def summary(a):
    dist = a.get("distance") or 0
    moving = a.get("movingDuration") or a.get("duration") or 0
    return {
        "id": a["activityId"],
        "data": a["startTimeLocal"][:10],  # só a data: sem horário nem nome (que traz a cidade)
        "tipo": a["activityType"]["typeKey"],
        "distancia_m": round(dist, 1),
        "tempo_s": round(a.get("duration") or 0, 1),
        "tempo_nadando_s": round(moving, 1),
        "ritmo_100m_s": round(moving / dist * 100, 1) if dist else None,
        "swolf": a.get("averageSwolf"),
        "bracadas_min": a.get("averageSwimCadenceInStrokesPerMinute"),
        "bracadas_piscina": a.get("avgStrokes"),
        "piscinas": a.get("activeLengths"),
        "piscina_m": (a.get("poolLength") or 0) / 100 or None,
        "melhor_100m_s": a.get("fastestSplit_100"),
    }


def main():
    DETAIL.mkdir(parents=True, exist_ok=True)
    index = {s["id"]: s for s in json.loads(INDEX.read_text())} if INDEX.exists() else {}
    g = Garmin()
    novas = 0
    for a in g.all_activities():
        if "swim" not in a["activityType"]["typeKey"]:
            continue
        aid = a["activityId"]
        index[aid] = summary(a)
        out = DETAIL / f"{aid}.json"
        if out.exists():
            continue
        try:
            detail = parse(g.download(aid))
        except Exception as e:  # um arquivo ruim não deve parar a sincronização
            print(f"aviso: {aid}: {e}", file=sys.stderr)
            continue
        out.write_text(json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
        novas += 1
    swims = sorted(index.values(), key=lambda s: (s["data"], s["id"]), reverse=True)
    INDEX.write_text(json.dumps(swims, ensure_ascii=False, indent=1))
    metricas.main()
    print(f"{len(swims)} natações no total, {novas} novas")


if __name__ == "__main__":
    import os
    import urllib.error
    try:
        main()
    except urllib.error.HTTPError as e:
        # ::error:: aparece como aviso no resumo da execução no GitHub.
        chave = "presente" if os.environ.get("GARMIN_PERSONAL_API_KEY") else "AUSENTE"
        print(f"::error::Garmin respondeu HTTP {e.code} em {e.url.split('?')[0]} (chave {chave})")
        sys.exit(1)
