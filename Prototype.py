import cv2
import face_recognition
import os
import pickle
import time
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk

# Configuration
CONFIG = {
    "dataset_folder": "face_dataset",
    "attendance_file": "attendance_log.txt",
    "encoding_file": "face_encodings.pkl",
    "logs_folder": "logs",
    "attendance_log_folder": "attendance_log",
    "absent_time_threshold": 5,
    "attendance_display_interval": 5,
    "prolonged_absence_threshold": 60,
    "face_detection_model": "hog"  # bisa di ganti antara hog dan cnn (hog lebih cepat) (cnn lebih presisi)
}

# Membuat folder yang diperlukan jika belum ada
def ensure_folders_exist():
    required_folders = [CONFIG["dataset_folder"], CONFIG["logs_folder"], CONFIG["attendance_log_folder"]]
    for folder in required_folders:
        os.makedirs(folder, exist_ok=True)

ensure_folders_exist()

# Memuat encoding wajah dan nama dari file encodings.pkl
def load_encodings():
    if os.path.exists(CONFIG["encoding_file"]):
        with open(CONFIG["encoding_file"], "rb") as f:
            return pickle.load(f)
    return [], []

# Menginisialisasi log kehadiran semua orang sebagai "absent"
def initialize_attendance_log():
    # Initializes the attendance log by setting all users to 'Absent'.
    # If the attendance file exists, it resets statuses to 'Absent'.
    
    known_persons = [sanitize_name(person_name) for person_name in os.listdir(CONFIG["dataset_folder"])]

    # Reset attendance log with default values
    current_date = time.strftime("%Y-%m-%d")
    with open(CONFIG["attendance_file"], "w") as file:
        for person_name in known_persons:
            file.write(f"Name: {person_name}, Date: {current_date}, Time: N/A, Status: Absent\n")

# Mengganti spasi dengan "_" dalam nama dan mengkapitalkan huruf pertama
def sanitize_name(name):
    return name.strip().replace(" ", "_").capitalize()

# Memperbarui status kehadiran dalam log
def update_attendance(name, status, custom_time=None):
    sanitized_name = sanitize_name(name)
    current_date = time.strftime("%Y-%m-%d")
    current_time = custom_time or time.strftime("%H:%M:%S")

    with open(CONFIG["attendance_file"], "r") as file:
        lines = file.readlines()

    with open(CONFIG["attendance_file"], "w") as file:
        found = False
        updated_lines = []
        for line in lines:
            if line.startswith(f"Name: {sanitized_name}"):
                found = True
                updated_lines.append(f"Name: {sanitized_name}, Date: {current_date}, Time: {current_time}, Status: {status}\n")
            else:
                updated_lines.append(line)

        if not found:
            updated_lines.append(f"Name: {sanitized_name}, Date: {current_date}, Time: {current_time}, Status: {status}\n")

        updated_lines.sort(key=lambda x: ("Status: Absent" in x, x))
        file.writelines(updated_lines)

# Mencatat jika ada sebuah error dalam menjalankan program
def log_error(message):
    log_file = os.path.join(CONFIG["logs_folder"], f"log_{time.strftime('%Y%m%d')}.txt")
    with open(log_file, "a") as file:
        file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {message}\n")

# Menyusun ringkasan kehadiran dengan menghitung jumlah yang hadir dan absen
def summarize_daily_attendance():
    summary = {"Present": 0, "Absent": 0}
    try:
        with open(CONFIG["attendance_file"], "r") as file:
            for line in file:
                if "Status: Present" in line:
                    summary["Present"] += 1
                elif "Status: Absent" in line:
                    summary["Absent"] += 1
    except Exception as e:
        log_error(f"Failed to summarize daily attendance: {str(e)}")
    return summary

# Fungsi untuk mengedit status kehadiran absen menjadi hadir dan sebaliknya
# karena program belum sempurna
def edit_attendance(tree):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a record to edit.")
        return

    values = tree.item(selected_item, "values")
    if values[3] == "Present":
        new_status = "Absent"
        custom_time = "N/A"
    elif values[3] == "Absent":
        new_status = "Present"
        custom_time = time.strftime("%H:%M:%S")
    else:
        messagebox.showinfo("Invalid Action", "Invalid status.")
        return

    name = values[0]
    update_attendance(name, new_status, custom_time)

    tree.item(selected_item, values=(values[0], values[1], custom_time, new_status))

