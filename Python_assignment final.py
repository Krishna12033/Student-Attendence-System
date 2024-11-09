import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pandas as pd
import qrcode
from PIL import Image, ImageTk
import tkcalendar


STUDENTS_FILE = 'students.csv'
ATTENDANCE_FILE = 'attendance.csv'
INSTRUCTOR_PASSWORD = "instructor"  


def load_data():
    try:
        students = pd.read_csv(STUDENTS_FILE)
        if students.empty or 'student_id' not in students.columns or 'name' not in students.columns:
            students = pd.DataFrame(columns=['student_id', 'name'])
    except FileNotFoundError:
        students = pd.DataFrame(columns=['student_id', 'name'])
    try:
        attendance = pd.read_csv(ATTENDANCE_FILE)
    except FileNotFoundError:
        attendance = pd.DataFrame(columns=['attendance_id', 'student_id', 'date', 'status'])
    return students, attendance

def save_data(students, attendance):
    students.to_csv(STUDENTS_FILE, index=False)
    attendance.to_csv(ATTENDANCE_FILE, index=False)


def security_page():
    def check_security():
        admin_id = entry_admin_id.get()
        admin_password = entry_admin_password.get()
        if admin_id == "admin" and admin_password == "admin123":
            security_window.destroy()  
            initialize_login()  
        else:
            messagebox.showerror("Error", "Invalid Admin ID or Password")

    security_window = tk.Tk()
    security_window.geometry("1400x700")
    security_window.config(bg="lightblue")
    security_window.title("Admin Login")

    tk.Label(security_window, text="Admin ID", font=("Arial", 14)).pack(pady=10)
    entry_admin_id = tk.Entry(security_window, font=("Arial", 14))
    entry_admin_id.pack(pady=5)

    tk.Label(security_window, text="Password", font=("Arial", 14)).pack(pady=10)
    entry_admin_password = tk.Entry(security_window, show="*", font=("Arial", 14))
    entry_admin_password.pack(pady=5)

    tk.Button(security_window, text="Login", font=("Arial", 14), command=check_security).pack(pady=20)

    security_window.mainloop()


def initialize_login():
    global login_window, user_type_var, entry_password

    login_window = tk.Tk()
    login_window.geometry("1400x700")
    login_window.title("Login Page")
    login_window.config(bg="lightblue")


    tk.Label(login_window, text="Welcome To Sigma College", font=("Arial", 40, "bold"), bg="lightblue").pack(pady=10)

    user_type_var = tk.StringVar(value="Student")
    tk.Radiobutton(login_window, text="Student", font=("Arial", 16), variable=user_type_var, value="Student", bg="lightblue").pack(pady=5)
    tk.Radiobutton(login_window, text="Instructor", font=("Arial", 16), variable=user_type_var, value="Instructor", bg="lightblue").pack(pady=5)

    tk.Label(login_window, text="Password (Instructors only)", font=("Arial", 16), bg="lightblue").pack(pady=10)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)

    tk.Button(login_window, text="Login", command=handle_login).pack(pady=20)
    
    login_window.mainloop()


def show_registration():
    registration_window = tk.Toplevel()
    registration_window.title("Student Registration")
    registration_window.config(bg="lightblue")
    registration_window.geometry("1400x700")

    tk.Label(registration_window, text="Student Registration", font=("Arial", 16)).pack(pady=20)

    # Name Entry Field
    tk.Label(registration_window, text="Enter your name:", font=("Arial", 12)).pack(pady=5)
    entry_name = tk.Entry(registration_window, font=("Arial", 12))
    entry_name.pack(pady=5)
    
    # ID Entry Field
    tk.Label(registration_window, text="Enter your ID:", font=("Arial", 12)).pack(pady=5)
    entry_id = tk.Entry(registration_window, font=("Arial", 12))
    entry_id.pack(pady=5)

    def register_student():
        name = entry_name.get()  # Get the student name from the entry widget
        if name:  # If name is not empty
            students, attendance = load_data()  # Load both students and attendance data
            student_id = len(students) + 1  # Generate a new student ID
            new_student = {'student_id': student_id, 'name': name}
            students = students.append(new_student, ignore_index=True)  # Append the new student
            save_data(students, attendance)  # Save the updated students and attendance data
            messagebox.showinfo("Success", f"Student {name} registered successfully!")  # Success message
            registration_window.destroy()  # Close the registration window
        else:
            messagebox.showerror("Error", "Please enter a valid name.")  # Show error if name is empty



    # Register Button
    tk.Button(registration_window, text="Register", command=register_student).pack(pady=10)





def handle_login():
    user_type = user_type_var.get()
    if user_type == "Student":
        show_registration()
    elif user_type == "Instructor":
        password = entry_password.get()
        if password == INSTRUCTOR_PASSWORD:
            instructor_functions()
        else:
            messagebox.showerror("Error", "Incorrect password!")


