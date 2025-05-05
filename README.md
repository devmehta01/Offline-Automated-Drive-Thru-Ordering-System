# 🧠 Automated Drive-Thru Assistant

This project presents a comprehensive offline, AI-driven drive-thru ordering system, integrating real-time facial recognition, automated speech processing, and natural language understanding for a fully autonomous customer experience.

---

## 🚀 Key Capabilities

- 🎥 **Facial Detection and Recognition** — Leverages OpenCV-based algorithms to identify and greet users personally, facilitating user-specific interactions.
- 😤 **Offline Automatic Speech Recognition (ASR)** — Employs [Vosk](https://github.com/alphacep/vosk-api) for low-latency speech transcription independent of internet connectivity.
- 💬 **Local LLM-Based Semantic Parsing** — Utilizes [Mistral](https://ollama.com/) via Ollama to convert natural language input into structured, JSON-based order intents.
- 🗞️ **Contextual Multi-Turn Dialogue Management** — Enables real-time updates, cancellations, and confirmations across a sustained conversational session.
- 📢 **Synthetic Speech Output** — Delivers dynamic verbal feedback through `pyttsx3` to simulate human-agent interaction.
- 🖼️ **GUI with PyQt5** — Presents a full-screen user interface comprising a dynamic menu display, live video feed with annotations, a transcription window, and session status bar.
- 💵 **Dynamic Menu Integration and Pricing Computation** — Ingests a structured JSON menu, displaying categorized items with images and calculating real-time order totals.
- ♻️ **Autonomous Session Lifecycle Management** — Automatically resets the interface and state following user departure, based on persistent absence detection.

---

## 📸 Demonstration

> _Coming soon_: A walkthrough video or animated showcase.

---

## 📂 Directory Layout

```
Automated_Drive_Thru/
│
├── app/
│   ├── audio/           # Modules for speech recognition and synthesis
│   ├── data/            # Structured configuration and content data
│   ├── interface/       # GUI definition using PyQt5
│   ├── nlp/             # LLM interface and query abstraction
│   ├── order/           # Order modeling and management logic
│   ├── utils/           # Utility scripts and helpers
│   ├── assets/          # Visual resources (e.g., menu item images)
│   └── vision/          # Face detection and recognition layers
│
├── known_faces/         # Persisted user facial embeddings
├── models/              # Local speech recognition model files
├── main.py              # Application entry point
└── requirements.txt     # Python dependency list
```

---

## 🛠️ System Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com) for local LLM deployment
- Package installation:

```bash
pip install -r requirements.txt
```

---

## 🧠 Core Models Employed

- **Facial Recognition**: OpenCV LBPH algorithm trained on local face samples
- **ASR**: Vosk Small English model (fully offline)
- **Language Model**: Mistral via Ollama
- **TTS Engine**: pyttsx3 for platform-native speech synthesis

---

## 📂 Execution Guide

```bash
# Step 1: Initialize local LLM
ollama run mistral

# Step 2: Launch the application
python main.py
```

> Ensure the appropriate Vosk model is located in the `models/` directory and `menu.json` is well-formed.

---

## 📌 Potential Extensions

- 🗞️ Persist user receipts as local files
- 🧠 Introduce order recommendation based on historical trends
- 🌐 Develop web-based interface with FastAPI and WebRTC
- 🧪 Incorporate modular testing suites for key components

---

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License**.  
You may view and use this code for personal or educational purposes, but **commercial use is strictly prohibited**.