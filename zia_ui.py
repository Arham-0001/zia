from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush
import math


class ZiaUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZIA - Voice Assistant")
        self.setGeometry(500, 200, 400, 400)
        self.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                           "stop:0 #1f1c2c, stop:1 #928DAB);")

        # ZIA Text
        self.label = QLabel("ZIA", self)
        self.label.setFont(QFont("Arial", 36, QFont.Bold))
        self.label.setStyleSheet("color: white;")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        # Animation variables
        self.mode = "idle"  # idle | listening | speaking
        self.radius = 50
        self.grow = True

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        if self.mode in ["listening", "speaking"]:
            if self.grow:
                self.radius += 2
                if self.radius >= 80:
                    self.grow = False
            else:
                self.radius -= 2
                if self.radius <= 50:
                    self.grow = True
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.mode == "listening":
            painter.setBrush(QBrush(QColor(0, 150, 255, 120)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.width()//2 - self.radius,
                                self.height()//2 - self.radius,
                                self.radius*2, self.radius*2)

        elif self.mode == "speaking":
            painter.setBrush(QBrush(QColor(0, 255, 120, 120)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.width()//2 - self.radius,
                                self.height()//2 - self.radius,
                                self.radius*2, self.radius*2)

    def show_idle(self):
        self.mode = "idle"
        self.update()

    def show_listening(self):
        self.mode = "listening"
        self.update()

    def show_speaking(self):
        self.mode = "speaking"
        self.update()
