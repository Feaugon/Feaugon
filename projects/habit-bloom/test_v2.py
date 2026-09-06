from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from habits import Store, rewards, week_count


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "habits.json"
        self.store = Store(self.path)

    def test_v1_migration_preserves_history_and_backup(self):
        old = {"version": 1, "habits": [{"id": "old", "name": "Ler", "days": ["2026-01-01"]}]}
        self.path.write_text(json.dumps(old), encoding="utf-8")
        store = Store(self.path)
        self.assertEqual(store.habits[0]["goal"], 7)
        store.edit("old", "Ler mais", "Estudo", 3, "Aprender")
        self.assertEqual(store.habits[0]["days"], ["2026-01-01"])
        self.assertEqual(json.loads(self.path.with_name("habits.json.v1-backup.json").read_text()), old)
        self.assertEqual(Store(self.path).habits[0]["name"], "Ler mais")

    def test_xp_cannot_be_farmed_and_archive_preserves_rewards(self):
        habit = self.store.add("Ler")
        self.store.toggle(habit["id"])
        self.assertEqual(rewards(self.store.habits)["xp"], 10)
        self.store.toggle(habit["id"])
        self.assertEqual(rewards(self.store.habits)["xp"], 0)
        self.store.toggle(habit["id"])
        self.store.archive(habit["id"])
        self.assertEqual(rewards(self.store.habits)["xp"], 10)
        self.store.archive(habit["id"], False)
        self.assertFalse(Store(self.path).habits[0]["archived"])

    def test_levels_badges_and_best_streak(self):
        habit = self.store.add("Ler")
        habit["days"] = [(date.today()-timedelta(days=i)).isoformat() for i in range(10)]
        result = rewards(self.store.habits)
        self.assertEqual(result["level"], 2)
        self.assertEqual(result["best"], 10)
        self.assertTrue(result["badges"][2][2])
        self.assertFalse(result["badges"][3][2])

    def test_week_starts_monday(self):
        self.assertEqual(week_count({"days": ["2026-09-06", "2026-09-07", "2026-09-08"]}, date(2026, 9, 8)), 2)

    def test_future_day_rejected(self):
        habit = self.store.add("Ler")
        with self.assertRaises(ValueError):
            self.store.toggle(habit["id"], date.today() + timedelta(days=1))

    def test_edit_failure_restores_old_values(self):
        habit = self.store.add("Ler")
        with patch.object(self.store, "save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.store.edit(habit["id"], "Estudar", "Estudo", 4, "")
        self.assertEqual(habit["name"], "Ler")

    def test_csv_and_data_file_protection(self):
        self.store.add("=1+1")
        out = Path(self.tmp.name) / "history.csv"
        self.store.export(out)
        self.assertIn("'=1+1", out.read_text(encoding="utf-8-sig"))
        with self.assertRaises(ValueError):
            self.store.export(self.path)

    def test_invalid_goal_category_notes(self):
        for values in [("Ler", "Inventada", 7, ""), ("Ler", "Pessoal", 0, ""), ("Ler", "Pessoal", 7, "a"*241)]:
            with self.assertRaises(ValueError):
                self.store.add(*values)


if __name__ == "__main__":
    unittest.main()
