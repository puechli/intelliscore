import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QGroupBox, 
                            QFormLayout, QSlider, QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QImage, QPalette, QColor
import numpy as np
import os
from intelliscore.application.setup import (PRIMARY_COLOR, SECONDARY_COLOR, FOLDER_PATH,
                    INITIAL_ZOOM_FACTOR, INITIAL_SCROLL_SPEED,
                    INITIAL_MEASURE_LENGTH, INITIAL_CONTINUOUS_SCROLL_SPEED)

__package__ = "intelliscore"

class SheetMusicViewer(QMainWindow):
    from intelliscore.application.resize_handle import ResizeHandle

    def __init__(self, image_path):
        super().__init__()
        self.init_variables(image_path)
        self.init_ui()
        self.setup_timers()
        self.apply_styles()
        
        self.show()
        self.resize(800, 600)

    def init_variables(self, image_path):
        self.image_path = image_path
        self.zoom_factor = INITIAL_ZOOM_FACTOR
        self.scroll_position = 0
        self.is_scrolling = False
        self.is_key_held = False
        self.scroll_speed = INITIAL_SCROLL_SPEED
        self.scroll_target = 100
        self.measure_length = INITIAL_MEASURE_LENGTH
        self.continuous_scroll_speed = INITIAL_CONTINUOUS_SCROLL_SPEED

    def init_ui(self):
        self.setWindowTitle("Visualiseur de Partition")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Setup Advanced Menu
        self.setup_advanced_menu()
        
        # Other UI components...
        self.setup_image_display()
        
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.show()
        
    def setup_advanced_menu(self):
        # Button to toggle the advanced settings
        self.advanced_button = QPushButton("Show Advanced Settings")
        self.advanced_button.setCheckable(True)
        self.advanced_button.clicked.connect(self.toggle_advanced_menu)
        self.main_layout.addWidget(self.advanced_button)

        # Advanced settings layout
        self.advanced_layout = QFormLayout()
        
        # Zoom Factor
        self.zoom_factor_input = QSpinBox()
        self.zoom_factor_input.setRange(1, 10)
        self.zoom_factor_input.setValue(int(self.zoom_factor))
        self.zoom_factor_input.valueChanged.connect(self.update_zoom_factor)
        self.advanced_layout.addRow("Zoom Factor:", self.zoom_factor_input)

        # Scroll Speed
        self.scroll_speed_input = QSpinBox()
        self.scroll_speed_input.setRange(1, 20)
        self.scroll_speed_input.setValue(self.scroll_speed)
        self.scroll_speed_input.valueChanged.connect(self.update_scroll_speed)
        self.advanced_layout.addRow("Scroll Speed:", self.scroll_speed_input)

        # Measure Length
        self.measure_length_input = QSpinBox()
        self.measure_length_input.setRange(1, 500)
        self.measure_length_input.setValue(self.measure_length)
        self.measure_length_input.valueChanged.connect(self.update_measure_length)
        self.advanced_layout.addRow("Measure Length:", self.measure_length_input)

        # Continuous Scroll Speed
        self.continuous_scroll_speed_input = QSpinBox()
        self.continuous_scroll_speed_input.setRange(1, 20)
        self.continuous_scroll_speed_input.setValue(self.continuous_scroll_speed)
        self.continuous_scroll_speed_input.valueChanged.connect(self.update_continuous_scroll_speed)
        self.advanced_layout.addRow("Continuous Scroll Speed:", self.continuous_scroll_speed_input)

        # Checkbox for enabling/disabling some feature
        self.enable_feature_checkbox = QCheckBox("Enable Feature X")
        self.enable_feature_checkbox.setChecked(False)
        self.advanced_layout.addRow(self.enable_feature_checkbox)

        # Create a widget to hold the advanced settings
        self.advanced_widget = QWidget()
        self.advanced_widget.setLayout(self.advanced_layout)
        self.advanced_widget.setVisible(False)  # Start hidden
        self.advanced_widget.setMaximumWidth(300)  # Set maximum width
        self.main_layout.addWidget(self.advanced_widget)

    def toggle_advanced_menu(self):
        # Toggle the visibility of the advanced settings
        is_checked = self.advanced_button.isChecked()
        self.advanced_widget.setVisible(is_checked)
        self.advanced_button.setText("Hide Advanced Settings" if is_checked else "Show Advanced Settings")

    def update_zoom_factor(self, value):
        self.zoom_factor = value
        print(f"Zoom factor updated to: {self.zoom_factor}")

    def update_scroll_speed(self, value):
        self.scroll_speed = value
        print(f"Scroll speed updated to: {self.scroll_speed}")

    def update_measure_length(self, value):
        self.measure_length = value
        print(f"Measure length updated to: {self.measure_length}")

    def update_continuous_scroll_speed(self, value):
        self.continuous_scroll_speed = value
        print(f"Continuous scroll speed updated to: {self.continuous_scroll_speed}")

    def setup_image_display(self):
        # Création d'un QScrollArea pour les barres de défilement
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setStyleSheet(f"background-color: {SECONDARY_COLOR};")
        
        # Connecter le signal de défilement horizontal
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.on_horizontal_scroll)
        
        # Chargement et affichage de l'image
        self.current_image = QPixmap(self.image_path)
        if self.current_image.isNull():
            raise Exception(f"Impossible de charger l'image: {self.image_path}")
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.image_label.setStyleSheet(f"background-color: {SECONDARY_COLOR};")
        self.image_label.setFocusPolicy(Qt.StrongFocus)
        
        # Ajouter le label à la zone de défilement
        self.scroll_area.setWidget(self.image_label)
        self.main_layout.addWidget(self.scroll_area)
        self.update_view()

    def on_horizontal_scroll(self, value):
        """Gestionnaire d'événements pour le défilement horizontal manuel"""
        if not self.is_scrolling:  # Ne pas interférer avec le défilement automatique
            self.scroll_position = value
            # Pas besoin d'appeler update_view() car le QScrollArea gère déjà l'affichage

    def setup_timers(self):
        # Timer pour l'animation de défilement
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_scroll)
        self.scroll_timer.setInterval(16)
        
        # Timer pour le défilement continu
        self.continuous_timer = QTimer()
        self.continuous_timer.timeout.connect(self.continuous_scroll)
        self.continuous_timer.setInterval(16)

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {SECONDARY_COLOR};
            }}
            QWidget {{
                background-color: {SECONDARY_COLOR};
            }}
        """)

    @staticmethod
    def get_button_style():
        return f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: {SECONDARY_COLOR};
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #34495E;
            }}
        """

    @staticmethod
    def get_input_style():
        return f"""
            QLineEdit {{
                background-color: white;
                border: 1px solid {PRIMARY_COLOR};
                padding: 3px;
                border-radius: 3px;
            }}
        """

    def update_all_values(self):
        """Met à jour à la fois la longueur et la vitesse"""
        # Mise à jour de la longueur
        try:
            new_length = int(self.length_input.text())
            if new_length > 0:
                self.measure_length = new_length
            else:
                self.length_input.setText(str(self.measure_length))
        except ValueError:
            self.length_input.setText(str(self.measure_length))

        # Mise à jour de la vitesse
        try:
            new_speed = float(self.speed_input.text())
            if new_speed > 0:
                self.continuous_scroll_speed = new_speed
            else:
                self.speed_input.setText(str(self.continuous_scroll_speed))
        except ValueError:
            self.speed_input.setText(str(self.continuous_scroll_speed))

        # Remettre le focus sur l'image_label
        self.image_label.setFocus()

    def update_view(self):
        # Conversion en entiers pour la méthode scaled()
        new_width = int(self.current_image.width() * self.zoom_factor)
        new_height = int(self.current_image.height() * self.zoom_factor)
        
        scaled_pixmap = self.current_image.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Mettre à jour directement le pixmap sans décalage
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
        
        # Mettre à jour la position horizontale du scroll
        if not self.is_scrolling:  # Seulement si pas en défilement automatique
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_position)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Obtenir la position relative dans l'image
            pos = self.image_label.mapFrom(self, event.pos())
            # Calculer le ratio vertical pour le zoom
            vertical_ratio = pos.y() / self.image_label.height()
            
            old_height = self.image_label.height()
            # Zoom in
            self.zoom_factor *= 1.2
            self.update_view()
            
            # Ajuster le défilement vertical pour zoomer sur le point cliqué
            new_height = self.image_label.height()
            new_scroll_pos = int(vertical_ratio * new_height - event.pos().y())
            self.scroll_area.verticalScrollBar().setValue(new_scroll_pos)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if not event.isAutoRepeat():  # Éviter les répétitions automatiques
                if not self.is_scrolling and not self.is_key_held:
                    # Démarrer le défilement initial
                    self.is_scrolling = True
                    self.scroll_start = self.scroll_position
                    self.scroll_target = self.scroll_position + int(self.measure_length * self.zoom_factor)
                    self.scroll_progress = 0
                    self.scroll_timer.start()
                    # Activer le mode continu
                    self.is_key_held = True
                    self.continuous_timer.start()
        elif event.key() == Qt.Key_Escape:
            self.zoom_factor = 1.0
            self.scroll_position = 0
            self.update_view()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.is_key_held = False
            self.continuous_timer.stop()

    def continuous_scroll(self):
        if self.is_key_held and not self.is_scrolling:
            # Défilement linéaire continu
            self.scroll_position += int(self.continuous_scroll_speed * self.zoom_factor)
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_position)

    def update_scroll(self):
        if self.is_scrolling:
            self.scroll_progress += 0.01 * self.scroll_speed
            if self.scroll_progress >= 1:
                self.is_scrolling = False
                self.scroll_timer.stop()
                self.scroll_position = self.scroll_target
            else:
                # Animation fluide avec easing
                t = np.sin(self.scroll_progress * np.pi / 2)
                self.scroll_position = int(
                    self.scroll_start + (self.scroll_target - self.scroll_start) * t
                )
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_position)

    def resizeEvent(self, event):
        """Gérer le redimensionnement de la fenêtre"""
        super().resizeEvent(event)
        # Mettre à jour uniquement la taille du logo
        self.update_logo_size()
