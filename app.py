import random
import tkinter as tk
from tkinter import messagebox


class LotoApp:
    """Application desktop de loto français (1 a 90)."""

    LIGHT_THEME = {
        "app_bg": "#f4efe5",
        "panel_bg": "#fffaf4",
        "panel_alt": "#efe6d7",
        "soft_green": "#e8f1e7",
        "soft_terracotta": "#f5e3dc",
        "soft_gold": "#f9efd0",
        "soft_blue": "#e7eef5",
        "deep_green": "#2f5d4a",
        "gold": "#c99a42",
        "terracotta": "#c26f53",
        "ink": "#25312d",
        "muted": "#75807c",
        "input_bg": "#ffffff",
        "grid_idle": "#e6ddcf",
        "grid_drawn": "#ffd67b",
        "grid_drawn_text": "#2e2a22",
        "toggle_bg": "#d9e5df",
        "toggle_fg": "#2f5d4a",
        "history_bg": "#efe6d7",
        "undo_bg": "#a6b4b1",
        "gain_quine": "#8f6a5f",
    }

    DARK_THEME = {
        "app_bg": "#14181d",
        "panel_bg": "#1d242b",
        "panel_alt": "#28313a",
        "soft_green": "#22362e",
        "soft_terracotta": "#3a2b2a",
        "soft_gold": "#3a3321",
        "soft_blue": "#202f3c",
        "deep_green": "#72c29a",
        "gold": "#e4b85a",
        "terracotta": "#d98b70",
        "ink": "#eef2f3",
        "muted": "#a9b4ba",
        "input_bg": "#11161b",
        "grid_idle": "#303942",
        "grid_drawn": "#e4b85a",
        "grid_drawn_text": "#181d21",
        "toggle_bg": "#2b3943",
        "toggle_fg": "#eef2f3",
        "history_bg": "#151b20",
        "undo_bg": "#51606b",
        "gain_quine": "#9f7e74",
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Loto Français")
        self.root.geometry("1420x920")
        self.root.minsize(1120, 760)

        self.drawn_numbers: list[int] = []
        self.undo_stack: list[dict[str, object]] = []
        self.animation_running = False
        self.compact_layout = False
        self.editing_title = False
        self.current_gain = ""
        self.last_clicked_number: int | None = None
        self.grid_cells: dict[int, tk.Label] = {}

        self.is_dark_mode = tk.BooleanVar(value=True)
        self.title_var = tk.StringVar(value="Loto Français")
        self.manual_var = tk.StringVar()
        self.counter_var = tk.StringVar(value="0 / 90")
        self.animation_var = tk.StringVar(value="--")
        self.gain_var = tk.StringVar(value="Aucune annonce")

        self.theme = self.DARK_THEME.copy()
        self.root.configure(bg=self.theme["app_bg"])

        # Conteneur principal fixe
        self.root_frame = tk.Frame(self.root, bg=self.theme["app_bg"])
        self.root_frame.pack(fill="both", expand=True)

        self.header_card = self._create_card(self.root_frame)
        self.header_card.pack(fill="x", pady=18, padx=18)

        self.content_frame = tk.Frame(self.root_frame, bg=self.theme["app_bg"])
        self.content_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self._build_header()
        self._build_content()
        self._bind_events()
        self._refresh_view()
        self._apply_theme()

    def _bind_mouse_wheel(self, widget) -> None:
        """Active le scroll avec la molette sur tous les widgets."""
        widget.bind_all("<MouseWheel>", self._on_mousewheel)
        widget.bind_all("<Button-4>", self._on_mousewheel)
        widget.bind_all("<Button-5>", self._on_mousewheel)

    def _on_sidebar_resize(self, event) -> None:
        """Ajuste la largeur de la frame interne de la sidebar."""
        self.sidebar_canvas.itemconfig(self.sidebar_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        if event.num == 4 or event.delta > 0: self.sidebar_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: self.sidebar_canvas.yview_scroll(1, "units")

    def _build_header(self) -> None:
        self.header_left = tk.Frame(self.header_card, bg=self.theme["panel_bg"])
        self.header_left.pack(side="left", fill="x", expand=True, padx=20, pady=18)

        self.header_title_wrap = tk.Frame(self.header_left, bg=self.theme["panel_bg"])
        self.header_title_wrap.pack(anchor="w")

        self.header_title_label = tk.Label(
            self.header_title_wrap,
            textvariable=self.title_var,
            font=("Segoe UI", 26, "bold"),
            cursor="xterm",
        )
        self.header_title_label.pack(anchor="w")
        self.header_title_label.bind("<Button-1>", lambda _event: self.begin_title_edit())

        self.title_entry = tk.Entry(
            self.header_title_wrap,
            textvariable=self.title_var,
            bd=0,
            relief="flat",
            font=("Segoe UI", 25, "bold"),
            width=24,
            insertwidth=2,
        )
        self.title_entry.bind("<Return>", lambda _event: self.finish_title_edit())
        self.title_entry.bind("<Escape>", lambda _event: self.cancel_title_edit())
        self.title_entry.bind("<FocusOut>", lambda _event: self.finish_title_edit())

        self.header_subtitle_label = tk.Label(
            self.header_left,
            text="Tableau de tirage 1 à 90",
            font=("Segoe UI", 13),
            anchor="w",
        )
        self.header_subtitle_label.pack(anchor="w", pady=(4, 0))

        self.header_right = tk.Frame(self.header_card, bg=self.theme["panel_bg"])
        self.header_right.pack(side="right", padx=20, pady=18)

        self.theme_toggle_button = self._create_button(
            self.header_right, "Mode sombre", self.toggle_theme, self.theme["toggle_bg"], self.theme["toggle_fg"]
        )
        self.theme_toggle_button.pack(side="right")

        self.title_hint_label = tk.Label(
            self.header_right,
            text="Cliquer sur le titre pour modifier",
            font=("Segoe UI", 11),
        )
        self.title_hint_label.pack(side="right", padx=(0, 12))

    def _build_content(self) -> None:
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=0)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Création du conteneur de Sidebar scrollable
        self.sidebar_container = tk.Frame(self.content_frame, bg=self.theme["app_bg"])
        self.sidebar_container.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        
        self.sidebar_canvas = tk.Canvas(self.sidebar_container, bg=self.theme["app_bg"], highlightthickness=0, width=350)
        self.sidebar_scrollbar = tk.Scrollbar(self.sidebar_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)
        
        self.sidebar_scrollbar.pack(side="right", fill="y")
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)

        self.sidebar = tk.Frame(self.sidebar_canvas, bg=self.theme["app_bg"])
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")

        self.sidebar.bind("<Configure>", lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.bind("<Configure>", self._on_sidebar_resize)
        self._bind_mouse_wheel(self.root)

        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=0)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.grid_area = tk.Frame(self.content_frame, bg=self.theme["app_bg"])
        self.grid_area.grid(row=0, column=1, sticky="nsew")
        self.grid_area.grid_rowconfigure(0, weight=1)
        self.grid_area.grid_columnconfigure(0, weight=1)

        self._build_recent_card()
        self._build_gain_card()
        self._build_control_card()
        self._build_grid_card()

    def _build_recent_card(self) -> None:
        self.recent_card = self._create_card(self.sidebar)
        self.recent_card.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        top = tk.Frame(self.recent_card, bg=self.theme["panel_bg"])
        top.pack(fill="x", padx=18, pady=(18, 12))

        self.recent_title_label = tk.Label(top, text="Derniers numeros", font=("Segoe UI", 18, "bold"))
        self.recent_title_label.pack(side="left")

        self.counter_badge = tk.Label(
            top, textvariable=self.counter_var, font=("Segoe UI", 13, "bold"), padx=14, pady=8
        )
        self.counter_badge.pack(side="right")

        self.ball_labels: list[tk.Label] = []
        ball_specs = [
            ("--", ("Segoe UI", 70, "bold")),
            ("--", ("Segoe UI", 40, "bold")),
            ("--", ("Segoe UI", 28, "bold")),
        ]

        for text, font in ball_specs:
            label = tk.Label(self.recent_card, text=text, font=font, pady=12)
            label.pack(fill="x", padx=18, pady=(0, 12))
            self.ball_labels.append(label)

    def _build_gain_card(self) -> None:
        self.gain_card = self._create_card(self.sidebar)
        self.gain_card.grid(row=2, column=0, sticky="ew", pady=(18, 0))

        top = tk.Frame(self.gain_card, bg=self.theme["panel_bg"])
        top.pack(fill="x", padx=18, pady=(18, 8))

        self.gain_title_label = tk.Label(top, text="Annonce de partie", font=("Segoe UI", 16, "bold"))
        self.gain_title_label.pack(side="left")

        self.gain_tag_label = self._create_tag(top, "Choix rapide")
        self.gain_tag_label.pack(side="right")

        self.gain_button_row = tk.Frame(self.gain_card, bg=self.theme["panel_bg"])
        self.gain_button_row.pack(fill="x", padx=18, pady=(0, 18))
        for index in range(3):
            self.gain_button_row.grid_columnconfigure(index, weight=1)

        self.gain_buttons = [
            self._create_button(
                self.gain_button_row,
                "Quine simple",
                lambda: self.set_gain("Quine simple"),
                self.theme["gain_quine"],
                "#ffffff",
            ),
            self._create_button(
                self.gain_button_row,
                "Double quine",
                lambda: self.set_gain("Double quine"),
                self.theme["terracotta"],
                "#ffffff",
            ),
            self._create_button(
                self.gain_button_row,
                "Carton plein",
                lambda: self.set_gain("Carton plein"),
                self.theme["deep_green"],
                "#ffffff",
            ),
        ]

        for index, button in enumerate(self.gain_buttons):
            button.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0))

    def _build_history_card(self) -> None:
        self.history_card = tk.Frame(self.grid_card, bd=0, highlightthickness=0)
        self.history_card.grid_columnconfigure(0, weight=1)

        self.history_title_label = tk.Label(self.history_card, text="Historique", font=("Segoe UI", 12, "bold"))
        self.history_title_label.grid(row=0, column=0, sticky="w")

        self.history_numbers_label = tk.Label(
            self.history_card,
            text="Aucun numero tire pour le moment.",
            font=("Consolas", 12),
            anchor="w",
            justify="left",
            wraplength=760,
            pady=2,
        )
        self.history_numbers_label.grid(row=1, column=0, sticky="ew", pady=(2, 0))

    def _build_grid_card(self) -> None:
        self.grid_card = self._create_card(self.grid_area)
        self.grid_card.grid(row=0, column=0, sticky="nsew")
        self.grid_card.grid_rowconfigure(3, weight=1)
        self.grid_card.grid_columnconfigure(0, weight=1)

        top = tk.Frame(self.grid_card, bg=self.theme["panel_bg"])
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 6))
        top.grid_columnconfigure(0, weight=1)

        left = tk.Frame(top, bg=self.theme["panel_bg"])
        left.grid(row=0, column=0, sticky="w")

        self.grid_title_label = tk.Label(left, text="Grille des numeros", font=("Segoe UI", 18, "bold"))
        self.grid_title_label.pack(anchor="w")

        self.animation_label = tk.Label(top, textvariable=self.animation_var, font=("Segoe UI", 34, "bold"))
        self.animation_label.grid(row=0, column=1, sticky="e")

        self.grid_gain_status_label = tk.Label(
            self.grid_card,
            textvariable=self.gain_var,
            font=("Segoe UI", 22, "bold"),
            anchor="center",
            pady=8,
        )
        self.grid_gain_status_label.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        self._build_history_card()
        self.history_card.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 8))

        self.grid_container = tk.Frame(self.grid_card, bg=self.theme["panel_bg"])
        self.grid_container.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))

        for row in range(9):
            self.grid_container.grid_rowconfigure(row, weight=1, uniform="grid_rows")
        for col in range(10):
            self.grid_container.grid_columnconfigure(col, weight=1, uniform="grid_cols")

        for number in range(1, 91):
            row = (number - 1) // 10
            col = (number - 1) % 10
            cell = tk.Label(
                self.grid_container,
                text=str(number),
                font=("Segoe UI", 16, "bold"),
                width=5,
                height=2,
                cursor="hand2",
                bd=0,
                relief="flat",
            )
            cell.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            cell.bind("<Button-1>", lambda _event, n=number: self.add_number(n))
            self.grid_cells[number] = cell

    def _build_control_card(self) -> None:
        self.control_card = self._create_card(self.sidebar)
        self.control_card.grid(row=1, column=0, sticky="ew")
        self.control_card.grid_columnconfigure(0, weight=1)

        self.control_title_label = tk.Label(self.control_card, text="Commandes", font=("Segoe UI", 16, "bold"))
        self.control_title_label.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        self.draw_panel = self._create_inner_panel(self.control_card)
        self.draw_panel.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))

        self._fill_draw_panel()

    def _fill_draw_panel(self) -> None:
        self.random_button = self._create_button(
            self.draw_panel, "Lancer le tirage", self.start_random_animation, self.theme["deep_green"], "#ffffff"
        )
        self.random_button.pack(anchor="center", expand=True)

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda _event: self.add_from_field() if not self.editing_title else None)
        self.root.bind("<Configure>", self._on_root_resize)

    def _create_card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bd=0, highlightthickness=0)

    def _create_inner_panel(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bd=0, highlightthickness=0, padx=16, pady=14)

    def _create_tag(self, parent: tk.Widget, text: str) -> tk.Label:
        return tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"), padx=10, pady=6)

    def _create_button(
        self, parent: tk.Widget, text: str, command, color: str, text_color: str
    ) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=text_color,
            activebackground=self._shade(color, -0.10),
            activeforeground=text_color,
            bd=0,
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            padx=16,
            pady=10,
            cursor="hand2",
        )
        button.bind("<Enter>", lambda _event: button.configure(bg=self._shade(color, 0.06)))
        button.bind("<Leave>", lambda _event, base=color: button.configure(bg=base))
        return button

    def toggle_theme(self) -> None:
        self.is_dark_mode.set(not self.is_dark_mode.get())
        self.theme = self.DARK_THEME.copy() if self.is_dark_mode.get() else self.LIGHT_THEME.copy()
        self._apply_theme()

    def begin_title_edit(self) -> None:
        if self.editing_title or self.animation_running:
            return
        self.editing_title = True
        self.header_title_label.pack_forget()
        self.title_entry.pack(anchor="w")
        self.title_entry.focus_set()
        self.title_entry.selection_range(0, "end")

    def finish_title_edit(self) -> None:
        if not self.editing_title:
            self._apply_window_title()
            return
        text = self.title_var.get().strip()
        self.title_var.set(text or "Loto Francais")
        self.title_entry.pack_forget()
        self.header_title_label.pack(anchor="w")
        self.editing_title = False
        self._apply_window_title()

    def cancel_title_edit(self) -> None:
        if not self.editing_title:
            return
        if not self.title_var.get().strip():
            self.title_var.set("Loto Francais")
        self.title_entry.pack_forget()
        self.header_title_label.pack(anchor="w")
        self.editing_title = False
        self._apply_window_title()

    def _apply_window_title(self) -> None:
        self.root.title(self.title_var.get().strip() or "Loto Français")

    def add_from_field(self) -> None:
        raw = self.manual_var.get().strip()
        if not raw:
            return
        if not raw.isdigit():
            self.manual_var.set("")
            messagebox.showwarning("Saisie invalide", "Entrez un nombre entre 1 et 90.")
            return
        if self.add_number(int(raw)):
            self.manual_var.set("")

    def add_number(self, number: int) -> bool:
        if self.animation_running:
            messagebox.showinfo("Tirage en cours", "Attendez la fin du tirage en cours.")
            return False
        if number < 1 or number > 90:
            messagebox.showwarning("Nombre invalide", "Le numero doit etre compris entre 1 et 90.")
            return False
        if number in self.drawn_numbers:
            self._flash_existing_number(number)
            messagebox.showwarning("Doublon", "Ce numero a deja ete tire.")
            return False

        self._push_undo_state()
        self.drawn_numbers.append(number)
        self.last_clicked_number = number
        self._refresh_view()
        self._flash_new_number(number)
        self._pulse_last_ball()

        if len(self.drawn_numbers) == 90:
            messagebox.showinfo("Partie terminee", "Tous les numeros ont ete tires.")
        return True

    def set_gain(self, gain: str) -> None:
        self.current_gain = gain
        self.gain_var.set(gain)

    def undo_last_action(self) -> None:
        if self.animation_running:
            return
        if not self.undo_stack:
            messagebox.showinfo("Annulation", "Aucune action a annuler.")
            return

        state = self.undo_stack.pop()
        self.drawn_numbers = list(state["drawn_numbers"])
        self.current_gain = str(state["current_gain"])
        self.gain_var.set(self.current_gain or "Aucune annonce")
        self.animation_var.set("--")
        self.manual_var.set("")
        self.last_clicked_number = self.drawn_numbers[-1] if self.drawn_numbers else None
        self._refresh_view()

    def reset(self) -> None:
        if self.animation_running:
            return
        self._push_undo_state()
        self.drawn_numbers.clear()
        self.current_gain = ""
        self.gain_var.set("Aucune annonce")
        self.animation_var.set("--")
        self.manual_var.set("")
        self.last_clicked_number = None
        self._refresh_view()

    def start_random_animation(self) -> None:
        if self.animation_running:
            return

        remaining = self._remaining_numbers()
        if not remaining:
            messagebox.showinfo("Partie terminee", "Il ne reste plus de numero a tirer.")
            return

        self.animation_running = True
        self._set_controls_state("disabled")
        final_number = random.choice(remaining)
        self._animate_roll(0, 4000, final_number)

    def _animate_roll(self, elapsed: int, total_duration: int, final_number: int) -> None:
        progress = min(elapsed / total_duration, 1)

        if progress >= 1:
            self._push_undo_state()
            self.drawn_numbers.append(final_number)
            self.last_clicked_number = final_number
            self.animation_var.set(f"{final_number:02d}")
            self.animation_label.configure(fg=self.theme["deep_green"])
            self._refresh_view(skip_animation_text=True)
            self._flash_new_number(final_number)
            self.root.after(850, self._finish_animation)
            return

        remaining = self._remaining_numbers()
        if not remaining:
            self._finish_animation()
            return

        display = random.choice(remaining)
        self.animation_var.set(f"{display:02d}")
        self.animation_label.configure(fg=self.theme["gold"])

        min_delay = 30
        max_delay = 170
        delay = int(min_delay + (max_delay - min_delay) * (progress ** 2))
        self.root.after(delay, lambda: self._animate_roll(elapsed + delay, total_duration, final_number))

    def _finish_animation(self) -> None:
        self.animation_running = False
        self.animation_var.set("--")
        self.animation_label.configure(fg=self.theme["gold"])
        self._set_controls_state("normal")
        self._pulse_last_ball()

    def _push_undo_state(self) -> None:
        self.undo_stack.append(
            {
                "drawn_numbers": self.drawn_numbers.copy(),
                "current_gain": self.current_gain,
            }
        )

    def _refresh_view(self, skip_animation_text: bool = False) -> None:
        self._apply_window_title()
        self._refresh_counter()
        self._refresh_recent_numbers()
        self._refresh_history()
        self._refresh_grid()
        if not skip_animation_text and not self.animation_running:
            self.animation_var.set("--")
            self.animation_label.configure(fg=self.theme["gold"])
        if not self.current_gain:
            self.gain_var.set("Aucune annonce")

    def _refresh_counter(self) -> None:
        self.counter_var.set(f"{len(self.drawn_numbers)} / 90")

    def _refresh_recent_numbers(self) -> None:
        recent = list(reversed(self.drawn_numbers[-3:]))
        # Couleurs de texte pour donner un effet de profondeur (le plus récent est plus vif)
        fading_colors = [self.theme["deep_green"], self.theme["muted"], self.theme["muted"]]
        
        for index, label in enumerate(self.ball_labels):
            if index < len(recent):
                label.configure(text=f"{recent[index]:02d}")
                # Appliquer une couleur plus discrète pour les anciens numéros
                if index > 0:
                    label.configure(fg=fading_colors[index])
            else:
                label.configure(text="--")
                label.configure(fg=self.theme["muted"])

    def _refresh_history(self) -> None:
        if not self.drawn_numbers:
            self.history_numbers_label.configure(text="Aucun numero tire pour le moment.")
        else:
            chunks = []
            for index, number in enumerate(self.drawn_numbers):
                separator = "   " if index else ""
                chunks.append(f"{separator}{number:02d}")
            self.history_numbers_label.configure(text="".join(chunks))

    def _refresh_grid(self) -> None:
        for number, cell in self.grid_cells.items():
            if number in self.drawn_numbers:
                bg = self.theme["grid_drawn"]
                fg = self.theme["grid_drawn_text"]
            else:
                bg = self.theme["grid_idle"]
                fg = self.theme["ink"]
            cell.configure(bg=bg, fg=fg)

    def _flash_new_number(self, number: int) -> None:
        cell = self.grid_cells[number]
        base_bg = self.theme["grid_drawn"]
        highlight_bg = self._shade(base_bg, 0.15)
        self._pulse_cell(cell, base_bg, highlight_bg, 4)

    def _flash_existing_number(self, number: int) -> None:
        cell = self.grid_cells[number]
        base_bg = self.theme["grid_drawn"] if number in self.drawn_numbers else self.theme["grid_idle"]
        highlight_bg = self.theme["terracotta"]
        self._pulse_cell(cell, base_bg, highlight_bg, 3)

    def _pulse_cell(self, cell: tk.Label, base_bg: str, flash_bg: str, repeats: int) -> None:
        def step(index: int) -> None:
            if index >= repeats * 2:
                number = int(cell.cget("text"))
                fg = self.theme["grid_drawn_text"] if number in self.drawn_numbers else self.theme["ink"]
                cell.configure(bg=base_bg, fg=fg)
                return
            is_flash = index % 2 == 0
            fg = "#ffffff" if is_flash and flash_bg == self.theme["terracotta"] else self.theme["grid_drawn_text"]
            cell.configure(bg=flash_bg if is_flash else base_bg, fg=fg)
            self.root.after(90, lambda: step(index + 1))

        step(0)

    def _pulse_last_ball(self) -> None:
        if not self.drawn_numbers:
            return

        colors = [self.theme["gold"], self._shade(self.theme["gold"], 0.18), "#f7d889", self._shade(self.theme["gold"], 0.18), self.theme["gold"]]
        final_fg = self.theme["deep_green"]

        def step(index: int) -> None:
            if index >= len(colors):
                self.ball_labels[0].configure(fg=final_fg)
                return
            self.ball_labels[0].configure(fg=colors[index])
            self.root.after(75, lambda: step(index + 1))

        step(0)

    def _remaining_numbers(self) -> list[int]:
        return [number for number in range(1, 91) if number not in self.drawn_numbers]

    def _set_controls_state(self, state: str) -> None:
        self.random_button.configure(state=state)
        self.title_entry.configure(state=state)
        self.theme_toggle_button.configure(state=state)
        for button in self.gain_buttons:
            button.configure(state=state)

    def _on_root_resize(self, event) -> None:
        if event.widget is not self.root:
            return
        self._apply_responsive_layout(max(self.root.winfo_width(), 1120), max(self.root.winfo_height(), 760))

    def _apply_responsive_layout(self, width: int, height: int) -> None:
        compact = width < 1280
        if compact != self.compact_layout:
            self.compact_layout = compact
            self.sidebar_container.grid_forget()
            self.grid_area.grid_forget()
            if compact:
                self.content_frame.grid_columnconfigure(0, weight=1)
                self.content_frame.grid_columnconfigure(1, weight=0)
                self.content_frame.grid_rowconfigure(0, weight=1)
                self.content_frame.grid_rowconfigure(1, weight=1)
                self.sidebar_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 18))
                self.grid_area.grid(row=1, column=0, sticky="nsew")
            else:
                self.content_frame.grid_rowconfigure(0, weight=1)
                self.content_frame.grid_rowconfigure(1, weight=0)
                self.content_frame.grid_columnconfigure(0, weight=0)
                self.content_frame.grid_columnconfigure(1, weight=1)
                self.sidebar_container.grid(row=0, column=0, sticky="nsew", padx=(0, 18), pady=0)
                self.grid_area.grid(row=0, column=1, sticky="nsew")

        scale = min(width / 1420, height / 920)
        scale = max(0.78, min(scale, 1.10))

        self.header_title_label.configure(font=("Segoe UI", max(20, int(26 * scale)), "bold"))
        self.title_entry.configure(font=("Segoe UI", max(19, int(25 * scale)), "bold"), width=max(16, int(24 * scale)))
        self.header_subtitle_label.configure(font=("Segoe UI", max(11, int(13 * scale))))
        self.title_hint_label.configure(font=("Segoe UI", max(9, int(11 * scale))))

        self.recent_title_label.configure(font=("Segoe UI", max(14, int(18 * scale)), "bold"))
        self.counter_badge.configure(font=("Segoe UI", max(10, int(13 * scale)), "bold"))
        self.gain_title_label.configure(font=("Segoe UI", max(13, int(16 * scale)), "bold"))
        self.history_title_label.configure(font=("Segoe UI", max(11, int(12 * scale)), "bold"))
        self.history_numbers_label.configure(
            font=("Consolas", max(10, int(12 * scale))),
            wraplength=max(460, int((width - 520) * 0.9)),
        )
        self.grid_title_label.configure(font=("Segoe UI", max(14, int(18 * scale)), "bold"))
        self.grid_gain_status_label.configure(font=("Segoe UI", max(16, int(22 * scale)), "bold"))
        self.animation_label.configure(font=("Segoe UI", max(24, int(34 * scale)), "bold"))

        ball_fonts = [
            ("Segoe UI", max(48, int(70 * scale)), "bold"),
            ("Segoe UI", max(28, int(40 * scale)), "bold"),
            ("Segoe UI", max(20, int(28 * scale)), "bold"),
        ]
        for label, font in zip(self.ball_labels, ball_fonts):
            label.configure(font=font)

        button_font = ("Segoe UI", max(10, int(12 * scale)), "bold")
        self.theme_toggle_button.configure(font=button_font)
        self.random_button.configure(font=button_font)
        for button in self.gain_buttons:
            button.configure(font=("Segoe UI", max(9, int(11 * scale)), "bold"))

        cell_font = max(11, int(16 * scale))
        cell_width = max(4, int(5 * scale))
        cell_height = max(1, int(2 * scale))
        pad = max(2, int(4 * scale))
        for cell in self.grid_cells.values():
            cell.configure(font=("Segoe UI", cell_font, "bold"), width=cell_width, height=cell_height)
            cell.grid_configure(padx=pad, pady=pad)

    def _apply_theme(self) -> None:
        self.root.configure(bg=self.theme["app_bg"])
        self.root_frame.configure(bg=self.theme["app_bg"])
        self.sidebar_container.configure(bg=self.theme["app_bg"])
        self.sidebar_canvas.configure(bg=self.theme["app_bg"])
        self.content_frame.configure(bg=self.theme["app_bg"])

        for card in [self.header_card, self.recent_card, self.gain_card, self.control_card, self.grid_card]:
            card.configure(bg=self.theme["panel_bg"])

        for frame in [self.header_left, self.header_right, self.header_title_wrap]:
            frame.configure(bg=self.theme["panel_bg"])

        for frame in [self.sidebar, self.grid_area]:
            frame.configure(bg=self.theme["app_bg"])

        self.header_title_label.configure(bg=self.theme["panel_bg"], fg=self.theme["deep_green"])
        self.title_entry.configure(
            bg=self.theme["input_bg"],
            fg=self.theme["ink"],
            insertbackground=self.theme["ink"],
        )
        self.header_subtitle_label.configure(bg=self.theme["panel_bg"], fg=self.theme["muted"])
        self.title_hint_label.configure(bg=self.theme["panel_bg"], fg=self.theme["muted"])

        self.theme_toggle_button.configure(
            text="Mode clair" if self.is_dark_mode.get() else "Mode sombre",
            bg=self.theme["toggle_bg"],
            fg=self.theme["toggle_fg"],
            activebackground=self._shade(self.theme["toggle_bg"], -0.10),
            activeforeground=self.theme["toggle_fg"],
        )

        self.counter_badge.configure(bg=self.theme["soft_green"], fg=self.theme["deep_green"])

        ball_backgrounds = [self.theme["soft_green"], self.theme["soft_terracotta"], self.theme["soft_gold"]]
        ball_foregrounds = [self.theme["deep_green"], self.theme["terracotta"], self.theme["gold"]]
        for index, label in enumerate(self.ball_labels):
            label.configure(bg=ball_backgrounds[index], fg=ball_foregrounds[index])

        for label in [
            self.recent_title_label,
            self.gain_title_label,
            self.history_title_label,
            self.grid_title_label,
            self.control_title_label,
        ]:
            label.configure(bg=self.theme["panel_bg"] if label in [self.recent_title_label, self.gain_title_label, self.history_title_label, self.grid_title_label] else label.master.cget("bg"), fg=self.theme["ink"])
        self.grid_gain_status_label.configure(bg=self.theme["panel_alt"], fg=self.theme["gold"])
        self.animation_label.configure(bg=self.theme["panel_bg"], fg=self.theme["gold"])

        self.gain_button_row.configure(bg=self.theme["panel_bg"])
        self.history_card.configure(bg=self.theme["panel_bg"])
        self.history_title_label.configure(bg=self.theme["panel_bg"], fg=self.theme["muted"])
        self.history_numbers_label.configure(bg=self.theme["panel_bg"], fg=self.theme["ink"])

        self.grid_container.configure(bg=self.theme["panel_bg"])
        self._refresh_grid()

        self.control_card.configure(bg=self.theme["panel_bg"])
        self.draw_panel.configure(bg=self.theme["soft_green"])

        self.random_button.configure(
            bg=self.theme["deep_green"],
            fg="#ffffff",
            activebackground=self._shade(self.theme["deep_green"], -0.10),
            activeforeground="#ffffff",
        )

        gain_colors = [self.theme["gain_quine"], self.theme["terracotta"], self.theme["deep_green"]]
        for button, color in zip(self.gain_buttons, gain_colors):
            button.configure(
                bg=color,
                fg="#ffffff",
                activebackground=self._shade(color, -0.10),
                activeforeground="#ffffff",
            )

        self.gain_tag_label.configure(bg=self.theme["panel_alt"], fg=self.theme["muted"])

        top_frames = [
            child for child in [self.recent_card.winfo_children()[0], self.gain_card.winfo_children()[0], self.grid_card.winfo_children()[0]]
        ]
        for frame in top_frames:
            frame.configure(bg=self.theme["panel_bg"])
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=self.theme["panel_bg"])

        self._refresh_view()

    @staticmethod
    def _hex_to_rgb(value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    @staticmethod
    def _shade(color: str, amount: float) -> str:
        r, g, b = LotoApp._hex_to_rgb(color)
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
    app = LotoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
