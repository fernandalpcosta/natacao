"""Extrai métricas de natação de um .FIT, sem GPS e sem frequência cardíaca."""
import io
import zipfile

from fitparse import FitFile


def _fit_bytes(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".fit"))
        return z.read(name)


def _vals(msg):
    return {d.name: d.value for d in msg if d.value is not None}


def parse(zip_bytes):
    fit = FitFile(io.BytesIO(_fit_bytes(zip_bytes)))

    session = next((_vals(m) for m in fit.get_messages("session")), {})
    workout = next((_vals(m) for m in fit.get_messages("workout")), {})

    lengths = []
    for m in fit.get_messages("length"):
        v = _vals(m)
        if v.get("length_type") != "active":
            continue
        lengths.append({
            "nado": v.get("swim_stroke"),
            "s": round(v.get("total_timer_time", 0), 2),
            "brac": v.get("total_strokes"),
        })

    laps = []
    for m in fit.get_messages("lap"):
        v = _vals(m)
        dist = v.get("total_distance") or 0
        laps.append({
            "nado": v.get("swim_stroke"),
            "m": round(dist, 1),
            "s": round(v.get("total_timer_time", 0), 2),
            "piscinas": v.get("num_active_lengths", 0),
            "descanso": dist == 0,
        })

    return {
        "piscina_m": session.get("pool_length"),
        "efeito_aerobico": session.get("total_training_effect"),
        "efeito_anaerobico": session.get("total_anaerobic_training_effect"),
        "treino": (workout.get("wkt_name") or "").strip() or None,
        "piscinas": lengths,
        "series": laps,
    }
