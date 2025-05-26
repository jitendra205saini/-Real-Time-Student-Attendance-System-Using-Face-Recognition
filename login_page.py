import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import subprocess
import threading
import sys

password = "9351"

SCRIPT_PATH = "D://face-attendance-system-gui//attendance_file//main.py"
LEFT_IMAGE_PATH = "D://face-attendance-system-gui//toggle//logo.jpg"
SHOW_ICON_PATH = "D://face-attendance-system-gui//toggle//hide.png"
HIDE_ICON_PATH = "D://face-attendance-system-gui//toggle//show.png"

root = tk.Tk()
root.title("Login App")
root.attributes("-fullscreen", True)
root.configure(bg="white", highlightbackground="#000000", highlightthickness=20)
root.resizable(False, False)

try:
    left_image = ImageTk.PhotoImage(Image.open(LEFT_IMAGE_PATH))
    show_icon = ImageTk.PhotoImage(Image.open(SHOW_ICON_PATH).resize((50, 40)))
    hide_icon = ImageTk.PhotoImage(Image.open(HIDE_ICON_PATH).resize((50, 40)))


except Exception as e:
    tk.Tk().withdraw()
    messagebox.showerror("Error", f"Failed to load images: {e}")
    sys.exit()

def validate_login():
    username = username_entry.get()
    entered_password = password_entry.get()
    
    if username == "jitendra" and entered_password == password:
        output_label.config(text="Login Successful! Processing...", fg='green')
        show_loading_circle()
        threading.Thread(target=main, daemon=True).start()
        root.after(7000, stop_program)  
    elif username != "jitendra":
        output_label.config(text="Invalid Username", fg='red')
    else:
        output_label.config(text="Invalid Password", fg='red')


def main():
    try:
        subprocess.call(["python", SCRIPT_PATH])
        hide_loading_circle()
    except FileNotFoundError:
        messagebox.showerror("Error", "Main script not found. Please check the path.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Script execution failed with error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    finally:
        output_label.config(text="Processing Completed", fg='blue')


def stop_program():
    root.quit()
    root.destroy()
    sys.exit()

def toggle_password():
    if password_entry.cget('show') == "*":
        password_entry.config(show="")
        toggle_button.config(image=hide_icon)
    else:
        password_entry.config(show="*")
        toggle_button.config(image=show_icon)

def show_loading_circle():
    global progress
    progress = 0
    circle_canvas.place(x=850, y=350)
    percentage_label.place(x=867, y=380)
    animate_loading()

def hide_loading_circle():
    circle_canvas.place_forget()
    percentage_label.place_forget()

def animate_loading():
    global progress
    progress += 2.1  
    if progress > 100:
        progress = 100
    draw_loading_circle(progress)
    percentage_label.config(text=f"{int(progress)}%")
    if progress < 100:
        circle_canvas.after(125, animate_loading)  

def draw_loading_circle(percentage):
    radius = 40
    angle = (360 * percentage) / 100
    start_angle = -90
    extent = angle
    circle_canvas.delete("all")
    circle_canvas.create_oval(10, 10, 80, 80, outline="#c0c0c0", width=6)
    circle_canvas.create_arc(10, 10, 80, 80, start=start_angle, extent=extent, outline="black", width=5, style="arc")

left_side_image = tk.Label(root, image=left_image, bg="white",height=818,width=780)
left_side_image.place(x=1, y=1)

stop_button = tk.Button(root, text="Stop", command=stop_program, bg='red', fg='white', font=('Arial', 18), width=10)
stop_button.place(x=20, y=20)

logo_label = tk.Label(root, text="Login", bg="white", fg="black", font=('Arial', 55, "bold"))
logo_label.place(x=1050, y=100)

username_label = tk.Label(root, text="Enter Username:", bg="white", fg="black", font=('Arial', 20))
username_label.place(x=1050, y=250)

username_entry = tk.Entry(root, bg="#bac5ba", bd=2, font=('Arial', 20))
username_entry.place(x=1005, y=300)

password_label = tk.Label(root, text="Enter Password:", bg="white", fg="black", font=('Arial', 20))
password_label.place(x=1050, y=350)

password_entry = tk.Entry(root, bg="#bac5ba", bd=2, font=('Arial', 20), show="*")
password_entry.place(x=1005, y=400)

toggle_button = tk.Button(root, image=show_icon, command=toggle_password)
toggle_button.place(x=1320, y=395)

login_button = tk.Button(root, text="Login", font=("Arial", 18), bg="#696969", fg="black", width=19,
                         highlightbackground="black", highlightthickness=3, command=validate_login)
login_button.place(x=1015, y=500)

output_label = tk.Label(root, text="", bg='white', fg='black', font=("Arial", 16), width=30, height=4, anchor="w", justify="left")
output_label.place(x=1035, y=600)

circle_canvas = tk.Canvas(root, width=100, height=100, bg="white", bd=0, highlightthickness=0)
percentage_label = tk.Label(root, text="0%", bg="white", fg="black", font=("Arial", 16))

root.mainloop()
