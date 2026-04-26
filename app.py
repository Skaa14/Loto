import random
import tkinter as tk
from tkinter import messagebox


class LottoApp:
    """Application de gestion de loto (1 a 90)."""

    BG_START = "#0f172a"
    BG_END = "#1d4ed8"
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
        self.root.minsize(860, 620)

        self.drawn_numbers: list[int] = []
        self.draw_history: list[tuple[int, str]] = []
        self.undo_stack: list[dict[str, object]] = []
        self.current_gain = tk.StringVar(value="")
        self.animation_running = False
        self.compact_layout = False

        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self._draw_gradient)

        self.main = tk.Frame(self.root, bg="")
        self.main.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.94)

        self._build_layout()
        self._refresh_recent_labels()
        self._refresh_history()
        self._update_header_display()

        self.root.bind("<Return>", self._on_enter)
        self.root.bind("<Configure>", self._on_root_resize)

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

        self.title_var = tk.StringVar(value="LOTO FRANCAIS")
        self.title_entry = tk.Entry(
            self.left_panel,
            textvariable=self.title_var,
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Segoe UI", 26, "bold"),
            justify="center",
            bd=0,
            relief="flat",
            insertbackground=self.TEXT,
        )
        self.title_entry.pack(fill="x", padx=16, pady=(18, 18), ipady=4)

        recent_frame = tk.Frame(self.left_panel, bg=self.PANEL_ALT)
        recent_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.rolling_label = tk.Label(
            recent_frame,
            text="",
            fg="#fde68a",
            bg=self.PANEL_ALT,
            font=("Segoe UI Black", 30),
        )
        self.rolling_label.pack(pady=(16, 0))

        self.last_label = tk.Label(
            recent_frame,
            text="--",
            fg=self.ACCENT,
            bg=self.PANEL_ALT,
            font=("Segoe UI Black", 120),
        )
        self.last_label.pack(pady=(8, 0))

        self.second_label = tk.Label(
            recent_frame,
            text="--",
            fg=self.TEXT,
            bg=self.PANEL_ALT,
            font=("Segoe UI", 52, "bold"),
        )
        self.second_label.pack()

        self.third_label = tk.Label(
            recent_frame,
            text="--",
            fg=self.MUTED,
            bg=self.PANEL_ALT,
            font=("Segoe UI", 34),
        )
        self.third_label.pack(pady=(0, 16))

        self.controls_frame = tk.Frame(self.left_panel, bg=self.PANEL)
        self.controls_frame.pack(fill="x", padx=16, pady=(8, 10))
        for col in range(5):
            self.controls_frame.columnconfigure(col, weight=0)
        self.controls_frame.columnconfigure(1, weight=1)
        self.controls_frame.columnconfigure(3, weight=2)
        self.controls_frame.columnconfigure(4, weight=1)

        self.manual_title_label = tk.Label(
            self.controls_frame,
            text="Numero",
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Segoe UI", 12, "bold"),
        )
        self.manual_title_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self.controls_frame,
            textvariable=self.entry_var,
            width=6,
            font=("Segoe UI", 16, "bold"),
            justify="center",
            bd=0,
            relief="flat",
            bg="#e5e7eb",
            fg="#111827",
            insertbackground="#111827",
        )
        self.entry.grid(row=0, column=1, sticky="w", padx=(0, 10), ipady=6)

        self.undo_button = self._create_button(
            self.controls_frame, "Annuler", self.undo_last_action, "#94a3b8"
        )
        self.undo_button.grid(row=0, column=2, sticky="ew", padx=(0, 6))

        self.random_button = self._create_button(
            self.controls_frame, "Tirage aleatoire", self.start_random_animation, self.ACCENT
        )
        self.random_button.grid(row=0, column=3, sticky="ew", padx=(0, 6))

        self.reset_button = self._create_button(self.controls_frame, "Reset", self.reset, self.DANGER)
        self.reset_button.grid(row=0, column=4, sticky="ew")

        gains_frame = tk.Frame(self.left_panel, bg=self.PANEL)
        gains_frame.pack(fill="x", padx=16, pady=(8, 10))

        btn_row = tk.Frame(gains_frame, bg=self.PANEL)
        btn_row.pack(fill="x")

        self.gain_buttons = [
            self._create_button(btn_row, "Quine simple", lambda: self.set_gain("QUINE SIMPLE"), "#6366f1"),
            self._create_button(btn_row, "Double quine", lambda: self.set_gain("DOUBLE QUINE"), "#8b5cf6"),
            self._create_button(btn_row, "Carton plein", lambda: self.set_gain("CARTON PLEIN"), "#ec4899"),
        ]

        for i, button in enumerate(self.gain_buttons):
            button.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="ew")
            btn_row.columnconfigure(i, weight=1)

    def _build_right_panel(self) -> None:
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        wrap = tk.Frame(self.right_panel, bg=self.PANEL_ALT)
        wrap.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        wrap.rowconfigure(2, weight=1)
        wrap.columnconfigure(0, weight=1)

        self.grid_gain_label = tk.Label(
            wrap,
            text="",
            fg=self.ACCENT,
            bg=self.PANEL_ALT,
            font=("Segoe UI Black", 28),
        )
        self.grid_gain_label.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        history_wrap = tk.Frame(wrap, bg=self.PANEL_ALT)
        history_wrap.grid(row=1, column=0, pady=(0, 12))

        self.history_title_label = tk.Label(
            history_wrap,
            text="Historique des numeros tires",
            fg=self.TEXT,
            bg=self.PANEL_ALT,
            font=("Segoe UI", 12, "bold"),
        )
        self.history_title_label.pack(anchor="w", pady=(0, 8))

        self.history_text = tk.Text(
            history_wrap,
            height=3,
            wrap="word",
            bg="#0b1220",
            fg=self.TEXT,
            insertbackground=self.TEXT,
            font=("Consolas", 13),
            bd=0,
            padx=10,
            pady=10,
            width=44,
        )
        self.history_text.pack()
        self.history_text.configure(state="disabled")

        self.grid_host = tk.Frame(wrap, bg=self.PANEL_ALT)
        self.grid_host.grid(row=2, column=0, sticky="nsew")
        self.grid_host.rowconfigure(0, weight=1)
        self.grid_host.columnconfigure(0, weight=1)

        self.grid_container = tk.Frame(self.grid_host, bg=self.PANEL_ALT)
        self.grid_container.grid(row=0, column=0)

        self.cell_labels: dict[int, tk.Label] = {}
        for row in range(9):
            self.grid_container.rowconfigure(row, weight=1, uniform="numbers")
        for col in range(10):
            self.grid_container.columnconfigure(col, weight=1, uniform="numbers")

        for number in range(1, 91):
            row = (number - 1) // 10
            col = (number - 1) % 10
            lbl = tk.Label(
                self.grid_container,
                text=f"{number}",
                bg="#111827",
                fg=self.TEXT,
                bd=1,
                relief="solid",
                font=("Segoe UI", 16, "bold"),
                width=4,
                height=2,
            )
            lbl.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self.cell_labels[number] = lbl

        self._apply_responsive_layout()

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

    def _on_enter(self, _event) -> None:
        if not self.animation_running:
            self._add_from_entry()

    def _add_from_entry(self) -> None:
        raw = self.entry_var.get().strip()
        if not raw:
            return
        if not raw.isdigit():
            self.entry_var.set("")
            messagebox.showwarning("Saisie invalide", "Veuillez saisir un nombre entier entre 1 et 90.")
            return
        self.add_number(int(raw), source="manual")

    def add_number(self, number: int, source: str = "manual") -> bool:
        if number < 1 or number > 90:
            self.entry_var.set("")
            messagebox.showwarning("Hors limite", "Le numero doit etre compris entre 1 et 90.")
            return False
        if number in self.drawn_numbers:
            self.entry_var.set("")
            messagebox.showwarning("Doublon", f"Le numero {number} a deja ete tire.")
            return False

        self._push_undo_state()
        self.drawn_numbers.append(number)
        self.draw_history.append((number, source))
        self.entry_var.set("")
        self._refresh_recent_labels()
        self._refresh_history()
        self._mark_number(number)
        self._pulse_last_number()

        if len(self.drawn_numbers) == 90:
            messagebox.showinfo("Termine", "Tous les numeros ont ete tires.")
        return True

    def start_random_animation(self) -> None:
        if self.animation_running:
            return

        remaining = [n for n in range(1, 91) if n not in self.drawn_numbers]
        if not remaining:
            messagebox.showinfo("Termine", "Il ne reste plus de numero a tirer.")
            return

        self.animation_running = True
        self._set_controls_state("disabled")
        final_number = random.choice(remaining)

        self._animate_roll(
            elapsed=0,
            duration=3500,
            final_number=final_number,
            min_delay=40,
            max_delay=320,
        )

    def _animate_roll(
        self, elapsed: int, duration: int, final_number: int, min_delay: int, max_delay: int
    ) -> None:
        progress = min(elapsed / duration, 1)
        if progress >= 1:
            self.rolling_label.configure(text="")
            self.add_number(final_number, source="random")
            self.animation_running = False
            self._set_controls_state("normal")
            return

        remaining = [n for n in range(1, 91) if n not in self.drawn_numbers]
        rolling_number = random.choice(remaining)
        self.rolling_label.configure(text=f"EN COURS : {rolling_number:02d}")

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
        self.current_gain.set(gain_name)
        self._update_header_display()

    def undo_last_action(self) -> None:
        if self.animation_running:
            return

        if not self.undo_stack:
            messagebox.showinfo("Annulation", "Aucune action a annuler.")
            return

        state = self.undo_stack.pop()
        self._restore_state(state)

    def reset(self) -> None:
        if self.animation_running:
            return

        self._push_undo_state()
        self.drawn_numbers.clear()
        self.draw_history.clear()
        self.entry_var.set("")
        self.current_gain.set("")
        self.rolling_label.configure(text="")
        self._refresh_recent_labels()
        self._refresh_history()
        self._update_header_display()

        for label in self.cell_labels.values():
            label.configure(bg="#111827", fg=self.TEXT)

    def _refresh_recent_labels(self) -> None:
        values = self.drawn_numbers[-3:]
        formatted = [f"{n:02d}" for n in values]
        self.last_label.configure(text=formatted[-1] if len(formatted) >= 1 else "--", fg=self.ACCENT)
        self.second_label.configure(text=formatted[-2] if len(formatted) >= 2 else "--")
        self.third_label.configure(text=formatted[-3] if len(formatted) >= 3 else "--")

    def _update_header_display(self) -> None:
        gain = self.current_gain.get().strip()
        if gain:
            self.grid_gain_label.configure(text=gain)
        else:
            self.grid_gain_label.configure(text="")

    def _refresh_history(self) -> None:
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")

        if not self.drawn_numbers:
            self.history_text.insert("end", "Aucun numero tire pour le moment.")
        else:
            numbers = " - ".join(f"{n:02d}" for n in self.drawn_numbers)
            self.history_text.insert("end", numbers)

        self.history_text.configure(state="disabled")

    def _mark_number(self, number: int) -> None:
        lbl = self.cell_labels[number]
        lbl.configure(bg=self.SUCCESS, fg="#052e16")
        self._flash_cell(lbl, count=4)

    def _push_undo_state(self) -> None:
        snapshot = {
            "drawn_numbers": self.drawn_numbers.copy(),
            "draw_history": self.draw_history.copy(),
            "current_gain": self.current_gain.get(),
        }
        self.undo_stack.append(snapshot)

    def _restore_state(self, state: dict[str, object]) -> None:
        self.drawn_numbers = list(state["drawn_numbers"])
        self.draw_history = list(state["draw_history"])
        self.current_gain.set(str(state["current_gain"]))
        self.entry_var.set("")
        self.rolling_label.configure(text="")
        self._rebuild_grid()
        self._refresh_recent_labels()
        self._refresh_history()
        self._update_header_display()

    def _rebuild_grid(self) -> None:
        for label in self.cell_labels.values():
            label.configure(bg="#111827", fg=self.TEXT)
        for number in self.drawn_numbers:
            self.cell_labels[number].configure(bg=self.SUCCESS, fg="#052e16")

    def _flash_cell(self, label: tk.Label, count: int) -> None:
        if count <= 0:
            label.configure(bg=self.SUCCESS, fg="#052e16")
            return

        current_bg = label.cget("bg")
        next_bg = "#86efac" if current_bg == self.SUCCESS else self.SUCCESS
        label.configure(bg=next_bg)
        self.root.after(120, lambda: self._flash_cell(label, count - 1))

    def _pulse_last_number(self) -> None:
        pulse_colors = [self.ACCENT, "#fbbf24", "#fde68a", "#fbbf24", self.ACCENT]

        def step(i: int) -> None:
            if i >= len(pulse_colors):
                self.last_label.configure(fg=self.ACCENT)
                return
            self.last_label.configure(fg=pulse_colors[i])
            self.root.after(70, lambda: step(i + 1))

        step(0)

    def _set_controls_state(self, state: str) -> None:
        self.entry.configure(state=state)
        self.undo_button.configure(state=state)
        self.random_button.configure(state=state)
        self.reset_button.configure(state=state)
        for button in self.gain_buttons:
            button.configure(state=state)

    def _on_root_resize(self, event) -> None:
        if event.widget is self.root:
            self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        width = max(self.root.winfo_width(), 860)
        height = max(self.root.winfo_height(), 620)
        compact = width < 1180

        if compact != self.compact_layout:
            self.compact_layout = compact
            if compact:
                self.main.columnconfigure(0, weight=1)
                self.main.columnconfigure(1, weight=0)
                self.main.rowconfigure(0, weight=0)
                self.main.rowconfigure(1, weight=1)
                self.left_panel.grid_configure(row=0, column=0, padx=0, pady=(0, 12), sticky="nsew")
                self.right_panel.grid_configure(row=1, column=0, padx=0, pady=0, sticky="nsew")
            else:
                self.main.columnconfigure(0, weight=2)
                self.main.columnconfigure(1, weight=3)
                self.main.rowconfigure(0, weight=1)
                self.main.rowconfigure(1, weight=0)
                self.left_panel.grid_configure(row=0, column=0, padx=(0, 12), pady=0, sticky="nsew")
                self.right_panel.grid_configure(row=0, column=1, padx=(12, 0), pady=0, sticky="nsew")

        scale = min(width / 1366, height / 820)
        scale = max(0.72, min(scale, 1.18))

        self.title_entry.configure(font=("Segoe UI", max(18, int(26 * scale)), "bold"))
        self.grid_gain_label.configure(font=("Segoe UI Black", max(20, int(28 * scale))))
        self.rolling_label.configure(font=("Segoe UI Black", max(20, int(34 * scale))))
        self.last_label.configure(font=("Segoe UI Black", max(68, int(120 * scale))))
        self.second_label.configure(font=("Segoe UI", max(28, int(52 * scale)), "bold"))
        self.third_label.configure(font=("Segoe UI", max(18, int(34 * scale))))
        self.manual_title_label.configure(font=("Segoe UI", max(10, int(12 * scale)), "bold"))
        self.history_title_label.configure(font=("Segoe UI", max(10, int(12 * scale)), "bold"))
        self.entry.configure(font=("Segoe UI", max(12, int(16 * scale)), "bold"), width=6)
        self.history_text.configure(
            font=("Consolas", max(10, int(13 * scale))),
            width=max(30, int(44 * scale)),
            height=max(2, int(3 * scale)),
        )

        button_font = ("Segoe UI", max(9, int(11 * scale)), "bold")
        self.undo_button.configure(font=button_font)
        self.random_button.configure(font=button_font)
        self.reset_button.configure(font=button_font)
        for button in self.gain_buttons:
            button.configure(font=button_font)

        cell_font_size = max(10, int(16 * scale))
        cell_width = max(3, int(4 * scale))
        cell_height = max(1, int(2 * scale))
        cell_pad = max(2, int(4 * scale))
        for label in self.cell_labels.values():
            label.configure(
                font=("Segoe UI", cell_font_size, "bold"),
                width=cell_width,
                height=cell_height,
            )
            label.grid_configure(padx=cell_pad, pady=cell_pad)

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
