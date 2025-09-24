# Face Recognition Attendance System 🎯

An AI-powered attendance management system using face recognition technology built with Python, OpenCV, and face_recognition library.

## 🌟 Features

- **Real-time Face Recognition**: Live camera feed with instant face detection and recognition
- **Automated Attendance Tracking**: Automatically marks attendance as Present/Absent
- **User Registration**: Easy registration of new users with photo capture
- **Attendance Management**: View, edit, and export attendance records
- **Privacy Protection**: Secure handling of biometric data
- **Export Functionality**: Export attendance to CSV files
- **Smart Detection**: Configurable absence threshold and confidence levels

## 🛠️ Technologies Used

- **Python 3.7+** - Main programming language
- **OpenCV (cv2)** - Computer vision and camera operations
- **face_recognition** - Face detection and recognition
- **tkinter** - GUI interface
- **dlib** - Face encoding and detection models
- **pickle** - Data serialization for face encodings

## 📋 Prerequisites

- Python 3.7 (recommended for compatibility with provided dlib wheel)
- Webcam/Camera
- Windows OS (for the provided dlib wheel file)

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Teddy-Jul/Face-Recognition-Attendance-System.git
   cd Face-Recognition-Attendance-System
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   py -3.7 -m venv myvenv37
   .\myvenv37\Scripts\Activate.ps1
   ```

3. **Install required packages:**
   ```bash
   pip install opencv-python
   pip install face_recognition
   pip install cmake==3.25.2
   pip install dlib-19.19.0-cp37-cp37m-win_amd64.whl
   ```

## 🚀 Usage

1. **Run the application:**
   ```bash
   py Prototype.py
   ```

2. **Register new users:**
   - Click "Register New Person"
   - Enter username
   - Allow system to capture 100 training photos
   - Wait for AI training to complete

3. **Start attendance tracking:**
   - Click "Start Live Recognition"
   - System will automatically detect and mark attendance
   - Press 'q' to stop camera

4. **Manage attendance:**
   - Click "Show Attendance" to view records
   - Edit attendance manually if needed
   - Export to CSV for external use

## 📁 Project Structure

```
Face-Recognition-Attendance-System/
├── Prototype.py                              # Main application
├── haarcascade_frontalface_default.xml       # Face detection model
├── dlib-19.19.0-cp37-cp37m-win_amd64.whl    # dlib library for Python 3.7
├── coco.names                                # Object detection labels
├── Instruction READ FIRST.txt               # Setup instructions
├── .gitignore                               # Git ignore rules
├── face_dataset/                            # User face photos (created at runtime)
├── logs/                                    # Error logs (created at runtime)
├── attendance_log/                          # Exported CSV files (created at runtime)
└── README.md                                # This file
```

## ⚙️ Configuration

The system can be configured by modifying the `CONFIG` dictionary in `Prototype.py`:

```python
CONFIG = {
    "absent_time_threshold": 5,        # Seconds before marking absent
    "face_detection_model": "hog",     # "hog" (faster) or "cnn" (more accurate)
    "confidence_threshold": 0.4        # Face matching confidence level
}
```

## 🔒 Privacy & Security

- **Biometric Data**: Face encodings are stored locally and never transmitted
- **Personal Photos**: Training images are stored locally in `face_dataset/`
- **Data Protection**: The `.gitignore` file prevents accidental upload of personal data
- **Local Processing**: All face recognition happens on your local machine

## 🔧 Troubleshooting

### Common Issues:

1. **"No module named cv2"**
   ```bash
   pip install opencv-python
   ```

2. **"dlib wheel not compatible"**
   - Make sure you're using Python 3.7
   - Check if the wheel file matches your system architecture

3. **Camera not accessible**
   - Check if other applications are using the camera
   - Verify camera permissions

### Requirements:
- Python 3.7 (for provided dlib wheel compatibility)
- Adequate lighting for face detection
- Clear view of faces for recognition

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes. Please ensure compliance with local privacy laws when using biometric data.

## 👨‍💻 Author

**Teddy Juliansyah**
- GitHub: [@Teddy-Jul](https://github.com/Teddy-Jul)
- Email: teddy.juliansyah@binus.ac.id

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- face_recognition library by Adam Geitgey
- dlib library for machine learning algorithms

---

⭐ **Star this repository if you found it helpful!**