import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pandas as pd
import qrcode
from PIL import Image, ImageTk
from fpdf import FPDF
import tkcalendar

# File Paths
STUDENTS_FILE = 'students.csv'
ATTENDANCE_FILE = 'attendance.csv'
INSTRUCTOR_PASSWORD = "instructor"  # Instructor login password

# Load data from CSV, create if not exists
def load_data():
    try:
        students = pd.read_csv(STUDENTS_FILE)
        if students.empty or not {'student_id', 'name', 'email', 'course'}.issubset(students.columns):
            students = pd.DataFrame(columns=['student_id', 'name', 'email', 'course'])
    except FileNotFoundError:
        students = pd.DataFrame(columns=['student_id', 'name', 'email', 'course'])
    
    try:
        attendance = pd.read_csv(ATTENDANCE_FILE)
    except FileNotFoundError:
        attendance = pd.DataFrame(columns=['attendance_id', 'student_id', 'date', 'status'])
    
    return students, attendance

# Save data to CSV
def save_data(students, attendance=None):
    students.to_csv(STUDENTS_FILE, index=False)
    if attendance is not None:
        attendance.to_csv(ATTENDANCE_FILE, index=False)

# Main security page for instructor login
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
    security_window.geometry("500x300")
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

# Login page for selecting user type
def initialize_login():
    login_window = tk.Tk()
    login_window.geometry("500x300")
    login_window.title("Login Page")
    login_window.config(bg="lightblue")

    tk.Label(login_window, text="Welcome To Sigma College", font=("Arial", 20, "bold"), bg="lightblue").pack(pady=10)

    user_type_var = tk.StringVar(value="Student")
    tk.Radiobutton(login_window, text="Student", font=("Arial", 16), variable=user_type_var, value="Student", bg="lightblue").pack(pady=5)
    tk.Radiobutton(login_window, text="Instructor", font=("Arial", 16), variable=user_type_var, value="Instructor", bg="lightblue").pack(pady=5)

    tk.Label(login_window, text="Password (Instructors only)", font=("Arial", 16), bg="lightblue").pack(pady=10)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)

    def handle_login():
        user_type = user_type_var.get()
        if user_type == "Student":
            student_login()
        elif user_type == "Instructor":
            password = entry_password.get()
            if password == INSTRUCTOR_PASSWORD:
                login_window.destroy()
                instructor_functions()
            else:
                messagebox.showerror("Error", "Incorrect password!")

    tk.Button(login_window, text="Login", command=handle_login).pack(pady=20)
    tk.Button(login_window, text="Student Registration", command=show_registration).pack(pady=5)

    login_window.mainloop()

# Student Registration function
# Student Registration function
def show_registration():
    registration_window = tk.Toplevel()
    registration_window.title("Student Registration")
    registration_window.config(bg="lightblue")
    registration_window.geometry("400x400")

    tk.Label(registration_window, text="Student Registration", font=("Arial", 16)).pack(pady=20)

    entry_name = tk.Entry(registration_window, font=("Arial", 12))
    entry_id = tk.Entry(registration_window, font=("Arial", 12))
    entry_email = tk.Entry(registration_window, font=("Arial", 12))
    entry_course = tk.Entry(registration_window, font=("Arial", 12))

    tk.Label(registration_window, text="Enter your name:", font=("Arial", 12)).pack(pady=5)
    entry_name.pack(pady=5)

    tk.Label(registration_window, text="Enter your ID:", font=("Arial", 12)).pack(pady=5)
    entry_id.pack(pady=5)

    tk.Label(registration_window, text="Enter your email:", font=("Arial", 12)).pack(pady=5)

    entry_email.pack(pady=5)
    tk.Label(registration_window, text="Enter your course:", font=("Arial", 12)).pack(pady=5)
    entry_course.pack(pady=5)

    def register_student():
        name = entry_name.get().strip()
        student_id = entry_id.get().strip()
        email = entry_email.get().strip()
        course = entry_course.get().strip()

        if name and student_id and email and course:
            students, _ = load_data()
            # Check if the student ID already exists in the database
            if student_id in students['student_id'].astype(str).values:
                messagebox.showerror("Error", "Student ID already exists. Please use a different ID.")
                return

            # Add the new student record to the DataFrame
            new_student = pd.DataFrame({'student_id': [student_id], 'name': [name], 'email': [email], 'course': [course]})
            students = pd.concat([students, new_student], ignore_index=True)

            # Save the updated student data to CSV
            save_data(students)

            # Confirm successful registration
            messagebox.showinfo("Welcome", f"Welcome {name}, you have been registered successfully!")
            generate_qr_code(student_id)

            # Clear the input fields
            entry_name.delete(0, tk.END)
            entry_id.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            entry_course.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter all details.")

    tk.Button(registration_window, text="Register", command=register_student).pack(pady=10)
    tk.Button(registration_window, text="Return to Login Page", command=registration_window.destroy).pack(pady=10)

