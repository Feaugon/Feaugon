from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from habits import Store, streak


class HabitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "habits.json"
        self.store = Store(self.path)

    def test_round_trip_and_uncheck(self):
        habit = self.store.add("Ler 10 páginas")
        today = date(2026, 9, 6)
        self.store.toggle(habit["id"], today)
        loaded = Store(self.path)
        self.assertEqual(loaded.habits[0]["days"], ["2026-09-06"])
        loaded.toggle(habit["id"], today)
        self.assertEqual(Store(self.path).habits[0]["days"], [])

    def test_validation(self):
        for invalid in (" ", "x" * 61):
            with self.assertRaises(ValueError):
                self.store.add(invalid)
        self.store.add("Ler")
        with self.assertRaises(ValueError):
            self.store.add(" ler ")

    def test_streak_allows_today_to_be_pending(self):
        days = ["2026-09-03", "2026-09-04", "2026-09-05"]
        self.assertEqual(streak(days, date(2026, 9, 6)), 3)
        self.assertEqual(streak(days + ["2026-09-06"], date(2026, 9, 6)), 4)
        self.assertEqual(streak(days, date(2026, 9, 7)), 0)

    def test_streak_crosses_month_and_leap_year(self):
        self.assertEqual(streak(["2024-02-28", "2024-02-29", "2024-03-01"], date(2024, 3, 1)), 3)

    def test_corrupt_data_is_not_overwritten(self):
        self.path.write_text("broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            Store(self.path)
        self.assertEqual(self.path.read_text(), "broken")

    def test_failed_save_rolls_back_memory(self):
        habit = self.store.add("Ler")
        with patch.object(self.store, "save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.store.toggle(habit["id"])
            self.assertEqual(habit["days"], [])
            with self.assertRaises(OSError):
                self.store.add("Caminhar")
            self.assertEqual(len(self.store.habits), 1)


if __name__ == "__main__":
    unittest.main()