def instructor_functions():
    global checkboxes, date_label

    instructor_window = tk.Toplevel()
    instructor_window.title("Instructor Functions")
    instructor_window.geometry("1400x700")
    instructor_window.config(bg="lightblue")

    tk.Label(instructor_window, text="Instructor Attendance Functions", font=("Arial", 24, "bold"), bg="lightblue", fg="black").pack(pady=10)

    frame_attendance = tk.Frame(instructor_window, bg="lightblue")
    frame_attendance.pack(pady=20)

    students, _ = load_data()
    checkboxes = []

    tk.Label(frame_attendance, text="Mark Attendance", bg="lightblue").grid(row=0, column=0, pady=10)
    for index, student in students.iterrows():
        var = tk.BooleanVar()
        tk.Checkbutton(frame_attendance, text=student['name'], variable=var, bg="lightblue").grid(row=index + 1, column=0, sticky='w')
        checkboxes.append(var)

    tk.Button(frame_attendance, text="Record Attendance", command=mark_attendance).grid(row=len(students) + 1, columnspan=2, pady=10)

    tk.Button(instructor_window, text="View Registered Students", command=view_students).pack(pady=5)
    tk.Button(instructor_window, text="Return to Login Page", command=instructor_window.destroy).pack(pady=5)

    date_label = tk.Label(instructor_window, text="Select Date for Attendance", font=("Arial", 16), bg="lightblue")
    date_label.pack(pady=10)
    
    date_button = tk.Button(instructor_window, text="Select Date", font=("Arial", 14), command=lambda: open_calendar(date_label))
    date_button.pack(pady=5)


def open_calendar(date_label):
    def set_date():
        selected_date = cal.get_date()
        date_label.config(text=f"Selected Date: {selected_date}")
        calendar_window.destroy()

    calendar_window = tk.Toplevel()
    calendar_window.title("Select Date")
    calendar_window.geometry("400x400")
    cal = tkcalendar.Calendar(calendar_window)
    cal.pack(pady=20)
    
    tk.Button(calendar_window, text="Set Date", command=set_date).pack(pady=10)


def mark_attendance():
    students, attendance = load_data()
    date = date_label.cget("text").split(": ")[-1]

    for idx, student in students.iterrows():
        status = "Present" if checkboxes[idx].get() else "Absent"
        new_record = pd.DataFrame([[len(attendance)+1, student['student_id'], date, status]],
                                 columns=['attendance_id', 'student_id', 'date', 'status'])
        attendance = pd.concat([attendance, new_record], ignore_index=True)

    save_data(students, attendance)
    messagebox.showinfo("Success", "Attendance recorded successfully")


def view_students():
    students, _ = load_data()
    student_list = "\n".join(f"ID: {row['student_id']}, Name: {row['name']}" for _, row in students.iterrows())
    messagebox.showinfo("Registered Students", student_list if student_list else "No registered students.")


def show_registration():
    registration_window = tk.Toplevel()
    registration_window.title("Student Registration")
    registration_window.config(bg="lightblue")
    registration_window.geometry("1400x700")

    tk.Label(registration_window, text="Student Registration", font=("Arial", 16)).pack(pady=20)

    # Name Entry Field
    tk.Label(registration_window, text="Enter your name:", font=("Arial", 12)).pack(pady=5)
    entry_name = tk.Entry(registration_window, font=("Arial", 12))
    entry_name.pack(pady=5)
    
    # ID Entry Field
    tk.Label(registration_window, text="Enter your ID:", font=("Arial", 12)).pack(pady=5)
    entry_id = tk.Entry(registration_window, font=("Arial", 12))
    entry_id.pack(pady=5)

    def register_student():
        name = entry_name.get()
        student_id = entry_id.get()
        
        if name and student_id:
            students, _ = load_data()
            
            # Check for duplicate student ID
            if student_id in students['student_id'].astype(str).values:
                messagebox.showerror("Error", "Student ID already exists.")
                return
            
            # Append new student record
            students = pd.concat([students, pd.DataFrame({'student_id': [student_id], 'name': [name]})], ignore_index=True)
            save_data(students, None)  
            messagebox.showinfo("Success", f"Student {name} registered successfully!")
            registration_window.destroy()  
        else:
            messagebox.showerror("Error", "Please enter both name and ID.")

    # Register Button
    tk.Button(registration_window, text="Register", command=register_student).pack(pady=10)


def generate_report():
    students, attendance = load_data()
    report = {}

    for _, student in students.iterrows():
        student_attendance = attendance[attendance['student_id'] == student['student_id']]
        total_classes = len(student_attendance)
        if total_classes == 0:
            report[student['name']] = "No attendance records"
        else:
            present_classes = len(student_attendance[student_attendance['status'] == "Present"])
            percentage = (present_classes / total_classes * 100)
            report[student['name']] = f"{present_classes}/{total_classes} ({percentage:.2f}%)"

    report_str = "\n".join(f"{name}: {data}" for name, data in report.items())
    messagebox.showinfo("Attendance Report", report_str if report_str else "No attendance records.")


if __name__ == "__main__":
    security_page()
