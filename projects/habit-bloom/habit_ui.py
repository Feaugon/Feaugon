"""Interface do Habit Bloom 2, sem dependências externas."""
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from habits import CATEGORIES, rewards, streak, week_count

BG, WHITE, INK, MUTED = "#f3f5ef", "#ffffff", "#223c32", "#6d7c72"
GREEN, PALE, LINE, GOLD = "#377b5b", "#e3eedf", "#e1e7dc", "#e8bd65"
COLORS = {"Bem-estar": "#e7deef", "Saúde": "#dbeedc", "Estudo": "#dfe9f4", "Trabalho": "#f7e8ce", "Pessoal": "#f3dddd"}


def label(parent, text, size=11, color=INK, bg=None, bold=False, **kw):
    return tk.Label(parent, text=text, font=("Segoe UI", size, "bold" if bold else "normal"), fg=color, bg=bg or parent.cget("bg"), **kw)


def button(parent, text, command, primary=False, **kw):
    return tk.Button(parent, text=text, command=command, font=("Segoe UI", 10, "bold"), bg=GREEN if primary else PALE,
                     fg=WHITE if primary else INK, activebackground="#bcd7b4", activeforeground=INK, relief="flat", bd=0,
                     cursor="hand2", padx=16, pady=10, **kw)


