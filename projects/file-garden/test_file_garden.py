from pathlib import Path
import tempfile
import unittest
from file_garden import apply, plan


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_preview_leaves_everything_unchanged(self):
        source = self.root / "foto.PNG"
        source.write_bytes(b"image")
        moves = plan(self.root)
        self.assertEqual(moves[0][1], self.root / "Imagens" / "foto.PNG")
        self.assertTrue(source.exists())
        self.assertFalse((self.root / "Imagens").exists())

    def test_collision_preserves_both_files(self):
        (self.root / "Documentos").mkdir()
        existing = self.root / "Documentos" / "a.txt"
        existing.write_text("old")
        (self.root / "a.txt").write_text("new")
        result = apply(plan(self.root))
        self.assertEqual(result[0]["status"], "moved")
        self.assertEqual(existing.read_text(), "old")
        self.assertEqual((existing.parent / "a (1).txt").read_text(), "new")
        self.assertFalse((self.root / "a.txt").exists())
        self.assertEqual(plan(self.root), [])

    def test_destination_created_after_preview_is_not_overwritten(self):
        source = self.root / "a.txt"
        source.write_text("new")
        moves = plan(self.root)
        moves[0][1].parent.mkdir()
        moves[0][1].write_text("old")
        self.assertEqual(apply(moves)[0]["status"], "error")
        self.assertEqual(source.read_text(), "new")
        self.assertEqual(moves[0][1].read_text(), "old")

    def test_hidden_and_nested_files_are_ignored(self):
        (self.root / ".env").write_text("hidden")
        (self.root / "folder").mkdir()
        (self.root / "folder" / "a.txt").write_text("nested")
        self.assertEqual(plan(self.root), [])

    def test_invalid_category_path_fails_before_moving(self):
        (self.root / "Imagens").write_text("not a directory")
        (self.root / "photo.png").write_bytes(b"test")
        with self.assertRaises(ValueError):
            plan(self.root)
        self.assertTrue((self.root / "photo.png").exists())


if __name__ == "__main__":
    unittest.main()
