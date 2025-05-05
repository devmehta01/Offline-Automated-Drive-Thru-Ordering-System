import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

class VoskTranscriber:
    def __init__(self, model_path="models/vosk-model-small-en-us-0.15"):
        self.model = Model(model_path)
        self.samplerate = 16000
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        self.q.put(bytes(indata))

    def transcribe_once(self):
        """Short transcription for things like getting the user's name."""
        recognizer = KaldiRecognizer(self.model, self.samplerate)

        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=self._callback):
            print("Listening...")
            while True:
                data = self.q.get()
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result).get("text", "").strip()
                    if text:
                        return text

    def transcribe_order(self, ui, timeout=3.0):
        """Longer transcription loop that waits until silence."""
        recognizer = KaldiRecognizer(self.model, self.samplerate)
        recognizer.SetWords(True)

        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=self._callback):
            ui.set_status_text("Listening...")
            silence_duration = 0.0
            silence_threshold = 1.0  # seconds of silence to consider speech over

            collected_text = ""
            silence_counter = 0

            while True:
                data = self.q.get()
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result).get("text", "").strip()
                    if text:
                        collected_text += " " + text
                        silence_counter = 0  # reset on speech
                    else:
                        silence_counter += 1
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "")
                    if not partial:
                        silence_counter += 1

                if silence_counter * 0.25 > silence_threshold:
                    break

            ui.set_status_text("Processing...")
            return collected_text.strip()