# Main program Face Recognition dan memperbarui status kehadiran secara real time
def live_face_recognition(known_face_encodings, known_face_names, confidence_threshold=0.4):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Unable to access the camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Starting live face recognition...")
    print("Press 'q' to exit the camera")

    attendance_window = tk.Toplevel(root)
    attendance_window.title("Live Attendance")
    attendance_window.geometry("600x400")

    attendance_label = tk.Label(attendance_window, text="Live Attendance", font=("Helvetica", 16))
    attendance_label.pack(pady=10)

    attendance_listbox = tk.Listbox(attendance_window, height=20, width=80)
    attendance_listbox.pack(pady=10)

    summary_label = tk.Label(attendance_window, text="", font=("Helvetica", 12))
    summary_label.pack(pady=5)

    present_users = {name: "Absent" for name in known_face_names}
    final_attendance = {name: {"Status": "Absent", "Time": "N/A"} for name in known_face_names}
    last_seen = {}

    # Initialize attendance log
    for name in known_face_names:
        update_attendance(name, "Absent", custom_time="N/A")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Unable to read the frame.")
            break

        frame = cv2.flip(frame, 1) # untuk mirror video terngatung aturan camera awal
        # tinggal di comment kalau tidak mau mirror
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame, model=CONFIG["face_detection_model"])
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        current_present_users = set()
        current_time = time.strftime("%H:%M:%S")

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=confidence_threshold)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                current_present_users.add(name)

                if present_users[name] == "Absent":
                    update_attendance(name, "Present", current_time)
                    final_attendance[name]["Status"] = "Present"
                    final_attendance[name]["Time"] = current_time
                    attendance_listbox.insert(tk.END, f"{name} marked present at {current_time}.")
                present_users[name] = "Present"
                last_seen[name] = time.time()

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        for name in present_users.keys():
            if name not in current_present_users:
                if time.time() - last_seen.get(name, 0) > CONFIG["absent_time_threshold"]:
                    if present_users[name] == "Present":
                        absent_time = time.strftime("%H:%M:%S")
                        update_attendance(name, "Absent", absent_time)
                        final_attendance[name]["Status"] = "Absent"
                        final_attendance[name]["Time"] = absent_time
                        attendance_listbox.insert(tk.END, f"{name} marked absent at {absent_time}.")
                    present_users[name] = "Absent"

        # Total yang hadir dan absen
        summary = summarize_daily_attendance()
        summary_label.config(text=f"Present: {summary['Present']}, Absent: {summary['Absent']}")

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    attendance_window.destroy()

    # Final Log
    with open(CONFIG["attendance_file"], "w") as file:
        for name, data in final_attendance.items():
            current_date = time.strftime("%Y-%m-%d")
            file.write(f"Name: {name}, Date: {current_date}, Time: {data['Time']}, Status: {data['Status']}\n")



