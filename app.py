import os
import sys
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QFrame, QScrollArea, QMessageBox,
    QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
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
    def __init__(self, theme):
        super().__init__()
        self.setWindowTitle("Loto - Affichage Public")
        self.theme = theme
        self.ball_labels = []
        self.cells = {}
        self._setup_ui()

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
        self.num_grid = QGridLayout(grid_frame)
        self.num_grid.setSpacing(8)
        for n in range(1, 91):
            lbl = QLabel(str(n))
            lbl.setFixedSize(85, 70)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
            lbl.setObjectName("gridCell")
            # Style par défaut (idle)
            lbl.setStyleSheet(f"background-color: {self.theme['grid_idle']}; color: {self.theme['ink']}; border-radius: 8px;")
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
            self.ball_labels[0].setStyleSheet(self.ball_labels[0].styleSheet().replace(self.theme['grid_idle'], self.theme['gold']))
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

        # Update Grid
        last_num = drawn_numbers[-1] if drawn_numbers and not anim_val else None
        for n, lbl in self.cells.items():
            if n == last_num:
                color = self.theme['grid_last']
            elif n in drawn_numbers:
                color = self.theme['grid_drawn']
            else:
                color = self.theme['grid_idle']
            lbl.setStyleSheet(f"background-color: {color}; color: {self.theme['grid_text'] if n in drawn_numbers else self.theme['ink']}; border-radius: 8px;")

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
        self.animation_running = False
        self.current_gain = ""
        self.is_dark_mode = True
        self.theme = Theme.DARK
        self.public_window = None

        self._setup_ui()
        self._apply_theme()
        
        # Timer pour l'animation de tirage
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._animation_step)
        self.anim_elapsed = 0
        self.anim_total = 3500
        self.final_number = 0

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
        
        # Sidebar (Scrollable)
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFixedWidth(380)
        sidebar_scroll.setFrameShape(QFrame.NoFrame)
        
        sidebar_content = QWidget()
        self.sidebar_vbox = QVBoxLayout(sidebar_content)
        self.sidebar_vbox.setSpacing(20)
        
        # Derniers numéros
        recent_card = self._create_card("Derniers numéros")
        self.ball_labels = []
        for i, size in enumerate([60, 35, 25]):
            lbl = QLabel("--")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", size, QFont.Bold))
            lbl.setObjectName(f"ball_{i}")
            recent_card.layout().addWidget(lbl)
            self.ball_labels.append(lbl)
        self.sidebar_vbox.addWidget(central_widget_card := recent_card)

        # Commandes
        control_card = self._create_card("Commandes")
        self.draw_btn = QPushButton("LANCER LE TIRAGE")
        self.draw_btn.setObjectName("drawBtn")
        self.draw_btn.setMinimumHeight(60)
        self.draw_btn.clicked.connect(self.start_random_draw)
        control_card.layout().addWidget(self.draw_btn)
        
        self.undo_btn = QPushButton("Annuler")
        self.reset_btn = QPushButton("Reset")
        self.undo_btn.clicked.connect(self.undo_action)
        self.reset_btn.clicked.connect(self.reset_game)
        reset_hbox = QHBoxLayout()
        reset_hbox.addWidget(self.undo_btn)
        reset_hbox.addWidget(self.reset_btn)
        control_card.layout().addLayout(reset_hbox)
        self.sidebar_vbox.addWidget(control_card)

        # Annonces
        gain_card = self._create_card("Annonces")
        self.gain_btns = []
        for text in ["Quine simple", "Double quine", "Carton plein"]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda ch, t=text: self.set_gain(t))
            gain_card.layout().addWidget(btn)
            self.gain_btns.append(btn)
        self.sidebar_vbox.addWidget(gain_card)
        
        self.sidebar_vbox.addStretch()
        sidebar_scroll.setWidget(sidebar_content)
        content_layout.addWidget(sidebar_scroll)

        # Main Grid Area
        grid_area = QVBoxLayout()
        
        # Status bar (Gain + Tirage en cours)
        status_hbox = QHBoxLayout()
        self.gain_display = QLabel("Aucune annonce")
        self.gain_display.setObjectName("gainDisplay")
        self.gain_display.setAlignment(Qt.AlignCenter)
        self.gain_display.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        self.anim_label = QLabel("--")
        self.anim_label.setObjectName("animLabel")
        self.anim_label.setFixedWidth(100)
        self.anim_label.setAlignment(Qt.AlignCenter)
        self.anim_label.setFont(QFont("Segoe UI", 40, QFont.Bold))
        
        status_hbox.addWidget(self.gain_display, 1)
        status_hbox.addWidget(self.anim_label)
        grid_area.addLayout(status_hbox)

        # History
        self.history_label = QLabel("Historique : ")
        self.history_label.setWordWrap(True)
        self.history_label.setObjectName("historyLabel")
        grid_area.addWidget(self.history_label)

        # Grille 1-90
        self.grid_widget = QFrame()
        self.grid_widget.setObjectName("gridPanel")
        self.num_grid = QGridLayout(self.grid_widget)
        self.num_grid.setSpacing(5)
        self.cells = {}
        
        for n in range(1, 91):
            btn = QPushButton(str(n))
            btn.setFixedSize(65, 55)
            btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
            btn.clicked.connect(lambda ch, num=n: self.add_number(num))
            self.num_grid.addWidget(btn, (n-1)//10, (n-1)%10)
            self.cells[n] = btn
            
        grid_area.addWidget(self.grid_widget)
        content_layout.addLayout(grid_area, 1)
        
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
                font-size: 20px;
                line-height: 1.4;
                background-color: {t['panel_alt']};
                padding: 12px;
                border-radius: 10px;
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
            
            #drawBtn {{
                background-color: {t['deep_green']};
                color: white;
                font-size: 16px;
            }}
            
            #gainDisplay {{
                background-color: {t['panel_alt']};
                color: {t['gold']};
                border-radius: 12px;
                margin-bottom: 5px;
            }}
            
            #animLabel {{ color: {t['gold']}; }}
            
            #gridPanel QPushButton {{
                background-color: {t['grid_idle']};
                color: {t['ink']};
                font-size: 18px;
            }}
            
            #gridPanel QPushButton.drawn {{
                background-color: {t['grid_drawn']} !important;
                color: {t['grid_text']} !important;
                border: none;
                font-weight: bold;
            }}

            #gridPanel QPushButton.last-drawn {{
                background-color: {t['grid_last']} !important;
                color: {t['grid_text']} !important;
                border: none;
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
            self.public_window = None

    def add_number(self, num):
        if self.animation_running: return
        if num in self.drawn_numbers:
            QMessageBox.warning(self, "Doublon", f"Le numéro {num} a déjà été tiré.")
            return

        self.undo_stack.append({"numbers": list(self.drawn_numbers), "gain": self.current_gain})
        self.drawn_numbers.append(num)
        self._refresh_ui()
        
        if len(self.drawn_numbers) == 90:
            QMessageBox.information(self, "Fin", "Tous les numéros ont été tirés !")

    def start_random_draw(self):
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
            self.draw_btn.setEnabled(True)
            self.add_number(self.final_number)
            # On affiche le numéro final de façon permanente
            self.anim_label.setText(f"{self.final_number:02d}")
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
        state = self.undo_stack.pop()
        self.drawn_numbers = state["numbers"]
        self.current_gain = state["gain"]
        self.anim_label.setText("--")
        self._refresh_ui()

    def reset_game(self):
        if not self.drawn_numbers: return
        confirm = QMessageBox.question(self, "Reset", "Voulez-vous vraiment recommencer la partie ?", 
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.drawn_numbers.clear()
            self.current_gain = ""
            self.anim_label.setText("--")
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
        recent = list(reversed(self.drawn_numbers[-3:]))
        for i in range(3):
            val = f"{recent[i]:02d}" if i < len(recent) else "--"
            self.ball_labels[i].setText(val)
            # Effet de fondu sur les couleurs
            color = self.theme['deep_green'] if i == 0 else self.theme['muted']
            self.ball_labels[i].setStyleSheet(f"color: {color};")

        # Update History
        items = []
        for n in self.drawn_numbers:
            # Le dernier numéro est en doré, les autres en vert
            color = self.theme['gold'] if n == last_num else self.theme['deep_green']
            items.append(f'<span style="color: {color}; font-weight: bold;">{n:02d}</span>')
        
        hist_text = " &nbsp; ".join(items)
        self.history_label.setText(f'<span style="color: {self.theme["muted"]}; font-size: 14px; font-weight: normal;">Historique ({len(self.drawn_numbers)}) :</span><br>{hist_text}')
        self.gain_display.setText(self.current_gain or "Aucune annonce")

        # Sync Public Window
        if self.public_window:
            self.public_window.update_view(self.drawn_numbers, self.current_gain)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Base propre pour le stylisage
    window = LotoApp()
    window.show()
    sys.exit(app.exec())
