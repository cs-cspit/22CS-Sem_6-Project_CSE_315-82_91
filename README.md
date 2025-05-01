# 22CS-Sem_6-Project_CSE_315-82_91

# 🚗 Vehicle Monitoring System

The **Vehicle Monitoring System** is a web-based application that allows users to upload a video and receive insights such as vehicle count by type, number plate detection, and traffic congestion visualization. This system uses YOLOv8 for vehicle detection and EasyOCR for number plate recognition. # 🚦 Vehicle Monitoring System

An AI-powered web-based system to monitor traffic, detect vehicles, recognize number plates, and simulate dynamic traffic signal control for smarter urban mobility.

---

## 👨‍💻 Team Members

- Shreya Vekariya (22CS091)
- Yashvi Suvariya (22CS082)

---

## ❓ Problem Statement

Traditional traffic systems rely on fixed timers and manual monitoring, resulting in:
- Inefficient traffic flow
- Increased delays and fuel wastage
- Lack of real-time adaptive response

---

## 🎯 Project Objectives

- 🔍 Vehicle Detection and Counting using YOLOv8n
- 🔢 Number Plate Recognition via OCR
- 🚦 Dynamic Signal Simulation for Traffic Control
- 🌐 Web-based Frontend and ML Integration
- 📉 Optimize flow, reduce congestion and emissions

---

---

## 🧠 Features

- Upload video for analysis  
- Vehicle detection using YOLOv8  
- Vehicle type-wise counting (car, bus, bike, etc.)  
- Number plate detection using EasyOCR  
- Output annotated video for download  
- Efficient traffic simulation using Pygame  
- Frontend-Backend integrated with FastAPI

---

## 🛠 Tech Stack

- **Frontend**: React.js  
- **Backend**: FastAPI (Python)  
- **Machine Learning**: YOLOv8, EasyOCR  
- **Simulation**: Pygame  
- **Deployment**: Localhost  

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### 1️⃣ Clone the Repository

### 2️⃣ Run the Frontend

```bash
cd frontend
npm install
npm start
```

The React app will start on `http://localhost:3000`.

### 3️⃣ Run the Backend

In a **new terminal** window:

```bash
cd backend
python server.py
```

The backend server will run on `http://localhost:8000`.

---

---

## 📷 Sample Output

- ✅ Annotated video with vehicle count overlay  
- ✅ Number plates marked and extracted  
- ✅ Dynamic traffic simulation via Pygame

---