class App:
    def __init__(self, root, store):
        self.root, self.store = root, store
        self.current_day = date.today()
        self.page, self.query = "Hoje", ""
        root.title("Habit Bloom 2 · Seu jardim de hábitos")
        root.geometry("1120x790")
        root.minsize(940, 650)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Bloom.Horizontal.TProgressbar", background=GREEN, troughcolor=PALE, borderwidth=0, lightcolor=GREEN, darkcolor=GREEN)
        style.configure("TCombobox", padding=7, fieldbackground=WHITE)
        sidebar = tk.Frame(root, bg=INK, width=204)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        mark = tk.Canvas(sidebar, width=80, height=77, bg=INK, highlightthickness=0)
        mark.pack(anchor="w", padx=25, pady=(26, 5))
        mark.create_line(38, 62, 38, 27, fill="#bddbb3", width=3)
        mark.create_oval(10, 20, 39, 41, fill="#bddbb3", outline="")
        mark.create_oval(38, 6, 67, 30, fill=GOLD, outline="")
        label(sidebar, "habit bloom", 19, WHITE, bold=True).pack(anchor="w", padx=25)
        label(sidebar, "CULTIVE SEU RITMO", 8, "#bdd2c5").pack(anchor="w", padx=26, pady=(4, 32))
        self.nav = {}
        for title in ("Hoje", "Progresso", "Conquistas", "Arquivados"):
            b = tk.Button(sidebar, text=title, anchor="w", command=lambda t=title: self.navigate(t), font=("Segoe UI", 11),
                          relief="flat", bg=INK, fg="#dae5dc", activebackground=GREEN, activeforeground=WHITE, padx=20, pady=13, cursor="hand2")
            b.pack(fill="x", padx=13, pady=3)
            self.nav[title] = b
        label(sidebar, "FEAUGON / VERSÃO 2.0", 8, "#b0c4b7").pack(side="bottom", pady=23)
        button(sidebar, "Exportar histórico", self.export).pack(side="bottom", fill="x", padx=18, pady=8)
        self.level = label(sidebar, "", 11, "#e8bd65", justify="left")
        self.level.pack(side="bottom", anchor="w", padx=25, pady=16)
        self.main = tk.Frame(root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        header = tk.Frame(self.main, bg=BG)
        header.pack(fill="x", padx=32, pady=(26, 12))
        self.heading = label(header, "Seu dia, com intenção.", 25, bold=True)
        self.heading.pack(side="left")
        button(header, "+ Novo hábito", self.editor, True).pack(side="right")
        self.subtitle = label(self.main, "", 11, MUTED, anchor="w")
        self.subtitle.pack(fill="x", padx=34, pady=(0, 14))
        self.notice = label(self.main, "", 10, GREEN, anchor="w")
        self.notice.pack(fill="x", padx=34)
        holder = tk.Frame(self.main, bg=BG)
        holder.pack(fill="both", expand=True, padx=(28, 16), pady=10)
        self.canvas = tk.Canvas(holder, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(holder, command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.body = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window(0, 0, anchor="nw", window=self.body)
        self.body.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        root.bind("<MouseWheel>", self.scroll)
        root.bind("<Control-n>", lambda _: self.editor())
        self.render()
        self.watch_date()

    def scroll(self, event):
        if event.widget.winfo_toplevel() == self.root and self.body.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-int(event.delta / 120), "units")

    def navigate(self, page):
        self.page, self.query = page, ""
        self.notice.config(text="")
        self.render()
        self.canvas.yview_moveto(0)

    def panel(self, parent=None):
        p = tk.Frame(parent or self.body, bg=WHITE, padx=20, pady=17, highlightbackground=LINE, highlightthickness=1)
        p.pack(fill="x", padx=4, pady=(0, 14))
        return p

    def render(self):
        for child in self.body.winfo_children():
            child.destroy()
        data = rewards(self.store.habits)
        self.level.config(text=f"NÍVEL {data['level']}\n{data['xp']} XP cultivados")
        for title, b in self.nav.items():
            b.config(bg=GREEN if self.page == title else INK)
        titles = {"Hoje": "Seu dia, com intenção.", "Progresso": "Veja o quanto já cresceu.", "Conquistas": "Pequenos passos, conquistas.", "Arquivados": "Uma pausa também faz parte."}
        self.heading.config(text=titles[self.page])
        self.subtitle.config(text=f"{date.today():%d/%m/%Y}  ·  Seu progresso fica neste computador.")
        if self.page == "Hoje":
            self.today()
        elif self.page == "Progresso":
            self.progress(data)
        elif self.page == "Conquistas":
            self.achievements(data)
        else:
            self.cards([h for h in self.store.habits if h["archived"]])

    def today(self):
        habits = [h for h in self.store.habits if not h["archived"]]
        done = sum(date.today().isoformat() in h["days"] for h in habits)
        hero = self.panel()
        text = tk.Frame(hero, bg=WHITE)
        text.pack(side="left", fill="both", expand=True)
        label(text, "UM POUCO MELHOR, A CADA DIA", 9, GREEN, bold=True).pack(anchor="w")
        label(text, f"{done} de {len(habits)} hábitos concluídos", 20, bold=True).pack(anchor="w", pady=(9, 5))
        label(text, "Você não precisa fazer tudo. Comece pelo próximo passo.", 10, MUTED).pack(anchor="w")
        ring = tk.Canvas(hero, width=106, height=106, bg=WHITE, highlightthickness=0)
        ring.pack(side="right", padx=8)
        ring.create_oval(10, 10, 96, 96, outline=PALE, width=8)
        ratio = done / len(habits) if habits else 0
        ring.create_arc(10, 10, 96, 96, start=90, extent=-359.9*ratio, style="arc", outline=GREEN, width=8)
        ring.create_text(53, 53, text=f"{round(ratio*100)}%", fill=INK, font=("Segoe UI", 21, "bold"))
        bar = tk.Frame(self.body, bg=BG)
        bar.pack(fill="x", padx=5, pady=(4, 14))
        label(bar, "SUA ROTINA", 10, MUTED, bold=True).pack(side="left")
        search = tk.Entry(bar, relief="flat", bg=WHITE, fg=INK, font=("Segoe UI", 11), width=22)
        search.pack(side="right", ipady=7)
        search.insert(0, self.query)
        search.bind("<Return>", lambda _: self.search(search.get()))
        button(bar, "Buscar", lambda: self.search(search.get())).pack(side="right", padx=6)
        self.cards([h for h in habits if self.query.casefold() in (h["name"] + h["category"]).casefold()])

    def search(self, query):
        self.query = query.strip()
        self.render()

    def cards(self, habits):
        if not habits:
            p = self.panel()
            label(p, "Espaço para um novo começo.", 19, bold=True).pack(anchor="w", pady=8)
            label(p, "Crie um hábito ou experimente outra busca.", 11, MUTED).pack(anchor="w")
        for h in habits:
            p = self.panel()
            top = tk.Frame(p, bg=WHITE)
            top.pack(fill="x")
            label(top, "  " + h["category"] + "  ", 9, INK, COLORS[h["category"]]).pack(side="left")
            label(top, f"Meta: {h['goal']} dias / semana", 9, MUTED).pack(side="right")
            row = tk.Frame(p, bg=WHITE)
            row.pack(fill="x", pady=(10, 4))
            label(row, h["name"], 16, bold=True, wraplength=410, justify="left").pack(side="left", anchor="w")
            checked = date.today().isoformat() in h["days"]
            if h["archived"]:
                button(row, "Restaurar", lambda key=h["id"]: self.archive(key, False)).pack(side="right")
            else:
                button(row, "Concluído ✓" if checked else "Concluir  +10 XP", lambda key=h["id"]: self.toggle(key), not checked).pack(side="right")
            if h["note"]:
                label(p, h["note"], 10, MUTED, wraplength=630, justify="left").pack(anchor="w", pady=4)
            count = week_count(h)
            label(p, f"{count}/{h['goal']} nesta semana  ·  {streak(h['days'])} dias consecutivos", 10, GREEN).pack(anchor="w", pady=(7, 5))
            ttk.Progressbar(p, style="Bloom.Horizontal.TProgressbar", maximum=h["goal"], value=min(count, h["goal"])).pack(fill="x", pady=(0, 8))
            bottom = tk.Frame(p, bg=WHITE)
            bottom.pack(fill="x")
            for offset in range(6, -1, -1):
                day = date.today() - timedelta(days=offset)
                label(bottom, f"{day.day:02}", 9, WHITE if day.isoformat() in h["days"] else MUTED,
                      GREEN if day.isoformat() in h["days"] else BG, width=3, pady=4).pack(side="left", padx=(0, 4))
            button(bottom, "Histórico", lambda key=h["id"]: self.history(key)).pack(side="right", padx=4)
            button(bottom, "Editar", lambda key=h["id"]: self.editor(key)).pack(side="right")

    def toggle(self, identifier, day=None):
        before = rewards(self.store.habits)
        try:
            self.store.toggle(identifier, day)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self.root)
            return
        after = rewards(self.store.habits)
        unlocked = [b[0] for b, old in zip(after["badges"], before["badges"]) if b[2] and not old[2]]
        self.notice.config(text=("Conquista: " + ", ".join(unlocked)) if unlocked else ("+10 XP · Mais um passo no seu ritmo." if after["xp"] > before["xp"] else "Registro removido. Seu progresso foi recalculado."))
        self.render()

    def progress(self, data):
        p = self.panel()
        label(p, "SEU CULTIVO ATÉ AQUI", 9, GREEN, bold=True).pack(anchor="w")
        label(p, f"{data['total']} conclusões   /   {data['best']} dias de recorde", 22, bold=True).pack(anchor="w", pady=12)
        label(p, "O recorde considera a melhor sequência de um hábito.", 10, MUTED).pack(anchor="w")
        p = self.panel()
        label(p, "Últimos 28 dias", 17, bold=True).pack(anchor="w", pady=(0, 14))
        grid = tk.Frame(p, bg=WHITE)
        grid.pack(fill="x")
        for i in range(28):
            day = date.today() - timedelta(days=27-i)
            count = sum(day.isoformat() in h["days"] for h in self.store.habits)
            cell = tk.Frame(grid, bg=GREEN if count else BG, padx=10, pady=8)
            cell.grid(row=i//7, column=i%7, sticky="nsew", padx=3, pady=3)
            grid.columnconfigure(i%7, weight=1)
            label(cell, f"{day:%d/%m}", 9, WHITE if count else MUTED).pack()
            label(cell, str(count), 15, WHITE if count else MUTED, bold=True).pack()
        label(p, "Cada número representa hábitos concluídos naquele dia.", 10, MUTED).pack(anchor="w", pady=(12, 0))

    def achievements(self, data):
        p = self.panel()
        label(p, f"Nível {data['level']} · {data['xp']} XP", 24, bold=True).pack(anchor="w")
        label(p, f"Faltam {100-data['progress']} XP para o próximo nível.", 11, MUTED).pack(anchor="w", pady=8)
        ttk.Progressbar(p, style="Bloom.Horizontal.TProgressbar", maximum=100, value=data["progress"]).pack(fill="x", pady=5)
        label(p, "Cada conclusão vale 10 XP. Desmarcar recalcula pontos e conquistas.\nOs hábitos arquivados mantêm seu progresso. As recompensas são simbólicas.", 10, MUTED, justify="left").pack(anchor="w", pady=10)
        for title, desc, unlocked in data["badges"]:
            p = self.panel()
            label(p, "DESBLOQUEADA" if unlocked else "EM CULTIVO", 9, GREEN if unlocked else MUTED, bold=True).pack(anchor="w")
            label(p, ("✦  " if unlocked else "○  ") + title, 18, INK if unlocked else MUTED, bold=True).pack(anchor="w", pady=5)
            label(p, desc, 11, MUTED).pack(anchor="w")

    def editor(self, identifier=None):
        h = self.store.get(identifier) if identifier else {"name": "", "category": "Pessoal", "goal": 7, "note": ""}
        win = tk.Toplevel(self.root)
        win.title("Editar hábito" if identifier else "Um novo começo")
        win.configure(bg=BG)
        win.geometry("520x560")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        frame = tk.Frame(win, bg=BG, padx=28, pady=25)
        frame.pack(fill="both", expand=True)
        label(frame, "Cultive uma nova rotina." if not identifier else "Sua rotina evolui com você.", 21, bold=True).pack(anchor="w", pady=(0, 18))
        label(frame, "Nome do hábito", 10, MUTED).pack(anchor="w")
        name = tk.Entry(frame, font=("Segoe UI", 13), relief="flat", bg=WHITE)
        name.pack(fill="x", ipady=10, pady=(5, 14))
        name.insert(0, h["name"])
        label(frame, "Categoria", 10, MUTED).pack(anchor="w")
        category = ttk.Combobox(frame, values=CATEGORIES, state="readonly", font=("Segoe UI", 11))
        category.set(h["category"])
        category.pack(fill="x", pady=(5, 14))
        label(frame, "Meta semanal · dias por semana (1–7)", 10, MUTED).pack(anchor="w")
        goal = ttk.Combobox(frame, values=list(range(1, 8)), state="readonly", font=("Segoe UI", 11))
        goal.set(h["goal"])
        goal.pack(fill="x", pady=(5, 14))
        label(frame, "Sua motivação · opcional, até 240 caracteres", 10, MUTED).pack(anchor="w")
        note = tk.Text(frame, height=3, font=("Segoe UI", 11), relief="flat", bg=WHITE, wrap="word")
        note.pack(fill="x", pady=(5, 16))
        note.insert("1.0", h["note"])
        def save():
            try:
                values = (name.get(), category.get(), int(goal.get()), note.get("1.0", "end-1c"))
                if identifier:
                    self.store.edit(identifier, *values)
                else:
                    self.store.add(*values)
            except (ValueError, OSError) as exc:
                messagebox.showerror("Confira o hábito", str(exc), parent=win)
                return
            win.destroy()
            self.render()
        button(frame, "Salvar hábito", save, True).pack(side="right")
        if identifier and not h["archived"]:
            button(frame, "Arquivar", lambda: (self.archive(identifier), win.destroy())).pack(side="left")
        name.focus_set()
        win.bind("<Escape>", lambda _: win.destroy())

    def archive(self, identifier, archived=True):
        try:
            self.store.archive(identifier, archived)
        except OSError as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self.root)
            return
        self.notice.config(text="Hábito arquivado. Você pode restaurá-lo em Arquivados." if archived else "Hábito restaurado.")
        self.render()

    def history(self, identifier):
        win = tk.Toplevel(self.root)
        win.title("Histórico · " + self.store.get(identifier)["name"])
        win.configure(bg=BG)
        win.geometry("560x380")
        win.transient(self.root)
        label(win, "Seu mês em pequenos passos", 20, bold=True).pack(pady=(22, 8))
        label(win, "Clique em uma data para corrigir o registro dos últimos 28 dias.", 10, MUTED).pack()
        frame = tk.Frame(win, bg=BG)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        def refresh():
            for child in frame.winfo_children():
                child.destroy()
            h = self.store.get(identifier)
            for i in range(28):
                day = date.today() - timedelta(days=27-i)
                done = day.isoformat() in h["days"]
                def act(d=day):
                    self.toggle(identifier, d)
                    refresh()
                b = button(frame, f"{day:%d/%m}" + (" ✓" if done else ""), act, done)
                b.grid(row=i//7, column=i%7, padx=2, pady=3, sticky="nsew")
                b.config(padx=4)
                frame.columnconfigure(i%7, weight=1)
        refresh()

    def export(self):
        path = filedialog.asksaveasfilename(parent=self.root, title="Exportar histórico", defaultextension=".csv", filetypes=[("Planilha CSV", "*.csv")], initialfile="habit-bloom-historico.csv")
        if path:
            try:
                self.store.export(path)
                self.notice.config(text="Histórico exportado com sucesso.")
            except (OSError, ValueError) as exc:
                messagebox.showerror("Exportação não concluída", str(exc), parent=self.root)

    def watch_date(self):
        if date.today() != self.current_day:
            self.current_day = date.today()
            self.render()
        self.root.after(15000, self.watch_date)
