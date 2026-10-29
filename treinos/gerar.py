"""Gera arquivos .FIT de treino de natação a partir das definições em treinos/*.json.

Uso: python treinos/gerar.py   (grava em treinos/fit/)
Para levar ao relógio: conecte por USB e copie o .fit para GARMIN/NewFiles.
"""
import datetime
import json
import pathlib

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.workout_message import WorkoutMessage
from fit_tool.profile.messages.workout_step_message import WorkoutStepMessage
from fit_tool.profile.profile_type import (
    DisplayMeasure, FileType, Intensity, Manufacturer, Sport, SubSport, SwimStroke,
    WorkoutEquipment, WorkoutStepDuration, WorkoutStepTarget,
)

DIR = pathlib.Path(__file__).resolve().parent
NADO = {"crawl": SwimStroke.FREESTYLE, "costas": SwimStroke.BACKSTROKE, "peito": SwimStroke.BREASTSTROKE,
        "borboleta": SwimStroke.BUTTERFLY, "educativo": SwimStroke.DRILL, "medley": SwimStroke.IM}
EQUIP = {"nadadeira": WorkoutEquipment.SWIM_FINS, "prancha": WorkoutEquipment.SWIM_KICKBOARD,
         "palmar": WorkoutEquipment.SWIM_PADDLES, "pullbuoy": WorkoutEquipment.SWIM_PULL_BUOY,
         "snorkel": WorkoutEquipment.SWIM_SNORKEL}
TIPO = {"aquecimento": Intensity.WARMUP, "principal": Intensity.ACTIVE, "desaquecimento": Intensity.COOLDOWN}


def nado(b):
    s = WorkoutStepMessage()
    s.intensity = TIPO[b.get("tipo", "principal")]
    s.duration_type = WorkoutStepDuration.DISTANCE
    s.duration_distance = float(b["m"])
    if b.get("nado", "livre") in NADO:
        s.target_type = WorkoutStepTarget.SWIM_STROKE
        s.target_stroke_type = NADO[b["nado"]]
    else:
        s.target_type = WorkoutStepTarget.OPEN
    if b.get("equip"):
        s.equipment = EQUIP[b["equip"]]
    if b.get("nota"):
        s.notes = b["nota"]
    return s


def descanso(segundos):
    s = WorkoutStepMessage()
    s.intensity = Intensity.REST
    s.target_type = WorkoutStepTarget.OPEN
    if segundos:
        s.duration_type = WorkoutStepDuration.TIME
        s.duration_time = float(segundos)
    else:  # descanso até apertar o botão de volta
        s.duration_type = WorkoutStepDuration.OPEN
    return s


def passos(blocos):
    out = []
    for b in blocos:
        if "m" not in b:
            out.append(descanso(b.get("descanso_s")))
            continue
        inicio = len(out)
        out.append(nado(b))
        if b.get("descanso_s") is not None or b.get("repetir", 1) > 1:
            out.append(descanso(b.get("descanso_s", 0)))
        if b.get("repetir", 1) > 1:
            r = WorkoutStepMessage()
            r.duration_type = WorkoutStepDuration.REPEAT_UNTIL_STEPS_CMPLT
            r.duration_step = inicio
            r.target_repeat_steps = b["repetir"]
            out.append(r)
    for i, s in enumerate(out):
        s.message_index = i
    return out


def gerar(defin):
    fid = FileIdMessage()
    fid.type = FileType.WORKOUT
    fid.manufacturer = Manufacturer.DEVELOPMENT.value
    fid.product = 0
    fid.serial_number = 0x4E415441
    fid.time_created = round(datetime.datetime.now().timestamp() * 1000)

    steps = passos(defin["blocos"])
    w = WorkoutMessage()
    w.workout_name = defin["nome"]
    w.sport = Sport.SWIMMING
    w.sub_sport = SubSport.LAP_SWIMMING
    w.pool_length = float(defin.get("piscina_m", 25))
    w.pool_length_unit = DisplayMeasure.METRIC
    w.num_valid_steps = len(steps)

    b = FitFileBuilder(auto_define=True, min_string_size=50)
    b.add(fid)
    b.add(w)
    b.add_all(steps)
    return b.build()


def total_m(blocos):
    return sum(b.get("m", 0) * b.get("repetir", 1) for b in blocos)


def main():
    (DIR / "fit").mkdir(exist_ok=True)
    for f in sorted(DIR.glob("*.json")):
        defin = json.loads(f.read_text())
        gerar(defin).to_file(str(DIR / "fit" / f"{f.stem}.fit"))
        print(f"{f.stem}.fit  {defin['nome']}  {total_m(defin['blocos'])} m")


if __name__ == "__main__":
    main()
