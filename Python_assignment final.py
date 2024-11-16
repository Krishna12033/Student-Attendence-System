import csv
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime
import qrcode
import cv2

# File paths
students_file = "students.csv"
attendance_file = "attendance.csv"

# Instructor password
instructor_password = "instructor"

# Function to initialize the CSV files (create if they don't exist)
def initialize_csv():
   # Create the students CSV file with headers if it doesn't exist
   try:
       with open(students_file, mode='r') as file:
           pass  # File exists, nothing to do
   except FileNotFoundError:
       with open(students_file, mode='w', newline='') as file:
           writer = csv.writer(file)
           writer.writerow(["id", "name", "email", "password", "class_id"])

   # Create the attendance CSV file with headers if it doesn't exist
   try:
       with open(attendance_file, mode='r') as file:
           pass  # File exists, nothing to do
   except FileNotFoundError:
       with open(attendance_file, mode='w', newline='') as file:
           writer = csv.writer(file)
           writer.writerow(["student_id", "course_id", "date", "time", "status"])

initialize_csv()

# Student Functions

# Register a new student
def register_student(student_id, name, email, password, class_id):
   with open(students_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       students = list(reader)
       for student in students:
           if student[0] == student_id:
               messagebox.showinfo("Registration", f"Student ID: {student_id} is already registered.")
               return
   
   # Add student to the CSV file
   with open(students_file, mode='a', newline='') as file:
       writer = csv.writer(file)
       writer.writerow([student_id, name, email, password, class_id])

   # Generate QR code for the student
   qr = qrcode.make(student_id)
   qr_image_path = f"{student_id}_qr.png"
   qr.save(qr_image_path)  # Save QR code image
   messagebox.showinfo("Registration", f"Student {name} registered successfully! QR code saved as {qr_image_path}")

# Login student
def login_student(student_id, password):
   with open(students_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       for student in reader:
           if student[0] == student_id and student[3] == password:
               messagebox.showinfo("Login", "Login successful!")
               return student
   messagebox.showerror("Login", "Invalid ID or password. Please try again.")
   return None

# Mark attendance for the student
def mark_attendance(student_id, course_id):
   today = date.today().isoformat()
   time = datetime.now().strftime("%H:%M:%S")
   
   with open(attendance_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       for record in reader:
           if record[0] == student_id and record[2] == today and record[1] == course_id:
               messagebox.showinfo("Attendance", "Attendance already marked for today.")
               return
   
   # Add attendance to the CSV file
   with open(attendance_file, mode='a', newline='') as file:
       writer = csv.writer(file)
       writer.writerow([student_id, course_id, today, time, "Present"])
   messagebox.showinfo("Attendance", f"Attendance marked for student ID: {student_id} in course {course_id}")

# View attendance history
def view_attendance_history(student_id):
   with open(attendance_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       records = [record for record in reader if record[0] == student_id]
   
   if not records:
       messagebox.showinfo("Attendance History", "No attendance records found.")
       return
   
   # Create a table to display attendance history
   history_window = tk.Toplevel()
   history_window.title("Attendance History")
   
   tk.Label(history_window, text="Student ID | Course ID | Date | Time | Status", font=("Helvetica", 10)).pack(pady=5)
   
   for record in records:
       tk.Label(history_window, text=f"{record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]}", font=("Helvetica", 10)).pack(pady=2)

# Function to scan QR code
def scan_qr_code(student_id, course_id_entry):
   course_id = course_id_entry.get()
   if not course_id:
       messagebox.showerror("Error", "Please enter a valid Course ID.")
       return

   cap = cv2.VideoCapture(0)  # Start the webcam
   detector = cv2.QRCodeDetector()

   while True:
       _, img = cap.read()
       data, _, _ = detector.detectAndDecode(img)
       
       if data:
           cap.release()
           cv2.destroyAllWindows()
           if data == student_id:
               mark_attendance(student_id, course_id)
           else:
               messagebox.showerror("Error", "QR code does not match student ID.")
           break

       cv2.imshow("Scan QR Code", img)
       if cv2.waitKey(1) == ord("q"):
           break

   cap.release()
   cv2.destroyAllWindows()

# Student GUI for registering new students
def register_gui():
   def register_action():
       student_id = id_entry.get()
       name = name_entry.get()
       email = email_entry.get()
       password = password_entry.get()
       class_id = class_id_entry.get()
       
       if student_id and name and email and password and class_id:
           register_student(student_id, name, email, password, class_id)
           reg_window.destroy()
       else:
           messagebox.showerror("Error", "Please enter all fields.")

   reg_window = tk.Toplevel()
   reg_window.title("Register New Student")
   reg_window.geometry("1400x700")
   
   tk.Label(reg_window, text="Student ID:").pack(pady=5)
   id_entry = tk.Entry(reg_window)
   id_entry.pack(pady=5)
   
   tk.Label(reg_window, text="Name:").pack(pady=5)
   name_entry = tk.Entry(reg_window)
   name_entry.pack(pady=5)

   tk.Label(reg_window, text="Email:").pack(pady=5)
   email_entry = tk.Entry(reg_window)
   email_entry.pack(pady=5)
   
   tk.Label(reg_window, text="Password:").pack(pady=5)
   password_entry = tk.Entry(reg_window, show="*")
   password_entry.pack(pady=5)

   tk.Label(reg_window, text="Class ID:").pack(pady=5)
   class_id_entry = tk.Entry(reg_window)
   class_id_entry.pack(pady=5)
   
   tk.Button(reg_window, text="Register", command=register_action).pack(pady=20)

# Student login GUI
def login_gui():
   def login_action():
       student_id = student_id_entry.get()
       password = password_entry.get()
       
       if student_id and password:
           student = login_student(student_id, password)
           if student:
               login_window.destroy()
               student_dashboard(student)
       else:
           messagebox.showerror("Login", "Please enter both Student ID and Password.")

   login_window = tk.Toplevel()
   login_window.title("Student Login")
   login_window.geometry("1400x700")
   
   tk.Label(login_window, text="Student ID:").pack(pady=5)
   student_id_entry = tk.Entry(login_window)
   student_id_entry.pack(pady=5)
   
   tk.Label(login_window, text="Password:").pack(pady=5)
   password_entry = tk.Entry(login_window, show="*")
   password_entry.pack(pady=5)
   
   tk.Button(login_window, text="Login", command=login_action).pack(pady=20)

# Student Dashboard (modified to include the course ID entry)
def student_dashboard(student):
   dashboard_window = tk.Toplevel()
   dashboard_window.title("Student Dashboard")
   dashboard_window.geometry("1400x700")
   
   tk.Label(dashboard_window, text=f"Welcome, {student[1]}", font=("Helvetica", 16)).pack(pady=20)

   # Add input field for course ID
   tk.Label(dashboard_window, text="Course ID:").pack(pady=5)
   course_id_entry = tk.Entry(dashboard_window)
   course_id_entry.pack(pady=5)

   # Button to mark attendance
   tk.Button(dashboard_window, text="Mark Attendance", command=lambda: scan_qr_code(student[0], course_id_entry)).pack(pady=10)

   # Button to view attendance history
   tk.Button(dashboard_window, text="View Attendance History", command=lambda: view_attendance_history(student[0])).pack(pady=10)

# Main menu for students
def main_menu():
   window = tk.Tk()
   window.title("Student Attendance System")
   window.geometry("1400x700")
   
   tk.Button(window, text="Register", command=register_gui).pack(pady=20)
   tk.Button(window, text="Login", command=login_gui).pack(pady=20)
   window.mainloop()

# File paths
students_file = "students.csv"
attendance_file = "attendance.csv"

# Instructor password
instructor_password = "instructor"

# Instructor login
def instructor_login(password):
   if password == instructor_password:
       messagebox.showinfo("Instructor Login", "Login successful!")
       instructor_dashboard()
   else:
       messagebox.showerror("Instructor Login", "Invalid password.")

# Instructor dashboard
def instructor_dashboard():
   dashboard_window = tk.Toplevel()
   dashboard_window.title("Instructor Dashboard")
   dashboard_window.geometry("1400x700")
   
   tk.Label(dashboard_window, text="Instructor Dashboard", font=("Helvetica", 16)).pack(pady=20)
   
   # Button to view all attendance records
   tk.Button(dashboard_window, text="View All Attendance Records", command=view_all_attendance).pack(pady=10)

   # Button to view registered students
   tk.Button(dashboard_window, text="View Registered Students", command=view_registered_students).pack(pady=10)

   # Button to generate attendance report for individual student
   tk.Button(dashboard_window, text="Generate Attendance Report for Student", command=generate_attendance_report).pack(pady=10)

   # Button to view absent students for today's class
   tk.Button(dashboard_window, text="View Absent Students (Today)", command=view_absent_students_today).pack(pady=10)

   # Button to manually mark attendance
   tk.Button(dashboard_window, text="Manually Mark Attendance", command=manually_mark_attendance).pack(pady=10)

# View all attendance records
def view_all_attendance():
   with open(attendance_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       records = list(reader)
   
   if not records:
       messagebox.showinfo("Attendance Records", "No records found.")
       return
   
   # Create a table to display all attendance records
   records_window = tk.Toplevel()
   records_window.title("All Attendance Records")
   records_window.geometry("1400x700")
   
   tk.Label(records_window, text="Student ID | Course ID | Date | Time | Status", font=("Helvetica", 10)).pack(pady=5)
   
   for record in records:
       tk.Label(records_window, text=f"{record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]}", font=("Helvetica", 10)).pack(pady=2)

# View registered students
def view_registered_students():
   with open(students_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       students = list(reader)
   
   if not students:
       messagebox.showinfo("Registered Students", "No students registered.")
       return
   
   # Create a table to display all registered students
   students_window = tk.Toplevel()
   students_window.title("Registered Students")
   students_window.geometry("1400x700")
   
   tk.Label(students_window, text="Student ID | Name | Email | Class ID", font=("Helvetica", 10)).pack(pady=5)
   
   for student in students:
       tk.Label(students_window, text=f"{student[0]} | {student[1]} | {student[2]} | {student[4]}", font=("Helvetica", 10)).pack(pady=2)

# Generate attendance report for an individual student
def generate_attendance_report():
   def search_report():
       student_id = student_id_entry.get()
       
       with open(attendance_file, mode='r', newline='') as file:
           reader = csv.reader(file)
           records = [record for record in reader if record[0] == student_id]
       
       if not records:
           messagebox.showinfo("Attendance Report", f"No attendance records found for Student ID {student_id}.")
           return
       
       # Display the attendance records for the student
       report_window = tk.Toplevel()
       report_window.title(f"Attendance Report for Student ID {student_id}")
       report_window.geometry("1400x700")
       
       tk.Label(report_window, text="Course ID | Date | Time | Status", font=("Helvetica", 10)).pack(pady=5)
       
       for record in records:
           tk.Label(report_window, text=f"{record[1]} | {record[2]} | {record[3]} | {record[4]}", font=("Helvetica", 10)).pack(pady=2)
   
   report_window = tk.Toplevel()
   report_window.title("Generate Attendance Report")
   report_window.geometry("1400x700")
   
   tk.Label(report_window, text="Enter Student ID:", font=("Helvetica", 12)).pack(pady=10)
   
   student_id_entry = tk.Entry(report_window)
   student_id_entry.pack(pady=5)
   
   tk.Button(report_window, text="Generate Report", command=search_report).pack(pady=20)

# View absent students for today
def view_absent_students_today():
   today = date.today().isoformat()
   
   with open(attendance_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       records = list(reader)
   
   # Find students who are absent today (status not "Present")
   absent_students = []
   with open(students_file, mode='r', newline='') as file:
       reader = csv.reader(file)
       students = {student[0]: student[1] for student in reader}  # Map student_id to student_name
   
   for student_id, student_name in students.items():
       attended_today = False
       for record in records:
           if record[0] == student_id and record[2] == today:
               if record[4] == "Present":
                   attended_today = True
                   break
       if not attended_today:
           absent_students.append(f"{student_id} | {student_name}")
   
   if not absent_students:
       messagebox.showinfo("Absent Students", "No students were absent today.")
       return
   
   # Create a window to show absent students
   absent_window = tk.Toplevel()
   absent_window.title(f"Absent Students for {today}")
   absent_window.geometry("1400x700")
   
   tk.Label(absent_window, text="Student ID | Name", font=("Helvetica", 10)).pack(pady=5)
   
   for student in absent_students:
       tk.Label(absent_window, text=student, font=("Helvetica", 10)).pack(pady=2)

# Manually mark attendance
def manually_mark_attendance():
   def search_student():
       student_id = student_id_entry.get()
       
       with open(students_file, mode='r', newline='') as file:
           reader = csv.reader(file)
           students = {student[0]: student[1] for student in reader}
       
       if student_id in students:
           student_name = students[student_id]
           student_info_label.config(text=f"Student: {student_name} ({student_id})")
           status_var.set("Absent")
       else:
           messagebox.showerror("Error", "Student ID not found.")
   
   def mark_attendance():
       student_id = student_id_entry.get()
       status = status_var.get()
       today = date.today().isoformat()
       time = datetime.now().strftime("%H:%M:%S")
       
       with open(attendance_file, mode='a', newline='') as file:
           writer = csv.writer(file)
           writer.writerow([student_id, "Course_ID", today, time, status])  # Replace "Course_ID" with the actual course ID
           
       messagebox.showinfo("Attendance", "Attendance marked successfully!")
       mark_window.destroy()

   # Create a window for manually marking attendance
   mark_window = tk.Toplevel()
   mark_window.title("Manually Mark Attendance")
   
   tk.Label(mark_window, text="Enter Student ID:", font=("Helvetica", 12)).pack(pady=10)
   
   student_id_entry = tk.Entry(mark_window)
   student_id_entry.pack(pady=5)
   
   search_button = tk.Button(mark_window, text="Search Student", command=search_student)
   search_button.pack(pady=5)
   
   student_info_label = tk.Label(mark_window, text="Student Info", font=("Helvetica", 10))
   student_info_label.pack(pady=5)
   
   status_var = tk.StringVar()
   tk.OptionMenu(mark_window, status_var, "Present", "Absent").pack(pady=5)
   
   tk.Button(mark_window, text="Mark Attendance", command=mark_attendance).pack(pady=20)

# Main program to run the system
def start_program():
   window = tk.Tk()
   window.title("Attendance System")
   window.geometry("1400x700")
   
   # Show student menu button
   tk.Button(window, text="Student Menu", command=main_menu).pack(pady=10)
   
   # Instructor login button
   tk.Label(window, text="Instructor Login", font=("Helvetica", 14)).pack(pady=10)
   password_entry = tk.Entry(window, show="*")
   password_entry.pack(pady=5)
   tk.Button(window, text="Login", command=lambda: instructor_login(password_entry.get())).pack(pady=20)
   
   window.mainloop()

# Run the program
start_program()
