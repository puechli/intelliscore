import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                            QScrollArea, QSpinBox, QCheckBox, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QImage, QPalette, QColor
import numpy as np
import os

# Couleurs prédéfinies
PRIMARY_COLOR = "#2C3E50"  # Bleu foncé
SECONDARY_COLOR = "#ECF0F1"  # Gris clair

# Chemin du dossier
FOLDER_PATH = "/home/ssidd/Documents/EKOL/GreRasme/CM/projetDeGroup/"

# Variables d'initialisation pour SheetMusicViewer
INITIAL_ZOOM_FACTOR = 1.0
INITIAL_SCROLL_SPEED = 5
INITIAL_MEASURE_LENGTH = 140
INITIAL_CONTINUOUS_SCROLL_SPEED = 4

# Variables d'initialisation pour SheetMusicViewer
INITIAL_ZOOM_FACTOR = 1.0
INITIAL_SCROLL_SPEED = 5
INITIAL_MEASURE_LENGTH = 140
INITIAL_CONTINUOUS_SCROLL_SPEED = 4

CONTROL_PANEL_MAX_HEIGHT= 300

class SheetMusicViewer(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.init_variables(image_path)
        self.init_ui()
        self.setup_timers()
        self.apply_styles()
        
        self.show()
        self.resize(1200, 900)

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
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setup_control_panel()
        self.setup_image_display()
        
    def setup_control_panel(self):
        self.active_variables = []
        # Widget de contrôle avec taille minimale
        self.control_widget = QWidget()
        self.control_widget.setMinimumHeight(50)
        self.control_widget.setMaximumHeight(CONTROL_PANEL_MAX_HEIGHT)
        
        # Layout principal pour le panneau de contrôle
        control_main_layout = QVBoxLayout()
        control_main_layout.setSpacing(0)
        control_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Layout pour le contenu du panneau de contrôle
        self.control_layout = QHBoxLayout()
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget conteneur pour les contrôles avec style transparent
        controls_container = QWidget()
        controls_container.setStyleSheet("border: none;")
        controls_container_layout = QVBoxLayout(controls_container)
        controls_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Création du layout pour tous les contrôles (à gauche)
        controls_layout = QVBoxLayout()
        
        # Layout horizontal pour la longueur
        length_layout = self.add_spinbox("measure_length", self.measure_length,  rangemin=50, rangemax=300, stepsize=30)
        length_layout.addStretch()
        
        speed_layout = self.add_spinbox("continuous_scroll_speed", self.continuous_scroll_speed, rangemax=20)
        # Layout horizontal pour la vitesse
        speed_layout.addStretch()
        
        # Bouton Update
        update_button = QPushButton("Update")
        update_button.setFixedWidth(70)
        update_button.clicked.connect(self.update_all_values)
        update_button.setStyleSheet(self.get_button_style())
        
        # Layout pour le bouton
        button_layout = QHBoxLayout()
        button_layout.addWidget(update_button)
        button_layout.addStretch()
        
        self.setup_advanced_menu()
        
        # Empiler les contrôles verticalement
        controls_layout.addLayout(length_layout)
        controls_layout.addLayout(speed_layout)

        for  widget, layout, input, function, _ in self.advanced_variables:
            controls_layout.addLayout(layout)
        # Ajouter le layout des contrôles avec alignement à gauche
        controls_container_layout.addLayout(controls_layout)
        controls_container_layout.addLayout(self.advanced_button_layout)
        controls_container_layout.addLayout(button_layout)
        controls_container_layout.addStretch()
        
        # Widget conteneur pour le logo avec style transparent
        logo_container = QWidget()
        logo_container.setStyleSheet("border: none;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignTop)

        
        # Logo au centre
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("border: none;")
        self.update_logo_size()
        self.logo_label.setAlignment(Qt.AlignTop)
        
        # Ajouter le logo au layout
        logo_layout.addWidget(self.logo_label)
        
        # different modes
        mode_selection_menu = QComboBox()
        mode_selection_menu_layout = QVBoxLayout(mode_selection_menu)
        mode_selection_menu_layout.setAlignment(Qt.AlignTop)
        mode_selection_menu.setMaximumWidth(100)
        mode_selection_menu.addItems(["Mode 1", "Mode 2", "Mode 3"])  # Add your modes here

        
        # Assemblage du layout principal avec des poids
        self.control_layout.addWidget(controls_container, 1)
        self.control_layout.addWidget(logo_container, 2)
        self.control_layout.addWidget(mode_selection_menu, 3)
        

        # Créer un widget conteneur pour le contenu
        content_widget = QWidget()
        content_widget.setLayout(self.control_layout)

        
        # Ajouter le contenu et la poignée de redimensionnement
        control_main_layout.addWidget(content_widget)
        control_main_layout.addWidget(ResizeHandle(self.control_widget))
        
        self.control_widget.setLayout(control_main_layout)
        self.main_layout.addWidget(self.control_widget)
        
        # Style pour le panneau de contrôle principal uniquement
        self.control_widget.setStyleSheet("""
            QWidget#control_widget {
                border-bottom: 2px solid #2C3E50;
                padding: 0px;
                margin: 0px;
            }
        """)
        self.control_widget.setObjectName("control_widget")
        self.control_widget.setProperty("resize", False)
        
        # Configuration des événements de redimensionnement
        self.control_widget.installEventFilter(self)
        self.is_resizing = False
        self.resize_area_height = 10

    def setup_advanced_menu(self):

        # Button to toggle the advanced settings
        self.advanced_button = QPushButton("Advanced Settings")
        self.advanced_button.setCheckable(True)
        self.advanced_button.clicked.connect(self.toggle_advanced_menu)
        self.advanced_button.setMaximumWidth(150)
        self.advanced_button.setStyleSheet(self.get_button_style())
        self.advanced_button_layout = QVBoxLayout()
        self.advanced_button_layout.addWidget(self.advanced_button)

        # Advanced settings layout
        self.advanced_layout = QFormLayout()
        self.advanced_variables = []

        # Zoom Factor
        self.add_spinbox("zoom_factor", self.zoom_factor, advanced=True)
        # Scroll Speed
        self.add_spinbox("scroll_speed", self.scroll_speed, advanced=True)

        # Checkbox for enabling/disabling some feature
        self.enable_feature_checkbox = QCheckBox("Enable Feature X")
        self.enable_feature_checkbox.setChecked(False)
        # self.enable_feature_checkbox.connectNotify(self.enable_feature_checkboxChanged)
        # self.advanced_variables.append([self.enable_feature_checkbox,self.enable_feature_checkbox.connectNotify(self.enable_feature_checkboxChanged)])

    def add_spinbox(self, name, variable, rangemin=1, rangemax=10, stepsize=1, maxwidth=100, advanced=False):
        label = QLabel(name +":")
        label.setStyleSheet(f"color: {PRIMARY_COLOR}; border: none;")
        
        input_field = QLineEdit(str(variable))
        input_field.setMaximumWidth(maxwidth)
        input_field.setStyleSheet(self.get_input_style())

        def update_function():
            value = float(input_field.text())
            if value < rangemin:
                value = rangemin
            elif value > rangemax:
                value = rangemax
            input_field.setText(str(value))
            setattr(self, name, value)
            

        def increment_value():
            value = float(input_field.text())
            value += stepsize
            if value > rangemax:
                value = rangemax
            input_field.setText(str(value))
            setattr(self, name, value)
            self.image_label.setFocus()
        def decrement_value():
            value = float(input_field.text())
            value -= stepsize
            if value < rangemin:
                value = rangemin
            input_field.setText(str(value))
            setattr(self, name, value)
            self.image_label.setFocus()

        # Create increment button
        increment_button = QPushButton(">")  
        increment_button.clicked.connect(increment_value)
        increment_button.setMaximumWidth(20)
        increment_button.setStyleSheet(self.get_button_style())
        
        # Create decrement button
        decrement_button = QPushButton("<")  
        decrement_button.clicked.connect(decrement_value)
        decrement_button.setMaximumWidth(20)
        decrement_button.setStyleSheet(self.get_button_style())

        layout=QHBoxLayout()

        layout.addWidget(label)
        layout.addWidget(decrement_button)
        layout.addWidget(input_field)
        layout.addWidget(increment_button)

        def visibility_function(is_checked):
            label.setVisible(is_checked)
            decrement_button.setVisible(is_checked)
            input_field.setVisible(is_checked)
            increment_button.setVisible(is_checked)

        self.active_variables.append([label, layout, input_field, update_function])
        if advanced:
            label.setVisible(False)
            decrement_button.setVisible(False)
            input_field.setVisible(False)
            increment_button.setVisible(False)
            self.advanced_variables.append([label, layout, input_field, update_function, visibility_function])
        return layout

    def toggle_advanced_menu(self):
        # Toggle the visibility of the advanced settings
        is_checked = self.advanced_button.isChecked()
        for label, layout, input, function, visibilityfunction in self.advanced_variables:
            visibilityfunction(is_checked)

    def eventFilter(self, obj, event):
        """Filtre d'événements pour gérer le curseur et le redimensionnement"""
        if obj == self.control_widget:
            if event.type() == event.MouseMove:
                if self.is_resizing:
                    self.do_resize(event)
                else:
                    # Vérifier si la souris est dans la zone de redimensionnement
                    cursor_pos = event.pos()
                    if cursor_pos.y() > (self.control_widget.height() - self.resize_area_height):
                        self.control_widget.setCursor(Qt.SizeVerCursor)
                    else:
                        self.control_widget.setCursor(Qt.ArrowCursor)
                return True
                    
            elif event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                if event.pos().y() > (self.control_widget.height() - self.resize_area_height):
                    self.is_resizing = True
                    self.resize_start_y = event.globalY()
                    self.resize_start_height = self.control_widget.height()
                    return True
                    
            elif event.type() == event.MouseButtonRelease:
                if self.is_resizing:
                    self.is_resizing = False
                    return True
                
        return super().eventFilter(obj, event)

    def do_resize(self, event):
        """Effectue le redimensionnement"""
        if self.is_resizing:
            new_height = self.resize_start_height + (event.globalY() - self.resize_start_y)
            new_height = max(50, min(CONTROL_PANEL_MAX_HEIGHT, new_height))
            self.control_widget.setFixedHeight(new_height)
            self.update_logo_size()
            return True
        return False

    def update_logo_size(self):
        """Méthode séparée pour mettre à jour la taille du logo"""
        logo_pixmap = QPixmap(FOLDER_PATH+"intelliscore_logo.png")
        if not logo_pixmap.isNull():
            effective_height = self.control_widget.height()
            max_width = self.width() // 3 * 2
            
            scaled_logo = logo_pixmap.scaled(
                max_width,
                effective_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled_logo)
            self.logo_label.setMaximumWidth(max_width)

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
        for _, _, input_field, update_function in self.active_variables:
            try: 
                update_function()
            except ValueError:
                print(f"Invalid input for {input_field}: {input_field.text()}")

        if self.advanced_button.isChecked():
            for _, _, input_field, update_function,_ in self.advanced_variables:
                try:
                    update_function()
                except ValueError:
                    print(f"Invalid input for {input_field}: {input_field.text()}")
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

class ResizeHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(10)  # Hauteur de la zone de redimensionnement
        self.setCursor(Qt.SizeVerCursor)  # Curseur de redimensionnement par défaut
        self.is_resizing = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(SECONDARY_COLOR))
        painter.setPen(QColor(PRIMARY_COLOR))
        painter.drawLine(0, 0, self.width(), 0)  # Ligne supérieure
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_resizing = True
            self.start_y = event.globalY()
            self.start_height = self.parent().height()
            
    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        
    def mouseMoveEvent(self, event):
        if self.is_resizing:
            delta = event.globalY() - self.start_y
            new_height = max(50, min(CONTROL_PANEL_MAX_HEIGHT, self.start_height + delta))
            self.parent().setFixedHeight(new_height)
            viewer.update_logo_size()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = SheetMusicViewer(FOLDER_PATH+"sheet.png")
    sys.exit(app.exec_())
