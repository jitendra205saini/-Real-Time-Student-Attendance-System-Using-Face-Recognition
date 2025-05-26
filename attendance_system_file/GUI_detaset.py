import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import subprocess
from threading import Thread
from queue import Queue, Empty
import threading


face_classifier = cv2.CascadeClassifier(
    'C:/Users/jiten/AppData/Local/Programs/Python/Python312/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Could not open video.")

def face_extractor(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    faces_cropped = []
    for (x, y, w, h) in faces:
        cropped_face = img[y:y+h, x:x+w]
        faces_cropped.append(cropped_face)
    return faces_cropped

def collect_face_samples(person_name, roll_number):
    save_path = f'D:/face-attendance-system-gui/data/{person_name}_{roll_number}/'
    os.makedirs(save_path, exist_ok=True)
    count = 0
    while count < 100:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image.")
            break
        faces = face_extractor(frame)
        if faces is not None:
            for face in faces:
                count += 1
                face = cv2.flip(face, 1)
                face = cv2.resize(face, (200, 200))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                file_name_path = os.path.join(save_path, f'{roll_number}_{count}.jpg')
                cv2.imwrite(file_name_path, face)
                cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Face Cropper', face)
                if count == 100:
                    messagebox.showinfo("Info", "100 samples collected.")
                    break
        if cv2.waitKey(1) == 13:
            break
    messagebox.showinfo("Info", "Sample Collection Completed")

def start_collection():
    person_name = entry_name.get()
    roll_number = entry_roll.get()
    if person_name and roll_number:
        collect_face_samples(person_name, roll_number)
    else:
        messagebox.showwarning("Warning", "Please enter both name and roll number.")


def read_process_output(process, output_queue):
    for line in iter(process.stdout.readline, ''):
        output_queue.put(line.strip())
    process.stdout.close()

def update_output():
    try:
        while True:
            line = output_queue.get_nowait() 
            current_text = output_label.cget("text")
            output_label.config(text=f"{current_text}\n{line}")
    except Empty:
        pass
    if process.poll() is None:  
        root.after(100, update_output)  
    else:
        summit_button.config(state=tk.NORMAL)  

def summit_program():
    summit_button.config(state=tk.DISABLED) 
    output_label.config(text="")  

    global process
    process = subprocess.Popen(
        ["python", r"D:\face-attendance-system-gui\attendance_file\Training.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    Thread(target=read_process_output, args=(process, output_queue), daemon=True).start()
    update_output()

def stop_program():
   
    global cap
    if 'cap' in globals() and cap.isOpened():
        cap.release()    
    try:
        subprocess.Popen(["python", r"D:\face-attendance-system-gui\attendance_file\main.py"])
        root.after(2000,cv2.destroyAllWindows()) 
        root.after(2000,cap.release())
        root.after(2000,root.quit())
        root.after(2000,sys.exit())
    except Exception as e:
        print(f"Error opening registration script: {e}")
    


root = tk.Tk()
root.title("Face Sample Collection")
root.attributes('-fullscreen', True)
root.configure(bg="#F0F8FF", highlightbackground="#000000", highlightthickness=20)
root.resizable(False, False)

label_name = tk.Label(root, text="Registration", bg="#F0F8FF", fg='black', font=('Arial', 50, "bold"))
label_name.place(x=540,y=30)

stop_button = tk.Button(root, text="Stop", command=stop_program, bg='red', fg='black', font=('Arial', 18),width=10,height=1)
stop_button.place(x=20, y=20)

summit_button = tk.Button(root, text="Start Training", command=summit_program, bg='red', fg='white',  font=('Arial', 18),width=10,height=1)
summit_button.place(x=210, y=600)

border = tk.Frame(root, bg="#696969")
border.place(x=65 ,y=220)

black = tk.Frame(border, bg="black")
black.pack(padx=25 ,pady=25)

output_label = tk.Label(black, text="", bg='black', fg='#248a20', font=("Arial", 16), width=30, height=8, anchor="w", justify="left")
output_label.pack(pady=25, padx=25)

frame = tk.Frame(root, bg="#F0F8FF",width= 400, height=400)
frame.place(x=890,y=200)

label_name = tk.Label(frame, text="Enter Your Name:", bg="#F0F8FF", fg='black', font=('Arial', 20))
label_name.pack(pady=5)

entry_name = tk.Entry(frame, bg="#bac5ba", bd=2,font=('Arial', 20))
entry_name.pack(pady=5)

label_roll = tk.Label(frame, text="Enter Your Roll Number:", bg="#F0F8FF", fg='black',font=('Arial', 20))
label_roll.pack(pady=10)

entry_roll = tk.Entry(frame, bg="#bac5ba", bd=2,font=('Arial', 20))
entry_roll.pack(pady=5)

space = tk.Label(frame, bg="#F0F8FF",font=('Arial', 20))
space.pack(pady=5)

button_start = tk.Button(frame, text="Start Collection", command=start_collection, bg="#696969", fg='black',width=15,height=1,font=('Arial',20))
button_start.pack(pady=5)


output_queue = Queue()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
