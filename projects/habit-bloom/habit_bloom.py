"""Habit Bloom 2 — seu jardim de hábitos."""
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from habits import Store
from habit_ui import App


def main():
    parser = argparse.ArgumentParser(description="Habit Bloom 2 · hábitos, metas e conquistas")
    parser.add_argument("--data", type=Path, default=Path.home() / ".habit-bloom" / "habits.json")
    args = parser.parse_args()
    root = tk.Tk()
    root.withdraw()
    try:
        store = Store(args.data)
    except (OSError, ValueError) as exc:
        messagebox.showerror("Não foi possível carregar seus hábitos", f"O arquivo original foi preservado.\n\n{exc}", parent=root)
        root.destroy()
        return
    App(root, store)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
