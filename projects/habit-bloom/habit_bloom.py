"""Habit Bloom — app desktop de hábitos, com dados locais."""
import argparse
from datetime import date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from habits import Store, streak

BG, PANEL, TEXT, MUTED, ACCENT = "#101827", "#1b2940", "#f4f7ff", "#aab6ce", "#c0a1ff"


class App:
    def __init__(self, root, store):
        self.root, self.store = root, store
        self.current_day = date.today()
        root.title("Habit Bloom · Feaugon")
        root.geometry("640x660")
        root.minsize(550, 480)
        root.configure(bg=BG)
        tk.Label(root, text="FEAUGON / LAB 03", font=("Segoe UI", 11), fg=ACCENT, bg=BG).pack(pady=(25, 12))
        tk.Label(root, text="Pequenos passos. Todos os dias.", font=("Segoe UI", 22, "bold"), fg=TEXT, bg=BG).pack()
        self.summary = tk.Label(root, font=("Segoe UI", 11), fg=MUTED, bg=BG)
        self.summary.pack(pady=12)
        form = tk.Frame(root, bg=BG)
        form.pack(fill="x", padx=24, pady=12)
        self.entry = tk.Entry(form, font=("Segoe UI", 13), bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.entry.bind("<Return>", lambda _: self.add())
        tk.Button(form, text="+ Hábito", command=self.add, font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg=BG, relief="flat", padx=14, pady=9).pack(side="right", padx=(10, 0))
        tk.Label(root, text="Digite um hábito acima. Ex.: ler 10 páginas", fg=MUTED, bg=BG, font=("Segoe UI", 10)).pack(anchor="w", padx=24)
        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True, padx=24, pady=20)
        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.cards = tk.Frame(self.canvas, bg=BG)
        self.card_window = self.canvas.create_window((0, 0), window=self.cards, anchor="nw")
        self.cards.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfig(self.card_window, width=event.width))
        tk.Label(root, text="Seu progresso fica neste computador. Sem conta, sem nuvem.", fg=MUTED, bg=BG, font=("Segoe UI", 10)).pack(pady=(0, 18))
        self.render()
        self.watch_date()

    def add(self):
        try:
            self.store.add(self.entry.get())
        except (ValueError, OSError) as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self.root)
            return
        self.entry.delete(0, "end")
        self.render()

    def toggle(self, identifier):
        try:
            self.store.toggle(identifier)
        except OSError as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self.root)
        self.render()

    def render(self):
        for child in self.cards.winfo_children():
            child.destroy()
        today = date.today()
        done = sum(today.isoformat() in h["days"] for h in self.store.habits)
        self.summary.config(text=f"{today:%d/%m/%Y}   /   {done} de {len(self.store.habits)} hábitos feitos hoje")
        if not self.store.habits:
            tk.Label(self.cards, text="Sua próxima rotina começa aqui.\nAdicione o primeiro hábito.", font=("Segoe UI", 14), fg=MUTED, bg=BG, pady=50).pack()
        for habit in self.store.habits:
            card = tk.Frame(self.cards, bg=PANEL, padx=16, pady=14)
            card.pack(fill="x", pady=(0, 12))
            checked = today.isoformat() in habit["days"]
            tk.Button(card, text="Feito hoje ✓" if checked else "Marcar hoje", command=lambda key=habit["id"]: self.toggle(key),
                      bg=ACCENT if checked else "#30425e", fg=BG if checked else TEXT, relief="flat", padx=10, pady=7).pack(side="right", padx=(8, 0))
            tk.Label(card, text=habit["name"], font=("Segoe UI", 13, "bold"), wraplength=285, justify="left", fg=TEXT, bg=PANEL).pack(anchor="w")
            tk.Label(card, text=f"{streak(habit['days'], today)} dias em sequência", font=("Segoe UI", 10), fg=ACCENT, bg=PANEL).pack(anchor="w", pady=(3, 8))
            week = tk.Frame(card, bg=PANEL)
            week.pack(anchor="w")
            for offset in range(6, -1, -1):
                day = today - timedelta(days=offset)
                tk.Label(week, text=f"{day.day:02}", width=3, font=("Segoe UI", 9),
                         bg=ACCENT if day.isoformat() in habit["days"] else "#30425e",
                         fg=BG if day.isoformat() in habit["days"] else MUTED).pack(side="left", padx=(0, 4))

    def watch_date(self):
        if date.today() != self.current_day:
            self.current_day = date.today()
            self.render()
        self.root.after(15000, self.watch_date)


def main():
    parser = argparse.ArgumentParser(description="Habit Bloom · hábitos com armazenamento local")
    parser.add_argument("--data", type=Path, default=Path.home() / ".habit-bloom" / "habits.json")
    args = parser.parse_args()
    try:
        store = Store(args.data)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Dados não carregados; arquivo original preservado: {exc}\n")
    root = tk.Tk()
    App(root, store)
    root.mainloop()


if __name__ == "__main__":
    main()
