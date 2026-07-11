import os
import sys
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QFrame, QScrollArea, QMessageBox,
    QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

def resource_path(relative_path):
    """ Obtient le chemin absolu vers la ressource, compatible dev et PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Theme:
    DARK = {
        "app_bg": "#14181d",
        "panel_bg": "#1d242b",
        "panel_alt": "#28313a",
        "deep_green": "#72c29a",
        "gold": "#e4b85a",
        "terracotta": "#d98b70",
        "ink": "#eef2f3",
        "muted": "#a9b4ba",
        "grid_idle": "#303942",
        "grid_drawn": "#388E3C",
        "grid_text": "#181d21",
        "grid_last": "#e4b85a",
    }
    LIGHT = {
        "app_bg": "#f4efe5",
        "panel_bg": "#fffaf4",
        "panel_alt": "#efe6d7",
        "deep_green": "#2f5d4a",
        "gold": "#c99a42",
        "terracotta": "#c26f53",
        "ink": "#25312d",
        "muted": "#75807c",
        "grid_idle": "#e6ddcf",
        "grid_drawn": "#A5D6A7",
        "grid_text": "#2e2a22",
        "grid_last": "#f9cf7a",
    }

class ClickableLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()

class PublicWindow(QMainWindow):
    """Fenêtre destinée au vidéoprojecteur (Public)"""
    closed = Signal()

    def __init__(self, theme):
        super().__init__()
        self.setWindowTitle("Loto - Affichage Public")
        self.theme = theme
        self.ball_labels = []
        self.cells = {}
        self._setup_ui()

    def closeEvent(self, event):
        # Prévient la fenêtre principale (Alt+F4, bouton X, etc.) pour qu'elle
        # ne garde pas une référence obsolète et puisse rouvrir le projecteur
        self.closed.emit()
        super().closeEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Double-clic pour basculer entre plein écran et fenêtré"""
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event):
        """Raccourcis clavier : F11 pour plein écran, Echap pour quitter le plein écran"""
        if event.key() == Qt.Key_F11:
            self.mouseDoubleClickEvent(None)
        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showMaximized()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Top: Gain + Last Ball
        top_hbox = QHBoxLayout()
        self.gain_label = QLabel("Bonne chance !")
        self.gain_label.setObjectName("gainDisplay")
        self.gain_label.setAlignment(Qt.AlignCenter)
        self.gain_label.setFont(QFont("Segoe UI", 40, QFont.Bold))
        
        # Last 3 balls container
        balls_layout = QHBoxLayout()
        balls_layout.setSpacing(15)
        for i, (size, px) in enumerate([(110, 220), (70, 150), (50, 110)]):
            lbl = QLabel("--")
            lbl.setFixedSize(px, px)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", size, QFont.Bold))
            lbl.setStyleSheet(f"background-color: {self.theme['panel_alt']}; border-radius: {px//2}px; border: 4px solid {self.theme['gold'] if i==0 else self.theme['grid_idle']};")
            balls_layout.addWidget(lbl)
            self.ball_labels.append(lbl)
            
        top_hbox.addWidget(self.gain_label, 1)
        top_hbox.addLayout(balls_layout)
        layout.addLayout(top_hbox)

        # Middle: Grid
        grid_frame = QFrame()
        grid_frame.setObjectName("gridPanel")
        grid_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.num_grid = QGridLayout(grid_frame)
        self.num_grid.setSpacing(8)
        for n in range(1, 91):
            lbl = QLabel(str(n))
            lbl.setMinimumSize(85, 70)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 26, QFont.Bold))
            lbl.setObjectName("gridCell")
            # Style par défaut (idle), même charte que la grille de l'app principale
            lbl.setStyleSheet(
                f"background-color: {self.theme['grid_idle']}; color: {self.theme['ink']}; "
                f"border-radius: 8px; border: 3px solid transparent; font-weight: bold;"
            )
            self.num_grid.addWidget(lbl, (n-1)//10, (n-1)%10)
            self.cells[n] = lbl
        layout.addWidget(grid_frame, stretch=1)

        # Bottom: History
        self.history_label = QLabel("Historique : ")
        self.history_label.setWordWrap(True)
        self.history_label.setObjectName("historyLabel")
        self.history_label.setMinimumHeight(100)
        self.history_label.setFont(QFont("Segoe UI", 98, QFont.Bold))
        layout.addWidget(self.history_label)

    def update_view(self, drawn_numbers, current_gain, anim_val=None):
        # Update Balls (Tirage en cours ou derniers numéros)
        if anim_val:
            # Pendant l'animation
            self.ball_labels[0].setText(anim_val)
            self.ball_labels[0].setStyleSheet(
                f"background-color: {self.theme['panel_alt']}; border-radius: 110px; "
                f"color: {self.theme['gold']}; border: 4px solid {self.theme['gold']};"
            )
            recent = list(reversed(drawn_numbers[-2:]))
            for i in range(1, 3):
                val = f"{recent[i-1]:02d}" if (i-1) < len(recent) else "--"
                self.ball_labels[i].setText(val)
        else:
            # Tirage au repos
            recent = list(reversed(drawn_numbers[-3:]))
            for i in range(3):
                val = f"{recent[i]:02d}" if i < len(recent) else "--"
                self.ball_labels[i].setText(val)
                # Bordure dorée uniquement pour le plus récent
                color = self.theme['gold'] if i == 0 and val != "--" else self.theme['grid_idle']
                text_color = self.theme['gold'] if i == 0 else self.theme['muted']
                px = [220, 150, 110][i]
                self.ball_labels[i].setStyleSheet(
                    f"background-color: {self.theme['panel_alt']}; border-radius: {px//2}px; "
                    f"color: {text_color}; border: 4px solid {color};"
                )

        # Update Grid (bordure colorée + fond, même charte que la grille de l'app principale)
        last_num = drawn_numbers[-1] if drawn_numbers and not anim_val else None
        for n, lbl in self.cells.items():
            if n == last_num:
                bg, border = self.theme['grid_last'], self.theme['terracotta']
            elif n in drawn_numbers:
                bg, border = self.theme['grid_drawn'], self.theme['deep_green']
            else:
                bg, border = self.theme['grid_idle'], "transparent"
            text_color = self.theme['grid_text'] if n in drawn_numbers else self.theme['ink']
            lbl.setStyleSheet(
                f"background-color: {bg}; color: {text_color}; border-radius: 8px; "
                f"border: 3px solid {border}; font-weight: bold;"
            )

        # Update History & Gain
        self.gain_label.setText(current_gain or "Loto Français")
        
        total = len(drawn_numbers)
        # On définit un seuil de saturation (environ 40 numéros). 
        # Au-delà, on réduit les 3 derniers pour préserver la taille de la grille.
        is_saturated = total > 40
        
        history_html = f'<span style="font-size: 22px; color: {self.theme["muted"]};">Historique :</span><br>'
        for i, n in enumerate(drawn_numbers):
            is_recent = i >= total - 3
            # Les 3 derniers ne restent gros que si on a encore de la place (pas de saturation)
            size = "98px" if (is_recent and not is_saturated) else "48px"
            color = self.theme["gold"] if n == last_num else self.theme["deep_green"]
            history_html += f'<span style="font-size: {size}; color: {color};">{n:02d}</span>'
            if i < total - 1:
                sep_size = "98px" if (i >= total - 3 and not is_saturated) else "48px"
                history_html += f'<span style="font-size: {sep_size}; color: {self.theme["muted"]};"> - </span>'
        self.history_label.setText(history_html)

class LotoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loto Français")
        self.resize(1420, 920)
        self.setMinimumSize(1000, 700)
        self.setWindowIcon(QIcon(resource_path("bingoloto.ico")))

        self.drawn_numbers = []
        self.undo_stack = []
        self.redo_stack = []
        self.animation_running = False
        self.current_gain = ""
        self.is_dark_mode = True
        self.theme = Theme.DARK
        self.public_window = None

        self._setup_ui()
        self._apply_theme()
        QApplication.instance().installEventFilter(self)

        # État de l'animation de tirage (le scheduling se fait via QTimer.singleShot)
        self.anim_elapsed = 0
        self.anim_total = 3500
        self.final_number = 0

        self._refresh_ui()

    def closeEvent(self, event):
        # Ferme aussi la fenêtre publique (vidéoprojecteur), y compris en plein écran
        if self.public_window:
            self.public_window.close()
        super().closeEvent(event)

    def eventFilter(self, obj, event):
        # Valide le titre si on clique en dehors du champ d'édition
        if event.type() == QEvent.MouseButtonPress and self.title_edit.isVisible():
            local_pos = self.title_edit.mapFromGlobal(event.globalPosition().toPoint())
            if not self.title_edit.rect().contains(local_pos):
                self.title_edit.clearFocus()
        return super().eventFilter(obj, event)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # --- Header ---
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        
        title_vbox = QVBoxLayout()
        self.title_label = ClickableLabel("Loto Français")
        self.title_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.title_label.clicked.connect(self._edit_title)
        
        self.title_edit = QLineEdit("Loto Français")
        self.title_edit.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.title_edit.hide()
        self.title_edit.editingFinished.connect(self._save_title)
        
        subtitle = QLabel("Tableau de tirage 1 à 90")
        subtitle.setObjectName("subtitle")
        title_vbox.addWidget(self.title_label)
        title_vbox.addWidget(self.title_edit)
        title_vbox.addWidget(subtitle)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        
        self.projector_btn = QPushButton("📺")
        self.projector_btn.setFixedSize(50, 40)
        self.projector_btn.setToolTip("Activer le vidéoprojecteur")
        self.projector_btn.clicked.connect(self.toggle_projector)
        header_layout.addWidget(self.projector_btn)

        self.theme_btn = QPushButton("☀️")
        self.theme_btn.setFixedSize(50, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)
        
        self.main_layout.addWidget(header)

        # --- Content Area ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # ===== Colonne gauche : tirage en cours + derniers numéros + historique =====
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFixedWidth(300)
        left_scroll.setFrameShape(QFrame.NoFrame)

        left_content = QWidget()
        left_vbox = QVBoxLayout(left_content)
        left_vbox.setSpacing(20)

        # Numéro en cours de tirage + derniers numéros
        recent_card = self._create_card("Derniers numéros")
        self.anim_label = QLabel("--")
        self.anim_label.setObjectName("animLabel")
        self.anim_label.setAlignment(Qt.AlignCenter)
        self.anim_label.setFont(QFont("Segoe UI", 54, QFont.Bold))
        recent_card.layout().addWidget(self.anim_label)

        self.ball_labels = []
        for i, size in enumerate([36, 26, 20]):
            lbl = QLabel("--")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", size, QFont.Bold))
            lbl.setObjectName(f"ball_{i}")
            recent_card.layout().addWidget(lbl)
            self.ball_labels.append(lbl)
        left_vbox.addWidget(recent_card)

        # Historique (discret, compact, sous les derniers numéros, taille adaptative)
        history_card = self._create_card("Historique")
        self.history_title_label = history_card.title_label
        self.history_label = QLabel("")
        self.history_label.setWordWrap(True)
        self.history_label.setObjectName("historyLabel")
        self.history_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        history_card.layout().addWidget(self.history_label)
        left_vbox.addWidget(history_card)

        left_vbox.addStretch()
        left_scroll.setWidget(left_content)
        content_layout.addWidget(left_scroll)

        # ===== Colonne centrale : grille 1-90, espace maximisé =====
        grid_area = QVBoxLayout()

        self.gain_display = QLabel("Aucune annonce")
        self.gain_display.setObjectName("gainDisplay")
        self.gain_display.setAlignment(Qt.AlignCenter)
        self.gain_display.setFont(QFont("Segoe UI", 34, QFont.Bold))
        self.gain_display.setMinimumHeight(70)
        grid_area.addWidget(self.gain_display)

        self.grid_widget = QFrame()
        self.grid_widget.setObjectName("gridPanel")
        self.grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.num_grid = QGridLayout(self.grid_widget)
        self.num_grid.setSpacing(5)
        self.cells = {}

        for n in range(1, 91):
            btn = QPushButton(str(n))
            btn.setMinimumSize(60, 50)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFont(QFont("Segoe UI", 22, QFont.Bold))
            btn.clicked.connect(lambda ch, num=n: self.add_number(num))
            self.num_grid.addWidget(btn, (n-1)//10, (n-1)%10)
            self.cells[n] = btn

        grid_area.addWidget(self.grid_widget, 1)
        content_layout.addLayout(grid_area, 1)

        # ===== Colonne droite : commandes + annonces =====
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFixedWidth(300)
        right_scroll.setFrameShape(QFrame.NoFrame)

        right_content = QWidget()
        right_vbox = QVBoxLayout(right_content)
        right_vbox.setSpacing(20)

        # Commandes
        control_card = self._create_card("Commandes")
        self.draw_btn = QPushButton("LANCER LE TIRAGE")
        self.draw_btn.setObjectName("drawBtn")
        self.draw_btn.setMinimumHeight(60)
        self.draw_btn.clicked.connect(self.start_random_draw)
        control_card.layout().addWidget(self.draw_btn)

        self.undo_btn = QPushButton("◀ Retour")
        self.redo_btn = QPushButton("Avance ▶")
        self.undo_btn.clicked.connect(self.undo_action)
        self.redo_btn.clicked.connect(self.redo_action)
        nav_hbox = QHBoxLayout()
        nav_hbox.addWidget(self.undo_btn)
        nav_hbox.addWidget(self.redo_btn)
        control_card.layout().addLayout(nav_hbox)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_game)
        control_card.layout().addWidget(self.reset_btn)
        right_vbox.addWidget(control_card)

        # Annonces
        gain_card = self._create_card("Annonces")
        self.gain_hint_label = QLabel("⚠ Choisissez une annonce")
        self.gain_hint_label.setObjectName("hintLabel")
        self.gain_hint_label.setAlignment(Qt.AlignCenter)
        self.gain_hint_label.setWordWrap(True)
        self.gain_hint_label.hide()
        gain_card.layout().addWidget(self.gain_hint_label)

        self.gain_btns = []
        for text in ["Quine simple", "Double quine", "Carton plein"]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda ch, t=text: self.set_gain(t))
            gain_card.layout().addWidget(btn)
            self.gain_btns.append(btn)
        right_vbox.addWidget(gain_card)

        right_vbox.addStretch()
        right_scroll.setWidget(right_content)
        content_layout.addWidget(right_scroll)

        self.main_layout.addLayout(content_layout)

    def _create_card(self, title):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        lbl = QLabel(title.upper())
        lbl.setObjectName("cardTitle")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(lbl)
        card.title_label = lbl
        return card

    def _apply_theme(self):
        t = self.theme
        qss = f"""
            QMainWindow, QDialog, QMessageBox {{ background-color: {t['app_bg']}; }}
            
            QScrollArea, QScrollArea > QWidget > QWidget {{
                background-color: {t['app_bg']};
                border: none;
            }}

            #header {{ background-color: {t['panel_bg']}; border-radius: 12px; }}
            QLabel, QMessageBox QLabel {{ color: {t['ink']}; }}
            #subtitle, #cardTitle {{ color: {t['muted']}; }}
            #card {{ background-color: {t['panel_bg']}; border-radius: 12px; }}
            #gridPanel {{ background-color: {t['panel_bg']}; border-radius: 12px; padding: 10px; }}
            
            #historyLabel {{
                font-family: 'Segoe UI Semibold', 'Trebuchet MS', sans-serif;
                line-height: 1.6;
                color: {t['muted']};
            }}

            QPushButton {{
                background-color: {t['panel_alt']};
                color: {t['ink']};
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {t['muted']}; }}
            QPushButton:disabled {{ background-color: {t['grid_idle']}; color: {t['muted']}; }}

            #drawBtn {{
                background-color: {t['deep_green']};
                color: white;
                font-size: 16px;
            }}
            #drawBtn:disabled {{ background-color: {t['grid_idle']}; color: {t['muted']}; }}
            
            #gainDisplay {{
                background-color: {t['panel_alt']};
                color: {t['gold']};
                border-radius: 12px;
                margin-bottom: 5px;
                padding: 10px;
            }}
            
            #animLabel {{
                color: {t['gold']};
                background-color: {t['panel_alt']};
                border-radius: 14px;
                padding: 14px;
            }}

            #hintLabel {{
                color: {t['terracotta']};
                background-color: {t['panel_alt']};
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }}
            
            #gridPanel QPushButton {{
                background-color: {t['grid_idle']};
                color: {t['ink']};
                font-size: 28px;
            }}

            #gridPanel QPushButton.drawn {{
                background-color: {t['grid_drawn']} !important;
                color: {t['grid_text']} !important;
                border: 3px solid {t['deep_green']};
                font-weight: bold;
            }}

            #gridPanel QPushButton.last-drawn {{
                background-color: {t['grid_last']} !important;
                color: {t['grid_text']} !important;
                border: 3px solid {t['terracotta']};
                font-weight: bold;
            }}
            
            QLineEdit {{
                background-color: {t['panel_alt']};
                color: {t['ink']};
                border: 2px solid {t['deep_green']};
                border-radius: 6px;
            }}
        """
        QApplication.instance().setStyleSheet(qss)
        self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")

        # Re-appliquer le thème à la fenêtre publique si elle existe
        if self.public_window:
            self.public_window.theme = t

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.theme = Theme.DARK if self.is_dark_mode else Theme.LIGHT
        self._apply_theme()
        self._refresh_ui()

    # --- Logique ---

    def _edit_title(self):
        self.title_label.hide()
        self.title_edit.setText(self.title_label.text())
        self.title_edit.show()
        self.title_edit.setFocus()

    def _save_title(self):
        new_title = self.title_edit.text().strip() or "Loto Français"
        self.title_label.setText(new_title)
        self.setWindowTitle(new_title)
        self.title_edit.hide()
        self.title_label.show()

    def toggle_projector(self):
        if self.public_window is None:
            self.public_window = PublicWindow(self.theme)
            self.public_window.closed.connect(self._on_public_window_closed)

            # Détection du 2ème écran
            screens = QApplication.screens()
            if len(screens) > 1:
                target_screen = screens[1]
                self.public_window.setScreen(target_screen)
                self.public_window.setGeometry(target_screen.geometry())
                self.public_window.showFullScreen()
            else:
                self.public_window.show()
            self._refresh_ui()
        else:
            self.public_window.close()

    def _on_public_window_closed(self):
        self.public_window = None

    def add_number(self, num):
        if self.animation_running: return
        if num in self.drawn_numbers:
            QMessageBox.warning(self, "Doublon", f"Le numéro {num} a déjà été tiré.")
            return

        self.undo_stack.append({"numbers": list(self.drawn_numbers), "gain": self.current_gain})
        self.redo_stack.clear()
        self.drawn_numbers.append(num)
        self._refresh_ui()

        if len(self.drawn_numbers) == 90:
            QMessageBox.information(self, "Fin", "Tous les numéros ont été tirés !")

    def start_random_draw(self):
        if not self.current_gain or self.animation_running:
            return
        remaining = [i for i in range(1, 91) if i not in self.drawn_numbers]
        if not remaining: return

        self.animation_running = True
        self.final_number = random.choice(remaining)
        self.anim_elapsed = 0
        self.draw_btn.setEnabled(False)
        self._animation_step()

    def _animation_step(self):
        # Calcul de la progression (0.0 à 1.0)
        progress = min(self.anim_elapsed / self.anim_total, 1.0)

        if self.anim_elapsed >= self.anim_total:
            self.animation_running = False
            self.add_number(self.final_number)
            return

        # Calcul d'un délai exponentiel pour l'effet de ralentissement
        # Commence à 40ms (rapide) et finit à environ 450ms (lent)
        delay = int(40 + (progress ** 2.5) * 400)
        self.anim_elapsed += delay
        
        temp = random.randint(1, 90)
        self.anim_label.setText(f"{temp:02d}")

        if self.public_window:
            self.public_window.update_view(self.drawn_numbers, self.current_gain, anim_val=f"{temp:02d}")
        
        # Planifie le prochain changement de numéro
        QTimer.singleShot(delay, self._animation_step)

    def set_gain(self, text):
        self.current_gain = text
        self.gain_display.setText(text)
        self._refresh_ui()

    def undo_action(self):
        if not self.undo_stack: return
        self.redo_stack.append({"numbers": list(self.drawn_numbers), "gain": self.current_gain})
        state = self.undo_stack.pop()
        self.drawn_numbers = state["numbers"]
        self.current_gain = state["gain"]
        self._refresh_ui()

    def redo_action(self):
        if not self.redo_stack: return
        self.undo_stack.append({"numbers": list(self.drawn_numbers), "gain": self.current_gain})
        state = self.redo_stack.pop()
        self.drawn_numbers = state["numbers"]
        self.current_gain = state["gain"]
        self._refresh_ui()

    def reset_game(self):
        if not self.drawn_numbers: return
        confirm = QMessageBox.question(self, "Reset", "Voulez-vous vraiment recommencer la partie ?", 
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.drawn_numbers.clear()
            self.current_gain = ""
            self._refresh_ui()

    def _refresh_ui(self):
        # Update Grid
        last_num = self.drawn_numbers[-1] if self.drawn_numbers else None
        for n, btn in self.cells.items():
            if n == last_num:
                btn.setProperty("class", "last-drawn")
            elif n in self.drawn_numbers:
                btn.setProperty("class", "drawn")
            else:
                btn.setProperty("class", "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Update Balls (Derniers numéros)
        if not self.animation_running:
            self.anim_label.setText(f"{last_num:02d}" if last_num else "--")
        recent = list(reversed(self.drawn_numbers[-3:]))
        for i in range(3):
            val = f"{recent[i]:02d}" if i < len(recent) else "--"
            self.ball_labels[i].setText(val)
            # Effet de fondu sur les couleurs
            color = self.theme['deep_green'] if i == 0 else self.theme['muted']
            self.ball_labels[i].setStyleSheet(f"color: {color};")

        # Update History (discret, taille adaptative selon le nombre de tirages)
        total = len(self.drawn_numbers)
        self.history_title_label.setText(f"HISTORIQUE ({total})")
        if total <= 10:
            num_size = 26
        elif total <= 25:
            num_size = 21
        elif total <= 45:
            num_size = 17
        elif total <= 70:
            num_size = 14
        else:
            num_size = 12

        items = []
        for n in self.drawn_numbers:
            # Le dernier numéro est en doré, les autres restent discrets
            color = self.theme['gold'] if n == last_num else self.theme['muted']
            weight = "bold" if n == last_num else "normal"
            items.append(f'<span style="font-size: {num_size}px; color: {color}; font-weight: {weight};">{n:02d}</span>')

        sep = f'<span style="color: {self.theme["muted"]};"> · </span>'
        hist_text = sep.join(items) if items else f'<span style="color: {self.theme["muted"]};">Aucun tirage</span>'
        self.history_label.setText(hist_text)
        self.gain_display.setText(self.current_gain or "Aucune annonce")

        # Disponibilité des commandes
        has_gain = bool(self.current_gain)
        remaining = any(i not in self.drawn_numbers for i in range(1, 91))
        self.draw_btn.setEnabled(has_gain and not self.animation_running and remaining)
        self.undo_btn.setEnabled(bool(self.undo_stack))
        self.redo_btn.setEnabled(bool(self.redo_stack))
        self.gain_hint_label.setVisible(not has_gain)

        # Sync Public Window
        if self.public_window:
            self.public_window.update_view(self.drawn_numbers, self.current_gain)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Base propre pour le stylisage
    window = LotoApp()
    window.show()
    sys.exit(app.exec())
