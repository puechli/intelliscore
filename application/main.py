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

FOLDER_PATH = "/home/ssidd/Documents/EKOL/GreRasme/CM/projetDeGroup/"



if __name__ == "__main__":

    from intelliscore.application.viewer import SheetMusicViewer
    app = QApplication(sys.argv)
    viewer = SheetMusicViewer(FOLDER_PATH+"sheet.png")
    sys.exit(app.exec_())
