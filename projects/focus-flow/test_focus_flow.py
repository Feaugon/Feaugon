import unittest
from focus_flow import Timer


class TimerTests(unittest.TestCase):
    def test_pause_does_not_consume_time(self):
        timer = Timer(focus=10, rest=3)
        timer.start(100)
        timer.pause(104)
        timer.start(200)
        self.assertFalse(timer.tick(205))
        self.assertEqual(timer.remaining, 1)
        self.assertTrue(timer.tick(206))

    def test_completed_focus_waits_for_user(self):
        timer = Timer(focus=10, rest=3)
        timer.start(0)
        self.assertTrue(timer.tick(100))
        self.assertEqual((timer.phase, timer.completed, timer.remaining), ("Pausa", 1, 3))
        self.assertIsNone(timer.deadline)
        self.assertFalse(timer.tick(200))
        timer.start(201)
        self.assertTrue(timer.tick(204))
        self.assertEqual((timer.phase, timer.completed), ("Foco", 1))

    def test_reset_preserves_count(self):
        timer = Timer(focus=10, rest=3)
        timer.start(0)
        timer.tick(10)
        timer.start(11)
        timer.tick(12)
        timer.reset()
        self.assertEqual(timer.remaining, 3)
        self.assertEqual(timer.completed, 1)
        self.assertIsNone(timer.deadline)

    def test_duplicate_start_does_not_extend_session(self):
        timer = Timer(focus=10)
        timer.start(1)
        timer.start(5)
        self.assertTrue(timer.tick(11))

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            Timer(focus=0)


if __name__ == "__main__":
    unittest.main()
