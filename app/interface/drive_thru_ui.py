from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextBrowser, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import sys
import json
import os
import cv2

class DriveThruUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drive-Thru Assistant")
        self.showMaximized()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left: Menu Panel
        self.menu_browser = QTextBrowser()
        self.menu_browser.setOpenExternalLinks(False)
        self.menu_browser.setStyleSheet("border: none; font-size: 20px;")
        self.menu_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu_browser.setFixedWidth(500)
        self.menu_browser.setHtml(self.generate_menu_html())

        # Right: Video + Status + Transcription stacked with equal height
        self.video_label = QLabel("Video Feed Here")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #222; color: white; font-size: 18px;")

        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: #e0e0e0; padding: 5px; font-size: 14px;")

        self.transcription_box = QTextEdit()
        self.transcription_box.setReadOnly(True)
        self.transcription_box.setStyleSheet("background-color: #f4f4f4; padding: 10px; font-size: 20px;")

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.video_label, stretch=1)
        right_layout.addWidget(self.status_label, stretch=0)
        right_layout.addWidget(self.transcription_box, stretch=1)

        # Final layout structure
        main_layout.addWidget(self.menu_browser, stretch=0)
        main_layout.addLayout(right_layout, stretch=1)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

    def generate_menu_html(self):
        menu_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'menu.json')
        with open(menu_path, 'r') as f:
            menu_data = json.load(f)

        html = '<h2 style="text-align:center;">Menu</h2>'
        for section, items in menu_data.items():
            html += f'<h3 style="margin-top:15px;">{section}</h3>'
            html += '<table cellpadding="10">'
            for item in items:
                name = item.get("name", "")
                price = item.get("price", "")
                image_path = os.path.abspath(item.get("image", ""))
                image_url = f"file:///{image_path.replace(os.sep, '/')}"
                html += f'''
                    <tr>
                      <td><img src="{image_url}" width="60"></td>
                      <td><b>{name}</b><br>${price:.2f}</td>
                    </tr>
                '''
            html += '</table>'
        return html

    def set_video_frame(self, frame):
        if not self.video_label or not self.video_label.size().isValid():
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    def set_status_text(self, text):
        color_map = {
            "Idle": ("#888888", "#FFFFFF"),
            "Listening...": ("#007BFF", "#FFFFFF"),
            "Processing...": ("#FFA500", "#000000"),
            "Completed": ("#28A745", "#FFFFFF")
        }
        bg_color, text_color = color_map.get(text, ("#444444", "#FFFFFF"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"background-color: {bg_color}; color: {text_color}; padding: 6px; font-size: 14px;"
        )

    def append_transcription(self, text):
        self.transcription_box.append(text)

if __name__ == '__main__':
    print("Run main.py instead to start the full application.")
