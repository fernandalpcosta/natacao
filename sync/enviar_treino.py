"""Envia um treino de treinos/*.json para a conta Garmin Connect e agenda no calendário.

O celular passa o treino ao relógio por Bluetooth na próxima sincronização.
Usa a biblioteca não oficial garminconnect, com GARMIN_EMAIL e GARMIN_PASSWORD.

Uso: python sync/enviar_treino.py 2-velocidade [AAAA-MM-DD] [--simular]
"""
import json
import os
import pathlib
import sys

TREINOS = pathlib.Path(__file__).resolve().parent.parent / "treinos"

NADO = {"crawl": "free", "costas": "backstroke", "peito": "breaststroke", "borboleta": "fly",
        "educativo": "drill", "medley": "individual_medley", "livre": "any_stroke"}
EQUIP = {"nadadeira": "fins", "prancha": "kickboard", "palmar": "paddles", "pullbuoy": "pull_buoy", "snorkel": "snorkel"}
PASSO = {"aquecimento": "warmup", "principal": "interval", "desaquecimento": "cooldown"}

# Usados só se a Garmin não devolver a lista de tipos.
RESERVA = {
    "stepType": {"warmup": 1, "cooldown": 2, "interval": 3, "recovery": 4, "rest": 5, "repeat": 6},
    "conditionType": {"lap.button": 1, "time": 2, "distance": 3, "iterations": 7},
    "strokeType": {"any_stroke": 1, "backstroke": 2, "breaststroke": 3, "drill": 4, "fly": 5, "free": 6, "individual_medley": 7},
    "equipmentType": {"fins": 1, "kickboard": 2, "paddles": 3, "pull_buoy": 4, "snorkel": 5},
}


class Tipos:
    """Traduz chaves como 'free' nos objetos com id que a Garmin espera."""

    def __init__(self, resposta=None):
        self.tabela = {k: {} for k in RESERVA}

        def varrer(o):
            if isinstance(o, dict):
                for kind in RESERVA:
                    if f"{kind}Key" in o and f"{kind}Id" in o:
                        self.tabela[kind][o[f"{kind}Key"]] = {f"{kind}Id": o[f"{kind}Id"], f"{kind}Key": o[f"{kind}Key"]}
                for v in o.values():
                    varrer(v)
            elif isinstance(o, list):
                for v in o:
                    varrer(v)

        varrer(resposta or {})

    def __call__(self, kind, key):
        if key in self.tabela[kind]:
            return self.tabela[kind][key]
        return {f"{kind}Id": RESERVA[kind][key], f"{kind}Key": key}


def montar(defin, tipos):
    ordem = [0]

    def prox():
        ordem[0] += 1
        return ordem[0]

    def nado(b):
        s = {"type": "ExecutableStepDTO", "stepOrder": prox(),
             "stepType": tipos("stepType", PASSO[b.get("tipo", "principal")]),
             "endCondition": tipos("conditionType", "distance"), "endConditionValue": float(b["m"]),
             "preferredEndConditionUnit": {"unitKey": "meter"},
             "strokeType": tipos("strokeType", NADO[b.get("nado", "livre")])}
        if b.get("equip"):
            s["equipmentType"] = tipos("equipmentType", EQUIP[b["equip"]])
        if b.get("nota"):
            s["description"] = b["nota"][:512]
        return s

    def descanso(segundos):
        s = {"type": "ExecutableStepDTO", "stepOrder": prox(), "stepType": tipos("stepType", "rest")}
        if segundos:
            s.update(endCondition=tipos("conditionType", "time"), endConditionValue=float(segundos))
        else:
            s["endCondition"] = tipos("conditionType", "lap.button")
        return s

    passos = []
    for b in defin["blocos"]:
        if "m" not in b:
            passos.append(descanso(b.get("descanso_s")))
            continue
        n = b.get("repetir", 1)
        if n > 1:
            grupo = {"type": "RepeatGroupDTO", "stepOrder": prox(), "stepType": tipos("stepType", "repeat"),
                     "numberOfIterations": n, "endCondition": tipos("conditionType", "iterations"),
                     "endConditionValue": float(n), "smartRepeat": False, "skipLastRestStep": False}
            grupo["workoutSteps"] = [nado(b), descanso(b.get("descanso_s", 0))]
            passos.append(grupo)
        else:
            passos.append(nado(b))
            if b.get("descanso_s"):
                passos.append(descanso(b["descanso_s"]))

    esporte = {"sportTypeId": 4, "sportTypeKey": "swimming"}
    return {
        "workoutName": defin["nome"],
        "description": defin.get("objetivo"),
        "sportType": esporte,
        "poolLength": float(defin.get("piscina_m", 25)),
        "poolLengthUnit": {"unitId": 1, "unitKey": "meter", "factor": 100.0},
        "workoutSegments": [{"segmentOrder": 1, "sportType": esporte, "workoutSteps": passos}],
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    simular = "--simular" in sys.argv
    if not args:
        sys.exit(__doc__)
    nome, data = args[0], (args[1] if len(args) > 1 else "")
    defin = json.loads((TREINOS / f"{nome}.json").read_text())

    if simular:
        print(json.dumps(montar(defin, Tipos()), ensure_ascii=False, indent=1))
        return

    from garminconnect import Garmin

    g = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"])
    status, _ = g.login()
    if status == "needs_mfa":
        sys.exit("A conta pede verificação em duas etapas; o envio automático não consegue responder ao código.")

    try:
        tipos = Tipos(g.get_workout_types())
    except Exception as e:
        print(f"aviso: tipos da Garmin indisponíveis ({e}); usando a tabela interna", file=sys.stderr)
        tipos = Tipos()

    # Substitui uma versão anterior do mesmo treino, para não acumular cópias.
    for w in g.get_workouts(0, 200, my_workouts_only=True) or []:
        if w.get("workoutName") == defin["nome"]:
            g.delete_workout(w["workoutId"])
            print(f"versão anterior removida ({w['workoutId']})")

    criado = g.upload_workout(montar(defin, tipos))
    wid = criado["workoutId"]
    print(f"treino criado: https://connect.garmin.com/modern/workout/{wid}")
    if data:
        g.schedule_workout(wid, data)
        print(f"agendado para {data}; o celular envia ao relógio na próxima sincronização")


if __name__ == "__main__":
    main()
