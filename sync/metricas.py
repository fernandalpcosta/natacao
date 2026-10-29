"""Resume cada natação em métricas comparáveis para o painel (docs/data/metricas.json)."""
import json
import pathlib
import statistics

DATA = pathlib.Path(__file__).resolve().parent.parent / "docs" / "data"


def _pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))]


def resumo(s, d):
    pool = d.get("piscina_m") or s.get("piscina_m")
    out = {k: s[k] for k in ("id", "data", "tipo", "distancia_m", "tempo_nadando_s", "ritmo_100m_s", "piscinas")}
    out["treino"] = d.get("treino")
    mix = {}
    for l in d.get("piscinas", []):
        if pool:
            mix[l["nado"]] = mix.get(l["nado"], 0) + pool
    out["nados_m"] = mix
    # Só piscinas de crawl com braçadas contadas e tempo plausível.
    livre = [l for l in d.get("piscinas", [])
             if l["nado"] == "freestyle" and l["brac"] and pool and 0.35 <= l["s"] / pool <= 3]
    if len(livre) >= 8:
        ritmos = [l["s"] / pool * 100 for l in livre]
        out["livre_ritmo_100m_s"] = round(statistics.median(ritmos), 1)
        out["livre_ritmo_rapido_100m_s"] = round(_pct(ritmos, 0.1), 1)
        if pool == 25:
            out["livre_bracadas_25m"] = round(statistics.mean(l["brac"] for l in livre), 1)
            out["livre_swolf_25m"] = round(statistics.mean(l["s"] + l["brac"] for l in livre), 1)
    return out


def main():
    swims = json.loads((DATA / "swims.json").read_text())
    rows = []
    for s in swims:
        f = DATA / "swims" / f"{s['id']}.json"
        rows.append(resumo(s, json.loads(f.read_text()) if f.exists() else {}))
    (DATA / "metricas.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
