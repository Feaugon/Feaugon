"""Focus Flow — Pomodoro desktop, somente biblioteca padrão."""
from dataclasses import dataclass
import math
import time
import tkinter as tk


@dataclass
class Timer:
    focus: int = 25 * 60
    rest: int = 5 * 60
    phase: str = "Foco"
    completed: int = 0
    remaining: float = 0
    deadline: float | None = None

    def __post_init__(self):
        if self.focus <= 0 or self.rest <= 0:
            raise ValueError("As durações devem ser positivas.")
        self.remaining = float(self.focus)

    def start(self, now):
        if self.deadline is None:
            self.deadline = now + self.remaining

    def tick(self, now):
        if self.deadline is None:
            return False
        self.remaining = max(0.0, self.deadline - now)
        if self.remaining > 0:
            return False
        self.deadline = None
        if self.phase == "Foco":
            self.completed += 1
            self.phase = "Pausa"
            self.remaining = float(self.rest)
        else:
            self.phase = "Foco"
            self.remaining = float(self.focus)
        return True

    def pause(self, now):
        self.tick(now)
        self.deadline = None

    def reset(self):
        self.deadline = None
        self.remaining = float(self.focus if self.phase == "Foco" else self.rest)


class App:
    def __init__(self, root):
        self.root, self.timer = root, Timer()
        root.title("Focus Flow · Feaugon")
        root.geometry("520x610")
        root.minsize(440, 570)
        root.configure(bg="#101827")
        self.label("FEAUGON / LAB 01", 11, "#63dec3").pack(pady=(30, 16))
        self.label("Uma coisa de cada vez.", 22).pack()
        self.label("Um espaço para cuidar da sua atenção.", 11, "#aab6ce").pack(pady=8)
        self.canvas = tk.Canvas(root, width=260, height=260, bg="#101827", highlightthickness=0)
        self.canvas.pack(pady=12)
        self.canvas.create_oval(15, 15, 245, 245, outline="#25334a", width=9)
        self.arc = self.canvas.create_arc(15, 15, 245, 245, start=90, extent=0,
                                          style="arc", outline="#63dec3", width=9)
        self.clock = self.canvas.create_text(130, 119, text="25:00", fill="#f4f7ff", font=("Segoe UI", 44, "bold"))
        self.phase = self.canvas.create_text(130, 167, text="FOCO", fill="#63dec3", font=("Segoe UI", 12))
        controls = tk.Frame(root, bg="#101827")
        controls.pack()
        self.play = tk.Button(controls, text="Começar", command=self.toggle, bg="#63dec3", fg="#101827",
                              font=("Segoe UI", 12, "bold"), width=13, relief="flat", pady=10)
        self.play.pack(side="left", padx=5)
        tk.Button(controls, text="Reiniciar", command=self.reset, bg="#25334a", fg="white",
                  font=("Segoe UI", 12), width=12, relief="flat", pady=10).pack(side="left", padx=5)
        self.status = self.label("Pronto para começar.", 11, "#aab6ce")
        self.status.pack(pady=17)
        self.counter = self.label("0 sessões concluídas", 11, "#aab6ce")
        self.counter.pack()
        self.label("25 min de foco  /  5 min de pausa", 10, "#aab6ce").pack(pady=16)
        root.bind("<space>", lambda _: self.toggle())
        self.refresh()

    def label(self, text, size, color="#f4f7ff"):
        return tk.Label(self.root, text=text, bg="#101827", fg=color, font=("Segoe UI", size))

    def toggle(self):
        if self.timer.deadline is None:
            self.timer.start(time.monotonic())
            self.status.config(text="No seu ritmo. Você está no controle.")
        else:
            self.timer.pause(time.monotonic())
            self.status.config(text="Pausado. Retome quando quiser.")
        self.paint()

    def reset(self):
        self.timer.reset()
        self.status.config(text="Etapa reiniciada.")
        self.paint()

    def paint(self):
        seconds = math.ceil(self.timer.remaining)
        self.canvas.itemconfig(self.clock, text=f"{seconds // 60:02}:{seconds % 60:02}")
        self.canvas.itemconfig(self.phase, text=self.timer.phase.upper())
        total = self.timer.focus if self.timer.phase == "Foco" else self.timer.rest
        self.canvas.itemconfig(self.arc, extent=-359.9 * (1 - self.timer.remaining / total))
        self.play.config(text="Pausar" if self.timer.deadline is not None else "Começar")
        self.counter.config(text=f"{self.timer.completed} sessões concluídas")

    def refresh(self):
        if self.timer.tick(time.monotonic()):
            self.root.bell()
            self.status.config(text=f"Etapa concluída! Comece: {self.timer.phase.lower()}.")
        self.paint()
        self.root.after(150, self.refresh)


if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()
