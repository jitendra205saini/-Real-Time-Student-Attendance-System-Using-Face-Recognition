import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import cv2
import pymysql
from os import listdir
from os.path import isdir, join
from datetime import datetime
import threading
import subprocess
import sys  

connection = pymysql.connect(
    host='localhost',
    user='jitendra',
    password='@Jitu9784',
    db='college'
)

try:
    model = cv2.face.LBPHFaceRecognizer_create()
    model.read('D:/face-attendance-system-gui/model/face_trained_model.yml')
    print("Trained Model Loaded")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

data_path = 'D:/face-attendance-system-gui/data/'
names = {}
label_count = 0

for person_folder in listdir(data_path):
    if isdir(join(data_path, person_folder)):
        name_roll = person_folder.split('_')
        if len(name_roll) == 2:
            names[label_count] = (name_roll[0], name_roll[1])
        label_count += 1

print("Names dictionary:", names)

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def face_detector(img, size=0.5):
    gray = cv2.resize(img,(760,560))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return img, None, None, None, None, None

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi = img[y:y + h, x:x + w]
        roi = cv2.resize(roi, (200, 200))
        return img, roi, x, y, w, h

def check_attendance(name, roll_number):
    current_date = datetime.now().strftime("%Y_%m_%d")
    check_query = f"SELECT * FROM attendance_{current_date} WHERE name=%s AND roll_number=%s"
    
    with connection.cursor() as cursor:
        try:
            cursor.execute(check_query, (name, roll_number))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking attendance for {name}: {e}")
            return False

def log_attendance(name, roll_number):
    current_date = datetime.now().strftime("%Y_%m_%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS attendance_{current_date} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        roll_number VARCHAR(50) NOT NULL,
        time VARCHAR(8) NOT NULL
    );
    """
    
    insert_query = f"INSERT INTO attendance_{current_date} (name, roll_number, time) VALUES (%s, %s, %s)"

    with connection.cursor() as cursor:
        try:
            cursor.execute(create_table_query)
            connection.commit()
            print(f"Table 'attendance_{current_date}' created or already exists.")
        except Exception as e:
            print(f"Error creating table 'attendance_{current_date}': {e}")

        try:
            cursor.execute(insert_query, (name, roll_number, current_time))
            connection.commit()
            print(f"Attendance logged for {name} ({roll_number}) at {current_time}.")
        except Exception as e:
            print(f"Error inserting attendance for {name} ({roll_number}): {e}")
is_detection_started = False

def update_camera():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        root.after(100, update_camera)
        return

   
    frame = cv2.flip(frame, 1)

    frame = cv2.resize(frame, (760, 560))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    img = ImageTk.PhotoImage(Image.fromarray(frame))

    camera_label.config(image=img)
    camera_label.image = img

    root.after(10, update_camera)

def start_detection():
    global is_detection_started
    is_detection_started = True
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)

        frame = cv2.resize(frame, (760, 560))

        image, face, x, y, w, h = face_detector(frame)

        if face is not None:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            result = model.predict(face)

            if result[1] < 500:
                confidence = int(100 * (1 - (result[1]) / 300))
            else:
                confidence = 0

            if confidence > 75:
                person_name, roll_number = names.get(result[0], ("Unknown", "Unknown"))
                cv2.putText(image, f"{person_name} ({roll_number})", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (42, 235, 35), 2)

                if person_name != "Unknown" and roll_number != "Unknown":
                    if not check_attendance(person_name, roll_number):
                        log_attendance(person_name, roll_number)
                    else:
                        print(f"Attendance already marked for {person_name} ({roll_number}).")
            else:
                cv2.putText(image, "Unknown", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(image, "Face Not Found", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(image))

        camera_label.config(image=img)
        camera_label.image = img
        if cv2.waitKey(1) & 0xFF == 13:
            break

    cap.release()

def toggle_detection():
    global is_detection_started
    if not is_detection_started:
        detection_thread = threading.Thread(target=start_detection)
        detection_thread.daemon = True
        detection_thread.start()
        detection_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
    else:
        is_detection_started = False
        detection_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        cap.release() 
        cap.open(0) 

def update_time():
    now = datetime.now()
    current_time = now.strftime("    %H:%M:%S     \n %A\n %d / %B / %Y")
    time_label.config(text=current_time)
    time_label.after(1000, update_time)

def open_registration():
    global cap
    if 'cap' in globals() and cap.isOpened():
        cap.release()    
    try:
        subprocess.Popen(["python", r"D:\face-attendance-system-gui\attendance_file\GUI_detaset.py"])
    except Exception as e:
        print(f"Error opening registration script: {e}")
    root.after(7000,stop_program)    

def download_student_list():
    try:
        subprocess.Popen(["python", r"D:\face-attendance-system-gui\attendance_file\table_canvert_exel.py"])
    except Exception as e:
        print(f"Error opening registration script: {e}")

def stop_program():
    cap.release()
    cv2.destroyAllWindows()
    root.quit()
    sys.exit()

root = tk.Tk()
root.title("Attendance System")

root.attributes('-fullscreen', True)

root.configure(bg="#F0F8FF", highlightbackground="#000000", highlightthickness=20)
root.resizable(False, False)

title_label = tk.Label(root, text="Attendance System", font=("Arial", 30,"bold"), bg="#F0F8FF", fg="black")
title_label.place(x=600, y=20)

camera_label = Label(root, width=800, height=600, bg="#696969" )
camera_label.place(x=50, y=130)

detection_button = tk.Button(root, text="Start Detection", font=("Arial", 14), command=toggle_detection, bg="#696969")
detection_button.place(x=150, y=750)

stop_button = tk.Button(root, text="Stop Detection", font=("Arial", 14), command=toggle_detection, bg="#696969", state=tk.DISABLED)
stop_button.place(x=550, y=750)

stop_button_gui = tk.Button(root, text="STOP CODE", command=stop_program, bg='red', fg='black', font=('Arial', 12))
stop_button_gui.place(x=50, y=20)

time_label = tk.Label(root, font=("Arial", 20), fg="Red", bg="#000000")
time_label.place(x=1120, y=30)

registration_button = tk.Button(root, text="Registration", font=("Arial", 18), bg="#696969", fg="black", width=19,
                                highlightbackground="black", highlightthickness=3, command=open_registration)
registration_button.place(x=1120, y=300)

list_student_button = tk.Button(root, text="list_student", font=("Arial", 18), bg="#696969", fg="black", width=19,
                                highlightbackground="black", highlightthickness=3, command=download_student_list)
list_student_button.place(x=1120, y=500)

update_time()

cap = cv2.VideoCapture(0)
update_camera()

root.mainloop()
