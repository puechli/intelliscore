import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QImage, QPalette, QColor
import numpy as np
import os


# Couleurs prédéfinies
PRIMARY_COLOR = "#2C3E50"  # Bleu foncé
SECONDARY_COLOR = "#ECF0F1"  # Gris clair
FOLDER_PATH = "/home/ssidd/Documents/EKOL/GreRasme/CM/projetDeGroup/"
class SheetMusicViewer(QMainWindow):
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
        self.zoom_factor = 1.0
        self.scroll_position = 0
        self.is_scrolling = False
        self.is_key_held = False
        self.scroll_speed = 5
        self.scroll_target = 100
        self.measure_length = 140
        self.continuous_scroll_speed = 4

    def init_ui(self):
        self.setWindowTitle("Visualiseur de Partition")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setup_control_panel()
        self.setup_image_display()
        
    def setup_control_panel(self):
        # Widget de contrôle avec taille minimale
        self.control_widget = QWidget()
        self.control_widget.setMinimumHeight(50)
        self.control_widget.setMaximumHeight(200)
        
        # Layout principal pour le panneau de contrôle
        control_main_layout = QVBoxLayout()
        control_main_layout.setSpacing(0)
        control_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Layout pour le contenu du panneau de contrôle
        self.control_layout = QHBoxLayout()
        self.control_layout.setContentsMargins(10, 5, 10, 5)
        
        # Widget conteneur pour les contrôles avec style transparent
        controls_container = QWidget()
        controls_container.setStyleSheet("border: none;")
        controls_container_layout = QHBoxLayout(controls_container)
        controls_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Création du layout pour tous les contrôles (à gauche)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(5)
        controls_layout.setAlignment(Qt.AlignVCenter)
        
        # Layout horizontal pour la longueur
        length_layout = QHBoxLayout()
        length_label = QLabel("Longueur:")
        length_label.setStyleSheet(f"color: {PRIMARY_COLOR}; border: none;")
        self.length_input = QLineEdit(str(self.measure_length))
        self.length_input.setFixedWidth(50)
        self.length_input.setStyleSheet(self.get_input_style())
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_input)
        length_layout.addStretch()
        
        # Layout horizontal pour la vitesse
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Vitesse:")
        speed_label.setStyleSheet(f"color: {PRIMARY_COLOR}; border: none;")
        self.speed_input = QLineEdit(str(self.continuous_scroll_speed))
        self.speed_input.setFixedWidth(50)
        self.speed_input.setStyleSheet(self.get_input_style())
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_input)
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
        
        # Empiler les contrôles verticalement
        controls_layout.addLayout(length_layout)
        controls_layout.addLayout(speed_layout)
        controls_layout.addLayout(button_layout)
        
        # Ajouter le layout des contrôles avec alignement à gauche
        controls_container_layout.addLayout(controls_layout)
        controls_container_layout.addStretch()
        
        # Widget conteneur pour le logo avec style transparent
        logo_container = QWidget()
        logo_container.setStyleSheet("border: none;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Logo au centre
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("border: none;")
        self.update_logo_size()
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        # Ajouter le logo au layout
        logo_layout.addWidget(self.logo_label)
        
        # Assemblage du layout principal avec des poids
        self.control_layout.addWidget(controls_container, 1)
        self.control_layout.addWidget(logo_container, 2)
        
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
            new_height = max(50, min(200, new_height))
            self.control_widget.setFixedHeight(new_height)
            self.update_logo_size()
            return True
        return False

    def update_logo_size(self):
        """Méthode séparée pour mettre à jour la taille du logo"""
        logo_pixmap = QPixmap(FOLDER_PATH+"intelliscore_logo.png")
        if not logo_pixmap.isNull():
            effective_height = self.control_widget.height() - 10
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
            new_height = max(50, min(200, self.start_height + delta))
            self.parent().setFixedHeight(new_height)
            if hasattr(self.parent(), 'update_logo_size'):
                self.parent().update_logo_size()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = SheetMusicViewer(FOLDER_PATH+"sheet.png")
    sys.exit(app.exec_())
