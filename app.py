import random
import tkinter as tk
from tkinter import messagebox


class LottoApp:
    """Application de gestion de loto (1 à 90)."""

    BG_START = "#0f172a"  # bleu nuit
    BG_END = "#1d4ed8"    # bleu électrique
    PANEL = "#111827"
    PANEL_ALT = "#1f2937"
    TEXT = "#f9fafb"
    MUTED = "#cbd5e1"
    ACCENT = "#f59e0b"
    SUCCESS = "#22c55e"
    DANGER = "#ef4444"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Loto 1-90")
        self.root.geometry("1366x820")
        self.root.minsize(1100, 700)

        # État applicatif
        self.drawn_numbers: list[int] = []
        self.current_gain = tk.StringVar(value="Aucun gain annoncé")
        self.animation_running = False

        # Couche fond dégradé
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self._draw_gradient)

        # Conteneur principal
        self.main = tk.Frame(self.root, bg="")
        self.main.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.94)

        self._build_layout()
        self._refresh_recent_labels()
        self._refresh_history()

        self.root.bind("<Return>", self._on_enter)

    # ---------------- UI ---------------- #
    def _build_layout(self) -> None:
        self.main.columnconfigure(0, weight=2)
        self.main.columnconfigure(1, weight=3)
        self.main.rowconfigure(0, weight=1)

        self.left_panel = tk.Frame(self.main, bg=self.PANEL, bd=0, highlightthickness=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.right_panel = tk.Frame(self.main, bg=self.PANEL_ALT, bd=0, highlightthickness=0)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        self.left_panel.columnconfigure(0, weight=1)

        title = tk.Label(
            self.left_panel,
            text="🎱 LOTO FRANÇAIS",
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Segoe UI", 26, "bold"),
        )
        title.pack(pady=(18, 4))

        subtitle = tk.Label(
            self.left_panel,
            text="Gestion complète des tirages 1 à 90",
            fg=self.MUTED,
            bg=self.PANEL,
            font=("Segoe UI", 12),
        )
        subtitle.pack(pady=(0, 18))

        # Bloc derniers numéros
        recent_frame = tk.Frame(self.left_panel, bg=self.PANEL_ALT)
        recent_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.last_label = tk.Label(
            recent_frame,
            text="--",
            fg=self.ACCENT,
            bg=self.PANEL_ALT,
            font=("Segoe UI Black", 120),
        )
        self.last_label.pack(pady=(18, 0))

        self.second_label = tk.Label(
            recent_frame,
            text="--",
            fg=self.TEXT,
            bg=self.PANEL_ALT,
            font=("Segoe UI", 52, "bold"),
        )
        self.second_label.pack(pady=(0, 0))

        self.third_label = tk.Label(
            recent_frame,
            text="--",
            fg=self.MUTED,
            bg=self.PANEL_ALT,
            font=("Segoe UI", 34),
        )
        self.third_label.pack(pady=(0, 16))

        # Saisie manuelle
        manual_frame = tk.Frame(self.left_panel, bg=self.PANEL)
        manual_frame.pack(fill="x", padx=16, pady=(8, 8))

        tk.Label(
            manual_frame,
            text="Ajouter un numéro (1 à 90)",
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            manual_frame,
            textvariable=self.entry_var,
            font=("Segoe UI", 18, "bold"),
            justify="center",
            bd=0,
            relief="flat",
            bg="#e5e7eb",
            fg="#111827",
            insertbackground="#111827",
        )
        self.entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=8)

        self.add_button = self._create_button(
            manual_frame, "Ajouter", self._add_from_entry, self.SUCCESS
        )
        self.add_button.grid(row=1, column=1, sticky="ew")

        manual_frame.columnconfigure(0, weight=1)
        manual_frame.columnconfigure(1, weight=0)

        # Actions
        actions_frame = tk.Frame(self.left_panel, bg=self.PANEL)
        actions_frame.pack(fill="x", padx=16, pady=(6, 10))
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)

        self.random_button = self._create_button(
            actions_frame, "Tirage aléatoire", self.start_random_animation, self.ACCENT
        )
        self.random_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.reset_button = self._create_button(actions_frame, "Reset", self.reset, self.DANGER)
        self.reset_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Gains
        gains_frame = tk.Frame(self.left_panel, bg=self.PANEL)
        gains_frame.pack(fill="x", padx=16, pady=(8, 10))

        tk.Label(
            gains_frame,
            text="Annonce des gains",
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(gains_frame, bg=self.PANEL)
        btn_row.pack(fill="x")

        self.gain_buttons = [
            self._create_button(btn_row, "Quine simple", lambda: self.set_gain("Quine simple"), "#6366f1"),
            self._create_button(btn_row, "Quine double", lambda: self.set_gain("Quine double"), "#8b5cf6"),
            self._create_button(btn_row, "Carton plein", lambda: self.set_gain("Carton plein"), "#ec4899"),
        ]

        for i, button in enumerate(self.gain_buttons):
            button.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="ew")
            btn_row.columnconfigure(i, weight=1)

        self.gain_label = tk.Label(
            gains_frame,
            textvariable=self.current_gain,
            fg=self.ACCENT,
            bg=self.PANEL,
            font=("Segoe UI", 14, "bold"),
        )
        self.gain_label.pack(anchor="w", pady=(10, 0))

        # Historique
        history_wrap = tk.Frame(self.left_panel, bg=self.PANEL)
        history_wrap.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        tk.Label(
            history_wrap,
            text="Historique des numéros tirés",
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.history_text = tk.Text(
            history_wrap,
            height=7,
            wrap="word",
            bg="#0b1220",
            fg=self.TEXT,
            insertbackground=self.TEXT,
            font=("Consolas", 13),
            bd=0,
            padx=10,
            pady=10,
        )
        self.history_text.pack(fill="both", expand=True)
        self.history_text.configure(state="disabled")

    def _build_right_panel(self) -> None:
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        wrap = tk.Frame(self.right_panel, bg=self.PANEL_ALT)
        wrap.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        tk.Label(
            wrap,
            text="Grille complète 1 à 90",
            fg=self.TEXT,
            bg=self.PANEL_ALT,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        grid_container = tk.Frame(wrap, bg=self.PANEL_ALT)
        grid_container.pack(fill="both", expand=True)

        self.cell_labels: dict[int, tk.Label] = {}
        for row in range(9):
            grid_container.rowconfigure(row, weight=1)
        for col in range(10):
            grid_container.columnconfigure(col, weight=1)

        for number in range(1, 91):
            row = (number - 1) // 10
            col = (number - 1) % 10
            lbl = tk.Label(
                grid_container,
                text=f"{number}",
                bg="#111827",
                fg=self.TEXT,
                bd=1,
                relief="solid",
                font=("Segoe UI", 16, "bold"),
                padx=6,
                pady=8,
            )
            lbl.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self.cell_labels[number] = lbl

    def _create_button(self, parent: tk.Widget, text: str, command, color: str) -> tk.Button:
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#111827",
            activebackground=self._shade(color, -0.15),
            activeforeground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
        )

        def on_enter(_event):
            if btn["state"] == "normal":
                btn.configure(bg=self._shade(color, 0.08))

        def on_leave(_event):
            btn.configure(bg=color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ---------------- Logique métier ---------------- #
    def _on_enter(self, _event) -> None:
        if not self.animation_running:
            self._add_from_entry()

    def _add_from_entry(self) -> None:
        raw = self.entry_var.get().strip()
        if not raw:
            return
        if not raw.isdigit():
            messagebox.showwarning("Saisie invalide", "Veuillez saisir un nombre entier entre 1 et 90.")
            return

        number = int(raw)
        self.add_number(number)

    def add_number(self, number: int) -> bool:
        """Ajoute un numéro si valide et non déjà tiré."""
        if number < 1 or number > 90:
            messagebox.showwarning("Hors limite", "Le numéro doit être compris entre 1 et 90.")
            return False
        if number in self.drawn_numbers:
            messagebox.showwarning("Doublon", f"Le numéro {number} a déjà été tiré.")
            return False

        self.drawn_numbers.append(number)
        self.entry_var.set("")
        self._refresh_recent_labels()
        self._refresh_history()
        self._mark_number(number)
        self._pulse_last_number()

        if len(self.drawn_numbers) == 90:
            messagebox.showinfo("Terminé", "Tous les numéros ont été tirés.")

        return True

    def start_random_animation(self) -> None:
        if self.animation_running:
            return

        remaining = [n for n in range(1, 91) if n not in self.drawn_numbers]
        if not remaining:
            messagebox.showinfo("Terminé", "Il ne reste plus de numéro à tirer.")
            return

        self.animation_running = True
        self._set_controls_state("disabled")

        final_number = random.choice(remaining)

        # 3.5 secondes d'animation avec ralentissement progressif
        total_duration_ms = 3500
        start = self.root.winfo_toplevel().tk.call("after", "info")
        _ = start  # évite l'avertissement des linters sur variable inutilisée

        self._animate_roll(
            elapsed=0,
            duration=total_duration_ms,
            final_number=final_number,
            min_delay=40,
            max_delay=320,
        )

    def _animate_roll(
        self, elapsed: int, duration: int, final_number: int, min_delay: int, max_delay: int
    ) -> None:
        progress = min(elapsed / duration, 1)

        if progress >= 1:
            self.last_label.configure(text=f"{final_number:02d}", fg=self.ACCENT)
            self.add_number(final_number)
            self.animation_running = False
            self._set_controls_state("normal")
            return

        # Affichage rapide puis ralenti (courbe quadratique)
        remaining = [n for n in range(1, 91) if n not in self.drawn_numbers]
        rolling_number = random.choice(remaining)
        self.last_label.configure(text=f"{rolling_number:02d}", fg="#fde68a")

        delay = int(min_delay + (max_delay - min_delay) * (progress ** 2))
        self.root.after(
            delay,
            lambda: self._animate_roll(
                elapsed + delay,
                duration,
                final_number,
                min_delay,
                max_delay,
            ),
        )

    def set_gain(self, gain_name: str) -> None:
        self.current_gain.set(f"Gain annoncé : {gain_name}")

    def reset(self) -> None:
        if self.animation_running:
            return

        self.drawn_numbers.clear()
        self.entry_var.set("")
        self.current_gain.set("Aucun gain annoncé")
        self._refresh_recent_labels()
        self._refresh_history()

        for label in self.cell_labels.values():
            label.configure(bg="#111827", fg=self.TEXT)

    # ---------------- Rendu ---------------- #
    def _refresh_recent_labels(self) -> None:
        values = self.drawn_numbers[-3:]
        formatted = [f"{n:02d}" for n in values]

        self.last_label.configure(text=formatted[-1] if len(formatted) >= 1 else "--", fg=self.ACCENT)
        self.second_label.configure(text=formatted[-2] if len(formatted) >= 2 else "--")
        self.third_label.configure(text=formatted[-3] if len(formatted) >= 3 else "--")

    def _refresh_history(self) -> None:
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")

        if not self.drawn_numbers:
            self.history_text.insert("end", "Aucun numéro tiré pour le moment.")
        else:
            numbers = " - ".join(f"{n:02d}" for n in self.drawn_numbers)
            self.history_text.insert("end", numbers)

        self.history_text.configure(state="disabled")

    def _mark_number(self, number: int) -> None:
        lbl = self.cell_labels[number]
        lbl.configure(bg=self.SUCCESS, fg="#052e16")
        self._flash_cell(lbl, count=4)

    def _flash_cell(self, label: tk.Label, count: int) -> None:
        if count <= 0:
            label.configure(bg=self.SUCCESS, fg="#052e16")
            return

        current_bg = label.cget("bg")
        next_bg = "#86efac" if current_bg == self.SUCCESS else self.SUCCESS
        label.configure(bg=next_bg)
        self.root.after(120, lambda: self._flash_cell(label, count - 1))

    def _pulse_last_number(self) -> None:
        base_size = 120

        def step(i: int) -> None:
            if i > 6:
                self.last_label.configure(font=("Segoe UI Black", base_size))
                return
            size = base_size + (10 if i % 2 == 0 else 0)
            self.last_label.configure(font=("Segoe UI Black", size))
            self.root.after(60, lambda: step(i + 1))

        step(0)

    def _set_controls_state(self, state: str) -> None:
        self.entry.configure(state=state)
        self.add_button.configure(state=state)
        self.random_button.configure(state=state)
        self.reset_button.configure(state=state)
        for button in self.gain_buttons:
            button.configure(state=state)

    # ---------------- Utilitaires ---------------- #
    def _draw_gradient(self, event) -> None:
        self.bg_canvas.delete("grad")
        width = max(event.width, 1)
        height = max(event.height, 1)

        r1, g1, b1 = self._hex_to_rgb(self.BG_START)
        r2, g2, b2 = self._hex_to_rgb(self.BG_END)

        for i in range(height):
            ratio = i / height
            nr = int(r1 + (r2 - r1) * ratio)
            ng = int(g1 + (g2 - g1) * ratio)
            nb = int(b1 + (b2 - b1) * ratio)
            color = f"#{nr:02x}{ng:02x}{nb:02x}"
            self.bg_canvas.create_line(0, i, width, i, tags=("grad",), fill=color)

        self.bg_canvas.lower("all")

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    @staticmethod
    def _shade(hex_color: str, amount: float) -> str:
        r, g, b = LottoApp._hex_to_rgb(hex_color)
        if amount >= 0:
            r = min(255, int(r + (255 - r) * amount))
            g = min(255, int(g + (255 - g) * amount))
            b = min(255, int(b + (255 - b) * amount))
        else:
            factor = 1 + amount
            r = max(0, int(r * factor))
            g = max(0, int(g * factor))
            b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"


def main() -> None:
    root = tk.Tk()
    app = LottoApp(root)
    app.entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
