"""Calendário de treinos: a Garmin é a referência, o site mostra docs/data/calendario.json.

Uso:
  python sync/calendario.py exportar
  python sync/calendario.py agendar <treino> <AAAA-MM-DD>
  python sync/calendario.py mover <agendamento_id> <AAAA-MM-DD>
  python sync/calendario.py remover <agendamento_id>

Usa a biblioteca não oficial garminconnect, com GARMIN_EMAIL e GARMIN_PASSWORD.
"""
import datetime
import json
import os
import pathlib
import sys

from enviar_treino import TREINOS, Tipos, montar

SAIDA = pathlib.Path(__file__).resolve().parent.parent / "docs" / "data" / "calendario.json"


def entrar():
    from garminconnect import Garmin

    g = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"])
    status, _ = g.login()
    if status == "needs_mfa":
        sys.exit("::error::A conta pede verificação em duas etapas; o calendário automático não consegue responder ao código.")
    return g


def nossos_treinos():
    """nome do treino na Garmin -> nome do arquivo em treinos/"""
    return {json.loads(f.read_text())["nome"]: f.stem for f in TREINOS.glob("*.json")}


def itens(g, meses=(-1, 0, 1, 2)):
    hoje = datetime.date.today()
    vistos = {}
    for d in meses:
        m0 = hoje.month - 1 + d
        ano, mes = hoje.year + m0 // 12, m0 % 12 + 1
        for it in (g.get_scheduled_workouts(ano, mes) or {}).get("calendarItems") or []:
            if it.get("itemType") == "workout":
                vistos[it.get("id")] = it
    return list(vistos.values())


def exportar(g):
    nomes = nossos_treinos()
    lista = itens(g)
    if lista:
        print("::notice::campos de um item do calendário Garmin: " + ", ".join(sorted(lista[0].keys())))
    saida = []
    for it in lista:
        nome = (it.get("title") or it.get("workoutName") or "").strip()
        saida.append({
            "data": it.get("date"),
            "nome": nome,
            "treino": nomes.get(nome),
            "agendamento_id": it.get("id"),
            "workout_id": it.get("workoutId"),
            "esporte": it.get("sportTypeKey"),
        })
    saida.sort(key=lambda x: (x["data"] or "", x["nome"]))
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1))
    print(f"{len(saida)} treinos agendados exportados")


def treino_na_garmin(g, stem):
    defin = json.loads((TREINOS / f"{stem}.json").read_text())
    for w in g.get_workouts(0, 200, my_workouts_only=True) or []:
        if w.get("workoutName") == defin["nome"]:
            return w["workoutId"]
    try:
        tipos = Tipos(g.get_workout_types())
    except Exception:
        tipos = Tipos()
    return g.upload_workout(montar(defin, tipos))["workoutId"]


def item_por_id(g, agendamento_id):
    for it in itens(g, meses=range(-2, 7)):
        if str(it.get("id")) == str(agendamento_id):
            return it
    sys.exit(f"::error::Agendamento {agendamento_id} não encontrado no calendário da Garmin.")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    acao, args = sys.argv[1], sys.argv[2:]
    g = entrar()
    if acao == "agendar":
        stem, data = args
        g.schedule_workout(treino_na_garmin(g, stem), data)
        print(f"::notice::{stem} agendado para {data}")
    elif acao == "mover":
        agendamento_id, data = args
        it = item_por_id(g, agendamento_id)
        g.schedule_workout(it["workoutId"], data)
        g.unschedule_workout(agendamento_id)
        print(f"::notice::{it.get('title')} movido de {it.get('date')} para {data}")
    elif acao == "remover":
        (agendamento_id,) = args
        it = item_por_id(g, agendamento_id)
        g.unschedule_workout(agendamento_id)
        print(f"::notice::{it.get('title')} removido de {it.get('date')}")
    elif acao != "exportar":
        sys.exit(__doc__)
    exportar(g)


if __name__ == "__main__":
    main()
