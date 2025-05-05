import sys
import cv2
import threading
import numpy as np
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
import json

from app.interface.drive_thru_ui import DriveThruUI
from app.vision.detector import FaceDetector
from app.vision.recognizer import FaceRecognizer
from app.audio.tts import TextToSpeech
from app.audio.transcriber import VoskTranscriber
from app.nlp.llm_engine import LlmEngine
from app.order.order_session import OrderSession

class DriveThruApp(QObject):
    start_order_session = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.ui = DriveThruUI()
        self.ui.show()

        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.tts = TextToSpeech()
        self.transcriber = VoskTranscriber(model_path="models/vosk-model-small-en-us-0.15")
        self.llm_engine = LlmEngine()
        self.order_session = OrderSession()

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(30)

        self.last_greeted_name = None
        self.last_greeted_time = 0
        self.registering = False
        self.face_absent_frames = 0
        self.reset_triggered = False

        self.start_order_session.connect(self.handle_order_session)

    def handle_unknown_face(self, face_crop):
        self.tts.speak_blocking("Welcome. Please state your name.")
        spoken_name = self.transcriber.transcribe_once()
        if spoken_name:
            self.recognizer.save_new_face(face_crop, spoken_name)
            self.tts.speak(f"Thank you {spoken_name}, you are now registered.")
            self.last_greeted_name = spoken_name
            self.last_greeted_time = time.time()
            self.recognizer._train()
            QTimer.singleShot(2500, lambda: self.start_order_session.emit())
        self.registering = False

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        face_boxes = self.detector.detect_faces(frame)

        if len(face_boxes) == 0:
            self.face_absent_frames += 1
        else:
            self.face_absent_frames = 0
        
        if self.face_absent_frames >= 60 and not self.reset_triggered:
            self.reset_session()

        for (x, y, w, h) in face_boxes:
            face_crop = frame[y:y + h, x:x + w]
            gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            resized_crop = cv2.resize(gray_crop, (200, 200))
            name = self.recognizer.recognize_face(resized_crop)

            current_time = time.time()
            cooldown_seconds = 5

            if name != self.last_greeted_name:
                if name == "Unknown" and not self.registering:
                    self.registering = True
                    resized_crop_copy = np.array(resized_crop, dtype=np.uint8).copy()
                    threading.Thread(target=self.handle_unknown_face, args=(resized_crop_copy,), daemon=True).start()
                elif name != "Unknown" and current_time - self.last_greeted_time > cooldown_seconds:
                    self.last_greeted_name = name
                    self.last_greeted_time = current_time

                    def greet_and_start_session(name):
                        self.tts.speak_blocking(f"Welcome back, {name}!")
                        self.start_order_session.emit()

                    threading.Thread(target=greet_and_start_session, args=(name,), daemon=True).start()

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        self.ui.set_video_frame(frame)
    
    def reset_session(self):
        print("[INFO] Resetting session for next customer")
        self.reset_triggered = True
        self.order_session.items = []
        self.last_greeted_name = None
        self.face_absent_frames = 0
        self.ui.transcription_box.clear()
        self.ui.set_status_text("Idle")
        QTimer.singleshot(500, lambda: setattr(self, 'reset_triggered', False))

    def run(self):
        sys.exit(self.app.exec_())

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

    def handle_order_session(self):
        threading.Thread(target=self.order_session_worker, daemon=True).start()

    def order_session_worker(self):
        self.tts.speak_blocking("Please place your order now.")

        while True:
            QTimer.singleShot(0, lambda: self.ui.set_status_text("Listening..."))
            customer_input = self.transcriber.transcribe_order(self.ui)
            print(f"Customer said: {customer_input}")

            if not customer_input.strip():
                continue

            QTimer.singleShot(0, lambda: self.ui.set_status_text("Processing..."))
            self.ui.append_transcription(f"Customer: {customer_input}")
            self.ui.transcription_box.moveCursor(self.ui.transcription_box.textCursor().End)

            if any(phrase in customer_input.lower() for phrase in ["confirm", "done", "that's all", "complete", "finish"]):
                print("Customer confirmed the order.")
                QTimer.singleShot(0, lambda: self.ui.set_status_text("Idle"))
                break

            response = self.llm_engine.parse_order(
                order_text=customer_input,
                current_order=self.order_session.get_current_order_json()
            )

            try:
                parsed = json.loads(response)
                self.order_session.update_from_llm(parsed)
                order_summary = self.order_session.get_current_order_pretty()
                self.ui.append_transcription(f"Order so far:\n{order_summary}")
                self.ui.transcription_box.moveCursor(self.ui.transcription_box.textCursor().End)
            except Exception as e:
                print(f"⚠️ Error parsing LLM response: {e}")
                continue

            self.tts.speak_blocking("Do you need anything else? If not, please say 'I am done.'")

        final_order_text = self.order_session.get_current_order_pretty()
        self.ui.transcription_box.append("\nFinal Order:")
        self.ui.transcription_box.append(final_order_text)
        self.ui.transcription_box.moveCursor(self.ui.transcription_box.textCursor().End)
        self.ui.set_status_text("Completed")
        print("\nFinal Order:\n", final_order_text)