# Generate QR Code for student
def generate_qr_code(student_id):
    qr = qrcode.make(student_id)
    qr.show()

# Student Login function
def student_login():
    def verify_student_login():
        students, _ = load_data()  # Load students data
        name = entry_name.get().strip()  # Remove extra spaces
        student_id = entry_id.get().strip()  # Remove extra spaces

        # Ensure case-insensitive matching by converting both to lower case
        student_record = students[students['name'].str.lower().str.strip() == name.lower()]

        # Check if a student with the name exists and if the ID matches
        if not student_record.empty:
            if str(student_record['student_id'].values[0]).strip() == student_id:
                messagebox.showinfo("Login Success", "Login successful!")
                view_student_profile(student_record)
            else:
                messagebox.showerror("Error", "Invalid Student ID")
        else:
            messagebox.showerror("Error", "Invalid name or student ID")

    student_login_window = tk.Toplevel()
    student_login_window.title("Student Login")
    student_login_window.geometry("400x300")
    student_login_window.config(bg="lightblue")

    tk.Label(student_login_window, text="Enter your name:", font=("Arial", 12), bg="lightblue").pack(pady=10)
    entry_name = tk.Entry(student_login_window, font=("Arial", 12))
    entry_name.pack(pady=5)

    tk.Label(student_login_window, text="Enter your Student ID:", font=("Arial", 12), bg="lightblue").pack(pady=10)
    entry_id = tk.Entry(student_login_window, font=("Arial", 12))
    entry_id.pack(pady=5)

    tk.Button(student_login_window, text="Login", command=verify_student_login).pack(pady=20)

# View student profile with download button
def view_student_profile(student_record):
    profile_window = tk.Toplevel()
    profile_window.title("Student Profile")
    profile_window.geometry("400x300")
    profile_window.config(bg="lightblue")

    student = student_record.iloc[0]

    tk.Label(profile_window, text=f"Name: {student['name']}", font=("Arial", 12), bg="lightblue").pack(pady=10)
    tk.Label(profile_window, text=f"ID: {student['student_id']}", font=("Arial", 12), bg="lightblue").pack(pady=10)
    tk.Label(profile_window, text=f"Email: {student['email']}", font=("Arial", 12), bg="lightblue").pack(pady=10)
    tk.Label(profile_window, text=f"Course: {student['course']}", font=("Arial", 12), bg="lightblue").pack(pady=10)

    tk.Button(profile_window, text="Download PDF", command=lambda: generate_pdf(student)).pack(pady=10)

# Generate a PDF for a student
def generate_pdf(student):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Student Profile", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Name: {student['name']}", ln=True)
    pdf.cell(200, 10, txt=f"ID: {student['student_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {student['email']}", ln=True)
    pdf.cell(200, 10, txt=f"Course: {student['course']}", ln=True)

    pdf_file = f"{student['name']}_profile.pdf"
    pdf.output(pdf_file)
    messagebox.showinfo("PDF Downloaded", f"PDF saved as {pdf_file}")
# Instructor Functions
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

# Open calendar for date selection
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

# Mark attendance
def mark_attendance():
    students, attendance = load_data()
    date = date_label.cget("text").split(": ")[-1]

    for idx, student in students.iterrows():
        status = "Present" if checkboxes[idx].get() else "Absent"
        # Include student name in the attendance record
        new_record = pd.DataFrame([[len(attendance)+1, student['name'], student['student_id'], date, status]],
                                 columns=['attendance_id', 'student_name', 'student_id', 'date', 'status'])
        attendance = pd.concat([attendance, new_record], ignore_index=True)

    save_data(students, attendance)
    messagebox.showinfo("Success", "Attendance recorded successfully!")

# View registered students
def view_students():
    students, _ = load_data()

    view_window = tk.Toplevel()
    view_window.title("Registered Students")
    view_window.geometry("1400x700")

    tree = tk.Treeview(view_window, columns=("ID", "Name", "Email", "Course"))
    tree.heading("#1", text="Student ID")
    tree.heading("#2", text="Name")
    tree.heading("#3", text="Email")
    tree.heading("#4", text="Course")

    for student in students.itertuples():
        tree.insert("", tk.END, values=(student.student_id, student.name, student.email, student.course))

    tree.pack(pady=20)

# Start the application
security_page()
