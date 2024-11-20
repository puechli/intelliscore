import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QImage, QPalette, QColor
import numpy as np
import os
from intelliscore.application.setup import (PRIMARY_COLOR, SECONDARY_COLOR, FOLDER_PATH,
                    INITIAL_ZOOM_FACTOR, INITIAL_SCROLL_SPEED,
                    INITIAL_MEASURE_LENGTH, INITIAL_CONTINUOUS_SCROLL_SPEED)


__package__ = "intelliscore"

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
