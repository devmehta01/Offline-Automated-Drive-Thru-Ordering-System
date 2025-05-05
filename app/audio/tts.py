import pyttsx3
import threading
import queue

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 1.0)

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def speak(self, text: str):
        self.queue.put(text)

    def _process_queue(self):
        while True:
            text = self.queue.get()
            self.engine.say(text)
            self.engine.runAndWait()

    def speak_blocking(self, text: str):
        done = threading.Event()

        def wrapped():
            self.engine.say(text)
            self.engine.runAndWait()
            done.set()

        threading.Thread(target=wrapped, daemon=True).start()
        done.wait()