# Mengambil 100 gambar wajah untuk pelatihan model
# gambar akan disimpan secara khusus pada folder Face_dataset
def capture_images_for_training(name, num_images=100):
    count = 0
    person_folder = os.path.join(CONFIG["dataset_folder"], name)
    os.makedirs(person_folder, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Unable to access the camera.")
        return

    # Menampilkan progress visual pada pengambilan gambar
    progress_window = tk.Toplevel(root)
    progress_window.title("Capturing Images")
    progress_window.geometry("400x100")

    progress_label = tk.Label(progress_window, text="Capturing images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, maximum=num_images, length=300)
    progress_bar.pack(pady=10)

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Unable to access the camera.")
            break

        face_locations = face_recognition.face_locations(frame, model=CONFIG["face_detection_model"])
        if face_locations:
            for (top, right, bottom, left) in face_locations:
                face_image = frame[top:bottom, left:right]
                face_image = cv2.resize(face_image, (150, 150))
                img_path = os.path.join(person_folder, f"{name}_{count}.jpg")
                cv2.imwrite(img_path, face_image)
                count += 1
                progress_bar["value"] = count
                progress_window.update_idletasks()

        cv2.imshow("Capture Photos", frame)
        if cv2.waitKey(100) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    progress_window.destroy()

# Melatih model dengan gambar yang telah di ambil
def train_face_encodings():
    known_face_encodings = []
    known_face_names = []

    # Menampilkan progress visual pada Pelatihan AI (progress paling lama di program)
    training_window = tk.Toplevel(root)
    training_window.title("Training AI")
    training_window.geometry("400x100")

    training_label = tk.Label(training_window, text="Training AI...")
    training_label.pack(pady=10)
    training_progress_bar = ttk.Progressbar(training_window, maximum=len(os.listdir(CONFIG["dataset_folder"])), length=300)
    training_progress_bar.pack(pady=10)

    person_count = 0
    for person_name in os.listdir(CONFIG["dataset_folder"]):
        person_folder = os.path.join(CONFIG["dataset_folder"], person_name)
        for img_name in os.listdir(person_folder):
            img_path = os.path.join(person_folder, img_name)
            try:
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(person_name)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        person_count += 1
        training_progress_bar["value"] = person_count
        training_window.update_idletasks()

    with open(CONFIG["encoding_file"], "wb") as f:
        pickle.dump((known_face_encodings, known_face_names), f)

    training_window.destroy()

# Memastikan nama yang di input adalah nama yang baru
def background_register_user(username):
    try:
        person_folder = os.path.join(CONFIG["dataset_folder"], username)
        if os.path.exists(person_folder):
            messagebox.showerror("Error", "User already exists.")
            return

        capture_images_for_training(username)
        train_face_encodings()
        messagebox.showinfo("Success", f"User '{username}' has been registered.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Menambahkan Orang pada program
def register_user():
    username = simpledialog.askstring("Input", "Enter a new username:")
    if not username:
        return

    threading.Thread(target=background_register_user, args=(username,), daemon=True).start()

# Menampilkan Absensi Keseluruhan
def show_attendance():
    if not os.path.exists(CONFIG["attendance_file"]):
        messagebox.showinfo("No Records", "No attendance records found.")
        return

    attendance_window = tk.Toplevel(root)
    attendance_window.title("Attendance Records")
    attendance_window.geometry("600x400")

    tree = ttk.Treeview(attendance_window, columns=("Name", "Date", "Time", "Status"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.heading("Status", text="Status")
    tree.column("Name", anchor="center", width=150)
    tree.column("Date", anchor="center", width=150)
    tree.column("Time", anchor="center", width=100)
    tree.column("Status", anchor="center", width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    with open(CONFIG["attendance_file"], "r") as file:
        for line in file:
            data = line.strip().split(", ")
            values = [item.split(": ")[1] for item in data]
            tree.insert("", tk.END, values=values)

    edit_button = tk.Button(attendance_window, text="Edit Selected", command=lambda: edit_attendance(tree))
    edit_button.pack(pady=10)

# Mengexport log kehadiran ke file CSV
def export_attendance_to_csv():
    logs_folder = CONFIG["attendance_log_folder"]
    os.makedirs(logs_folder, exist_ok=True)

    day_name = time.strftime("%A")  # Get current day name (e.g., Monday, Tuesday)
    log_files = [file for file in os.listdir(logs_folder) if file.startswith(f"Attendance_{day_name}_") and file.endswith(".csv")]
    max_number = 0
    for file in log_files:
        try:
            number = int(file.split("_")[-1].split(".")[0])
            max_number = max(max_number, number)
        except ValueError:
            continue

    new_file_name = f"Attendance_{day_name}_{max_number + 1}.csv"
    save_path = os.path.join(logs_folder, new_file_name)

    with open(save_path, "w") as csv_file:
        csv_file.write("Name,Date,Time,Status\n")
        with open(CONFIG["attendance_file"], "r") as file:
            for line in file:
                csv_file.write(line.replace(", ", ","))

    messagebox.showinfo("Success", f"Attendance records exported to {save_path}.")

# GUI Utama
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("400x300")

tk.Label(root, text="Face Recognition Attendance System", font=("Helvetica", 16)).pack(pady=20)
tk.Button(root, text="Register New Person", command=register_user, width=25).pack(pady=10)
tk.Button(root, text="Start Live Recognition", command=lambda: live_face_recognition(*load_encodings()), width=25).pack(pady=10)
tk.Button(root, text="Show Attendance", command=show_attendance, width=25).pack(pady=10)
tk.Button(root, text="Export Attendance to CSV", command=export_attendance_to_csv, width=25).pack(pady=10)

initialize_attendance_log()
root.mainloop()

