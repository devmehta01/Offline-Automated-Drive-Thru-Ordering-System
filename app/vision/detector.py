import cv2

class FaceDetector:
    def __init__(self, cascade_path=None):
        if cascade_path is None:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        return faces

    # def show_debug_feed(self):
    #     cap = cv2.VideoCapture(0)
    #     if not cap.isOpened():
    #         raise RuntimeError("Unable to access the webcam.")

    #     print("[INFO] Starting face detection. Press 'q' to quit.")

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break

    #         faces = self.detect_faces(frame)
    #         for (x, y, w, h) in faces:
    #             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #         cv2.imshow("Face Detection", frame)

    #         if cv2.waitKey(1) & 0xFF == ord("q"):
    #             break

    #     cap.release()
    #     cv2.destroyAllWindows()