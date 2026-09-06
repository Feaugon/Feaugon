"""Modelo e persistência local do Habit Bloom."""
from datetime import date, timedelta
import json
import os
from pathlib import Path
import tempfile
import uuid
import csv
from copy import deepcopy

CATEGORIES = ("Bem-estar", "Saúde", "Estudo", "Trabalho", "Pessoal")


def best_streak(days, today=None):
    previous = None
    best = current = 0
    for day in sorted({date.fromisoformat(d) for d in days if d <= (today or date.today()).isoformat()}):
        current = current + 1 if previous and day == previous + timedelta(days=1) else 1
        best, previous = max(best, current), day
    return best


def week_count(habit, today=None):
    today = today or date.today()
    start = today - timedelta(days=today.weekday())
    return sum(start.isoformat() <= d <= today.isoformat() for d in set(habit["days"]))


def rewards(habits, today=None):
    today = today or date.today()
    total = sum(len({d for d in h["days"] if d <= today.isoformat()}) for h in habits)
    best = max((best_streak(h["days"], today) for h in habits), default=0)
    xp = total * 10
    badges = [
        ("Primeira semente", "Conclua seu primeiro hábito.", total >= 1),
        ("Criando raízes", "Registre 7 conclusões.", total >= 7),
        ("Uma semana florida", "Alcance 7 dias seguidos em um hábito.", best >= 7),
        ("Jardim em expansão", "Registre 30 conclusões.", total >= 30),
        ("Cultivo constante", "Alcance 30 dias seguidos em um hábito.", best >= 30),
        ("Cem pequenos passos", "Registre 100 conclusões.", total >= 100),
    ]
    return {"total": total, "xp": xp, "level": 1 + xp // 100, "progress": xp % 100, "badges": badges, "best": best}


def streak(days, today=None):
    today = today or date.today()
    recorded = set(days)
    cursor = today if today.isoformat() in recorded else today - timedelta(days=1)
    count = 0
    while cursor.isoformat() in recorded:
        count += 1
        cursor -= timedelta(days=1)
    return count


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.habits = []
        self.legacy = False
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") not in (1, 2) or not isinstance(data.get("habits"), list):
                raise ValueError("Formato de dados não reconhecido.")
            ids = set()
            self.legacy = data["version"] == 1
            for habit in data["habits"]:
                if not isinstance(habit, dict):
                    raise ValueError("Hábito inválido.")
                identifier, name, days = habit.get("id"), habit.get("name"), habit.get("days")
                if not isinstance(identifier, str) or identifier in ids or not isinstance(name, str) or not name.strip() or not isinstance(days, list):
                    raise ValueError("Hábito inválido.")
                ids.add(identifier)
                for day in days:
                    if not isinstance(day, str) or date.fromisoformat(day).isoformat() != day:
                        raise ValueError("Data inválida.")
                habit.setdefault("category", "Pessoal")
                habit.setdefault("goal", 7)
                habit.setdefault("note", "")
                habit.setdefault("archived", False)
                if habit["category"] not in CATEGORIES or type(habit["goal"]) is not int or not 1 <= habit["goal"] <= 7 or not isinstance(habit["note"], str) or type(habit["archived"]) is not bool:
                    raise ValueError("Configuração de hábito inválida.")
                habit["days"] = sorted(set(days))
            self.habits = data["habits"]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.legacy and self.path.exists():
            backup = self.path.with_name(self.path.name + ".v1-backup.json")
            if not backup.exists():
                with backup.open("x", encoding="utf-8") as stream:
                    stream.write(self.path.read_text(encoding="utf-8"))
        fd, name = tempfile.mkstemp(prefix=".habit-bloom-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump({"version": 2, "habits": self.habits}, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
            self.legacy = False
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def validate(self, name, category, goal, note, identifier=None):
        name = name.strip()
        if not name or len(name) > 60:
            raise ValueError("Use um nome de 1 a 60 caracteres.")
        if any(h["id"] != identifier and h["name"].casefold() == name.casefold() for h in self.habits):
            raise ValueError("Esse hábito já existe.")
        if category not in CATEGORIES or type(goal) is not int or not 1 <= goal <= 7:
            raise ValueError("Escolha uma categoria e uma meta entre 1 e 7 dias.")
        if len(note) > 240:
            raise ValueError("Use até 240 caracteres na motivação.")
        return name

    def add(self, name, category="Pessoal", goal=7, note=""):
        name = self.validate(name, category, goal, note)
        habit = {"id": uuid.uuid4().hex, "name": name, "days": [], "category": category, "goal": goal, "note": note.strip(), "archived": False}
        self.habits.append(habit)
        try:
            self.save()
        except OSError:
            self.habits.pop()
            raise
        return habit

    def toggle(self, identifier, today=None):
        if (today or date.today()) > date.today():
            raise ValueError("Não é possível registrar dias futuros.")
        day = (today or date.today()).isoformat()
        habit = next(h for h in self.habits if h["id"] == identifier)
        previous = habit["days"][:]
        habit["days"] = sorted(set(previous) ^ {day})
        try:
            self.save()
        except OSError:
            habit["days"] = previous
            raise

    def get(self, identifier):
        return next(h for h in self.habits if h["id"] == identifier)

    def change(self, identifier, **fields):
        habit = self.get(identifier)
        old = deepcopy(habit)
        habit.update(fields)
        try:
            self.save()
        except OSError:
            habit.clear()
            habit.update(old)
            raise

    def edit(self, identifier, name, category, goal, note):
        name = self.validate(name, category, goal, note, identifier)
        self.change(identifier, name=name, category=category, goal=goal, note=note.strip())

    def archive(self, identifier, archived=True):
        self.change(identifier, archived=archived)

    def export(self, path):
        path = Path(path)
        if path.resolve() == self.path.resolve():
            raise ValueError("Escolha outro arquivo para exportar.")
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Hábito", "Categoria", "Meta semanal", "Arquivado", "Data concluída"])
            for h in self.habits:
                name = "'" + h["name"] if h["name"].startswith(("=", "+", "-", "@")) else h["name"]
                for day in h["days"] or [""]:
                    writer.writerow([name, h["category"], h["goal"], h["archived"], day])
