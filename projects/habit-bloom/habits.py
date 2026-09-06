"""Modelo e persistência local do Habit Bloom."""
from datetime import date, timedelta
import json
import os
from pathlib import Path
import tempfile
import uuid


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
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("habits"), list):
                raise ValueError("Formato de dados não reconhecido.")
            ids = set()
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
            self.habits = data["habits"]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".habit-bloom-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump({"version": 1, "habits": self.habits}, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def add(self, name):
        name = name.strip()
        if not name or len(name) > 60:
            raise ValueError("Use um nome de 1 a 60 caracteres.")
        if any(h["name"].casefold() == name.casefold() for h in self.habits):
            raise ValueError("Esse hábito já existe.")
        habit = {"id": uuid.uuid4().hex, "name": name, "days": []}
        self.habits.append(habit)
        try:
            self.save()
        except OSError:
            self.habits.pop()
            raise
        return habit

    def toggle(self, identifier, today=None):
        day = (today or date.today()).isoformat()
        habit = next(h for h in self.habits if h["id"] == identifier)
        previous = habit["days"][:]
        habit["days"] = sorted(set(previous) ^ {day})
        try:
            self.save()
        except OSError:
            habit["days"] = previous
            raise
