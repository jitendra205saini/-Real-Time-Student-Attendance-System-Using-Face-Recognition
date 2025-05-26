import pymysql
import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import re

def get_table_name():
    table_name = entry_name.get()  
    return table_name

def export_to_excel():
    table_name = get_table_name() 

    if not table_name or not re.match(r"\d{4}_\d{2}_\d{2}", table_name):
        messagebox.showerror("Error", "Invalid date format. Please enter the date in YYYY_MM_DD format.")
        return

    table_real_name = "attendance_" + table_name
    query = f"SELECT * FROM {table_real_name}"

    save_path = r"D:\face-attendance-system-gui\attendance_sheet"
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = os.path.join(save_path, f"{table_real_name}_output.xlsx")

    try:
        connection = pymysql.connect(
            host='localhost',
            user='jitendra',
            password='@Jitu9784',
            db='college'
        )
        
        df = pd.read_sql(query, connection)
        
        if df.empty:
            messagebox.showerror("Error", "No data found for the provided table name.")
            return

        df.to_excel(file_path, index=False, engine="openpyxl")
        
        connection.close()

        output_label.config(text=f"Table '{table_real_name}' exported successfully!\nFile saved at: {file_path}")
        output_label.config(fg='#248a20')
        
    except pymysql.MySQLError as e:
        output_label.config(text=f"Error: Unable to connect to MySQL database.\n{e}")
        output_label.config(fg='red')

    except Exception as e:
        output_label.config(text=f"Error: {e}")
        output_label.config(fg='red')

def stop_program():
    root.quit()
    root.destroy()

root = tk.Tk()
root.title("Export Attendance Table to Excel")
root.attributes("-fullscreen", True)
root.configure(bg="#F0F8FF", highlightbackground="#000000", highlightthickness=20)
root.resizable(False, False)

stop_button = tk.Button(root, text="Stop", command=stop_program, bg='red', fg='black', font=('Arial', 18), width=10, height=1)
stop_button.place(x=20, y=20)

label_name = tk.Label(root, text="Download student attendance sheet", bg="#F0F8FF", fg='black', font=('Arial', 30, "bold"))
label_name.place(x=440, y=30)

table_label = tk.Label(root, text="Table Name:-", bg="#F0F8FF", fg="black", font=('Arial', 20, "bold"))
table_label.place(x=683, y=200)

input_label = tk.Label(root, text="Please enter student attendance sheet date (in YYYY_MM_DD format):", bg="#F0F8FF", fg="black", font=('Arial', 20))
input_label.place(x=370, y=300)

entry_name = tk.Entry(root,bg="#bac5ba", bd=2, font=('Arial', 20))
entry_name.place(x=615, y=400)

export_button = tk.Button(root, text="Export Attendance Table", font=("Arial", 18), bg="#696969", fg="black", width=19,
                          highlightbackground="black", highlightthickness=3, command=export_to_excel)
export_button.place(x=629, y=500)

border = tk.Frame(root, bg="#696969")
border.place(x=65, y=600)

black = tk.Frame(border, bg="black")
black.pack(padx=25, pady=25)

output_label = tk.Label(black, text="", bg='black', fg='#248a20', font=("Arial", 16), width=105, height=4, anchor="w", justify="left")
output_label.pack(pady=25, padx=25)

root.mainloop()
