import cv2
import os
import numpy as np
import uuid
import json
from datetime import datetime

class FaceRecognizer:
    def __init__(self, model_path="trained_model.yml", face_dir="known_faces", metadata_file="known_faces/metadata.json"):
        self.model_path = model_path
        self.face_dir = face_dir
        self.metadata_file = metadata_file
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        os.makedirs(self.face_dir, exist_ok=True)
        self.metadata = self._load_metadata()

        if os.path.exists(model_path):
            self.recognizer.read(model_path)
            self.label_map = self._load_labels()
        else:
            self.label_map = {}
            self._train()

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def _load_labels(self):
        label_path = os.path.join(self.face_dir, "labels.npy")
        if os.path.exists(label_path):
            return dict(np.load(label_path, allow_pickle=True).item())
        return {}

    def _save_labels(self):
        label_path = os.path.join(self.face_dir, "labels.npy")
        np.save(label_path, self.label_map)

    def _train(self):
        print("[INFO] Training LBPH model...")
        images = []
        labels = []
        self.label_map = {}
        current_label = 0

        for uid in os.listdir(self.face_dir):
            person_path = os.path.join(self.face_dir, uid)
            if not os.path.isdir(person_path) or uid == "metadata.json":
                continue

            self.label_map[current_label] = uid

            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    images.append(img)
                    labels.append(current_label)

            current_label += 1

        if not images:
            print("[WARN] No face images found for training.")
            return

        self.recognizer.train(images, np.array(labels))
        self.recognizer.save(self.model_path)
        self._save_labels()
        self._save_metadata()
        print("[INFO] Training complete.")

    def recognize_face(self, gray_face_img):
        if not self.label_map:
            return "Unknown"

        label, confidence = self.recognizer.predict(gray_face_img)
        uid = self.label_map.get(label, None)
        if uid is None or confidence > 70:
            return "Unknown"

        return self.metadata.get(uid, {}).get("name", "Unknown")

    def save_new_face(self, gray_face_img, name):
        uid = str(uuid.uuid4())[:8]
        person_dir = os.path.join(self.face_dir, uid)
        os.makedirs(person_dir, exist_ok=True)

        count = len(os.listdir(person_dir))
        filename = f"img_{count+1}.png"
        img_path = os.path.join(person_dir, filename)
        if not isinstance(gray_face_img, np.ndarray):
            raise ValueError("gray_face_img is not a valid NumPy array")

        if gray_face_img.size == 0:
            raise ValueError("gray_face_img is empty")

        if gray_face_img.ndim != 2 or gray_face_img.dtype != np.uint8:
            try:
                gray_face_img = cv2.cvtColor(gray_face_img, cv2.COLOR_BGR2GRAY)
            except Exception as e:
                raise ValueError(f"Could not convert image to grayscale: {e}")
        cv2.imwrite(img_path, gray_face_img)

        self.metadata[uid] = {
            "name": name,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print(f"[INFO] Saved new face under UID {uid}")
        self._train()  # retrain with new data