import flet as ft
import mysql.connector
import cv2
import numpy as np
import face_recognition
import pickle
import logging
from datetime import datetime
import winsound
import os
import platform
import cvzone
import pyttsx3
import threading
import time
import pandas as pd
import io
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from back_button import create_back_button
from teacher_dashboard import teacher_dashboard
from manage_attendance import main_manage  # Import manage_attendance module

# Constants
ENCODE_FILE = "EncodeFile.p"
FACE_DISTANCE_THRESHOLD = 0.6
SOUND_FILE = "beep.wav"
CAMERA_TIMEOUT = 300  # Timeout in seconds (5 minutes)

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def play_beep_sound():
    logging.debug("Starting play_beep_sound")
    try:
        if platform.system() == "Windows":
            winsound.Beep(1000, 200)
        else:
            if os.path.exists(SOUND_FILE):
                os.system(f"aplay {SOUND_FILE}")
            else:
                logging.warning("Sound file not found for non-Windows system.")
        logging.debug("Finished play_beep_sound")
    except Exception as e:
        logging.error(f"Failed to play sound: {str(e)}")

def play_tts_message(message):
    logging.debug(f"Starting play_tts_message: {message}")
    try:
        tts_engine.say(message)
        tts_engine.runAndWait()
        logging.debug("Finished play_tts_message")
    except Exception as e:
        logging.error(f"Failed to play TTS message: {str(e)}")

def run_in_thread(func, *args):
    """Run a function in a separate thread to prevent blocking."""
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()

def main(page: ft.Page, teacher_id=1):
    logging.debug("Starting mark attendance application")

    # Window settings
    page.title = "Mark Attendance - Face Recognition System"
    page.window_width = 1920
    page.window_height = 1080
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 0
    page.scroll = None

    # Colors
    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900]
    )

    def show_alert_dialog(title, message, actions=None):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=actions or [ft.TextButton("OK", on_click=lambda e: close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Load face encodings
    try:
        with open(ENCODE_FILE, 'rb') as file:
            encode_list_known, roll_numbers = pickle.load(file)
        logging.debug(f"Loaded {len(encode_list_known)} encodings from {ENCODE_FILE}")
        if not encode_list_known:
            show_alert_dialog("Error", "No face encodings found in EncodeFile.p")
            return
    except Exception as e:
        show_alert_dialog("Error", f"Failed to load encodings: {str(e)}")
        return

    # Dropdown for selecting a course and section
    course_dropdown = ft.Dropdown(
        label="Course and Section",
        hint_text="Select a course and section",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        bgcolor=ft.colors.with_opacity(1, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.BOOK,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )

    # Text control for status messages
    status_text = ft.Text("", color=ft.colors.GREEN_400, size=16, text_align=ft.TextAlign.CENTER)

    def clear_status_text():
        status_text.value = ""
        page.update()

    def set_status_text(message, duration=3):
        status_text.value = message
        page.update()
        threading.Timer(duration, clear_status_text).start()

    def fetch_teacher_courses():
        logging.debug("Fetching teacher courses")
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            query = """
                SELECT e.CourseID, e.SectionID, c.CourseCode, c.CourseName, s.Name
                FROM enrollment e
                JOIN course c ON e.CourseID = c.CourseID
                JOIN section s ON e.SectionID = s.SectionID
                WHERE e.Teacher_ID = %s
            """
            cursor.execute(query, (teacher_id,))
            courses = cursor.fetchall()
            conn.close()
            course_dropdown.options = [
                ft.dropdown.Option(
                    key=f"{course[0]}:{course[1]}",
                    text=f"{course[2]} - {course[3]} (Section: {course[4]})"
                ) for course in courses
            ]
            page.update()
            logging.debug("Finished fetching teacher courses")
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")

    def fetch_students(course_id, section_id):
        logging.debug(f"Fetching students for CourseID {course_id}, SectionID {section_id}")
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            query = """
                SELECT s.Roll_no
                FROM student s
                WHERE s.SectionID = %s
            """
            cursor.execute(query, (section_id,))
            students = [row[0] for row in cursor.fetchall()]
            conn.close()
            logging.debug(f"Fetched students: {students}")
            return students
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")
            return []

    def fetch_student_details(roll_no):
        logging.debug(f"Fetching details for Roll No {roll_no}")
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Roll_no, Full_Name FROM student WHERE Roll_no=%s", (roll_no,))
            result = cursor.fetchone()
            conn.close()
            if result:
                logging.debug(f"Found student: {result}")
                return result[0], result[1]
            logging.debug(f"No student found for Roll No {roll_no}")
            return roll_no, "Unknown"
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")
            return roll_no, "Unknown"

    def check_if_already_marked(roll_no, course_id, section_id, teacher_id):
        logging.debug(f"Checking if attendance already marked for Roll No {roll_no}")
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) FROM attendance
                WHERE Roll_no=%s 
                AND CourseID=%s 
                AND SectionID=%s 
                AND Teacher_ID=%s 
                AND DATE(Attendance_Date)=CURDATE()
            """
            cursor.execute(query, (roll_no, course_id, section_id, teacher_id))
            count = cursor.fetchone()[0]
            conn.close()
            logging.debug(f"Attendance marked: {'Yes' if count > 0 else 'No'}")
            return count > 0
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")
            return False

    def mark_attendance(roll_no, course_id, section_id, status, name):
        logging.debug(f"Marking attendance for Roll No {roll_no}, Status: {status}")
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            now = datetime.now()
            date = now.date()
            time = now.time()
            cursor.execute("""
                INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Date, Attendance_Time, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (teacher_id, course_id, section_id, roll_no, date, time, status))
            conn.commit()
            conn.close()
            logging.info(f"Marked {status} for Roll No: {roll_no}")
            if status == "Present":
                run_in_thread(play_beep_sound)  # Run in thread
                run_in_thread(play_tts_message, f"Attendance marked for {name}")  # Run in thread
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")

    def complete_attendance(e):
        logging.debug("Complete Attendance button clicked")
        if not course_dropdown.value:
            show_alert_dialog("Error", "Please select a course and section!")
            return

        def handle_send_email(e):
            page.overlay[-1].open = False  # Close dialog
            page.update()
            send_attendance_email()

        def handle_modify_attendance(e):
            page.overlay[-1].open = False  # Close dialog
            page.controls.clear()
            main_manage(page, teacher_id)  # Navigate to manage attendance
            page.update()

        # Show confirmation dialog
        show_alert_dialog(
            "Complete Attendance",
            "Do you want to send the attendance email or modify the attendance?",
            actions=[
                ft.TextButton("Send Email", on_click=handle_send_email),
                ft.TextButton("Modify Attendance", on_click=handle_modify_attendance),
            ]
        )

    def send_attendance_email():
        logging.debug("Generating and sending attendance email")
        if not course_dropdown.value:
            show_alert_dialog("Error", "Please select a course and section!")
            return

        try:
            import openpyxl  # Check if openpyxl is available
        except ImportError:
            logging.error("openpyxl module not found")
            show_alert_dialog(
                "Error",
                "Required module 'openpyxl' not found. Please install it using 'pip install openpyxl'."
            )
            return

        try:
            # Retrieve teacher's email
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Email, Full_Name FROM teachers WHERE Teacher_ID = %s", (teacher_id,))
            teacher_result = cursor.fetchone()
            if not teacher_result or not teacher_result[0]:
                conn.close()
                show_alert_dialog("Error", "Teacher's email address not found in the database.")
                return
            teacher_email, teacher_name = teacher_result

            # Fetch attendance data for current date
            course_id, section_id = map(int, course_dropdown.value.split(":"))
            current_date = datetime.now().strftime("%Y-%m-%d")
            query = """
                SELECT s.Roll_no, s.Full_Name, a.Status, a.Attendance_Time
                FROM student s
                LEFT JOIN attendance a ON s.Roll_no = a.Roll_no
                    AND a.Teacher_ID = %s
                    AND a.CourseID = %s
                    AND a.SectionID = %s
                    AND a.Attendance_Date = %s
                WHERE s.SectionID = %s
            """
            params = (teacher_id, course_id, section_id, current_date, section_id)
            cursor.execute(query, params)
            students = cursor.fetchall()
            conn.close()

            if not students:
                show_alert_dialog("No Data", f"No attendance records found for {current_date}.")
                return

            # Prepare data for Excel
            data = []
            for roll_no, full_name, status, attendance_time in students:
                data.append({
                    "Roll No": roll_no,
                    "Name": full_name,
                    "Status": status if status else "Absent",
                    "Time": str(attendance_time) if attendance_time else "Not Recorded"
                })

            # Create DataFrame
            df = pd.DataFrame(data)

            # Generate course and section name for filename
            course_name = course_dropdown.options[
                [opt.key for opt in course_dropdown.options].index(f"{course_id}:{section_id}")
            ].text.replace(" - ", "_").replace(" (Section:", "_").replace(")", "").replace(" ", "_")
            filename = f"Attendance_{course_name}_{current_date}.xlsx"

            # Create Excel file in memory
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            excel_data = output.read()
            output.close()

            # Encode Excel file as base64
            encoded_file = base64.b64encode(excel_data).decode()

            # Create email with attachment
            message = Mail(
                from_email='support@mzstyle.top',
                to_emails=teacher_email,
                subject=f'Attend Smart: Attendance Report for {course_name} on {current_date}',
                html_content=f"""
                <h2>Attendance Report</h2>
                <p>Hello, <strong>{teacher_name}</strong></p>
                <p>Attached is the attendance report for <strong>{course_name} on {current_date}<?strong>.</p>
                <p>Best regards,<br>Attend Smart Team</p>
                """
            )

            # Add attachment
            attachment = Attachment(
                FileContent(encoded_file),
                FileName(filename),
                FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                Disposition('attachment')
            )
            message.attachment = attachment

            # Send email
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            if not sendgrid_api_key:
                show_alert_dialog("Error", "SendGrid API key not found. Please set the SENDGRID_API_KEY environment variable.")
                return

            sg = SendGridAPIClient(api_key=sendgrid_api_key)
            try:
                response = sg.send(message)
                logging.debug(f"Email sent to {teacher_email}: Status Code {response.status_code}")
                set_status_text(f"Attendance report emailed to {teacher_email} successfully!")
            except Exception as e:
                logging.error(f"Failed to send email: {str(e)}")
                if hasattr(e, 'body'):
                    logging.error(f"SendGrid response body: {e.body}")
                if hasattr(e, 'status_code'):
                    logging.error(f"SendGrid status code: {e.status_code}")
                show_alert_dialog("Error", f"Failed to send attendance report: {str(e)}")

        except Exception as e:
            logging.error(f"Error generating or sending Excel: {e}")
            show_alert_dialog("Error", f"Failed to send attendance report: {e}")

    stop_camera = False

    def mark_attendance_with_camera(e):
        nonlocal stop_camera
        stop_camera = False
        logging.debug("Starting mark_attendance_with_camera")

        if not course_dropdown.value:
            show_alert_dialog("Error", "Please select a course and section!")
            logging.debug("No course selected")
            return

        course_id, section_id = map(int, course_dropdown.value.split(":"))
        present_students = set()
        start_time = time.time()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            show_alert_dialog("Error", "Could not open camera!")
            logging.error("Camera could not be opened")
            return

        # Add Stop Camera button
        stop_button = ft.ElevatedButton(
            text="Stop Camera",
            on_click=lambda e: stop_camera_feed(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                bgcolor=ft.colors.RED_600,
                color=ft.colors.WHITE,
            )
        )
        page.controls.append(stop_button)
        page.update()

        def stop_camera_feed():
            nonlocal stop_camera
            stop_camera = True
            page.controls.remove(stop_button)
            page.update()
            logging.debug("Stop camera button clicked")

        while not stop_camera:
            # Check for timeout
            if time.time() - start_time > CAMERA_TIMEOUT:
                logging.warning("Camera loop timed out")
                show_alert_dialog("Timeout", "Camera session timed out after 5 minutes.")
                break

            logging.debug("Reading camera frame")
            ret, frame = cap.read()
            if not ret:
                show_alert_dialog("Error", "Failed to capture video frame!")
                logging.error("Failed to capture video frame")
                break

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            logging.debug("Detecting faces")
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]

            logging.debug(f"Detected {len(face_locations)} faces in the frame")

            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                logging.debug("Processing face encoding")
                matches = face_recognition.compare_faces(encode_list_known, face_encoding, tolerance=FACE_DISTANCE_THRESHOLD)
                face_distances = face_recognition.face_distance(encode_list_known, face_encoding)
                best_match_index = np.argmin(face_distances)

                bbox = (left, top, right - left, bottom - top)
                label = "Unknown"
                color = (0, 0, 255)

                if face_distances[best_match_index] < 0.4:
                    roll_no = roll_numbers[best_match_index]
                    logging.debug(f"Match found: Roll No {roll_no}, Distance: {face_distances[best_match_index]}")
                    students_in_section = fetch_students(course_id, section_id)
                    if roll_no in students_in_section:
                        roll_no, name = fetch_student_details(roll_no)
                        label = f"ID: {roll_no} ({name})"
                        color = (0, 255, 0)
                        if roll_no not in present_students:
                            if not check_if_already_marked(roll_no, course_id, section_id, teacher_id):
                                present_students.add(roll_no)
                                logging.debug(f"Marking attendance for Roll No {roll_no}")
                                mark_attendance(roll_no, course_id, section_id, "Present", name)
                                set_status_text(f"Marked Present for Roll No: {roll_no}")
                            else:
                                logging.debug(f"Roll No {roll_no} already marked today")
                    else:
                        logging.debug(f"Roll No {roll_no} not in section {section_id}")
                        label = "Unknown"
                        color = (0, 0, 255)
                else:
                    logging.debug("No match found for face")

                cvzone.cornerRect(frame, bbox, rt=0, colorR=color)
                x, y, w, h = bbox
                cvzone.putTextRect(frame, label, (x, y - 20), scale=1, thickness=2, colorR=color)

            logging.debug("Displaying frame")
            cv2.imshow("Face Recognition Attendance", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.debug("Quit key pressed")
                stop_camera = True

        logging.debug("Releasing camera")
        cap.release()
        cv2.destroyAllWindows()
        page.controls.remove(stop_button)
        page.update()
        logging.debug("Camera loop ended")

    # Mark Attendance button
    mark_button = ft.ElevatedButton(
        text="Mark Attendance",
        on_click=mark_attendance_with_camera,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=primary_color,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )

    # Complete Attendance button
    complete_button = ft.ElevatedButton(
        text="Complete Attendance",
        on_click=complete_attendance,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=primary_color,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )

    # Card layout
    card = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Mark Attendance",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Select a course and section to mark attendance",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Column(
                    [
                        course_dropdown,
                        ft.Row(
                            [mark_button, complete_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        status_text,
                    ],
                    spacing=15,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(
            blur_radius=30,
            spread_radius=5,
            color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
        ),
        animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
        scale=ft.transform.Scale(scale=1.0),
        on_hover=lambda e: e.control.update(
            scale=ft.transform.Scale(scale=1.02 if e.data == "true" else 1.0)
        ),
    )

    # Background with radial gradient and Back button
    background = ft.Container(
        content=ft.Stack(
            [
                card,
                ft.Container(
                    content=create_back_button(
                        page,
                        teacher_dashboard,
                        primary_color=primary_color,
                        teacher_id=teacher_id
                    ),
                    top=10,
                    left=0,
                ),
            ]
        ),
        alignment=ft.alignment.center,
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.Alignment(0, 0),
            radius=2.0,
            colors=[
                ft.colors.with_opacity(0.4, primary_color),
                ft.colors.with_opacity(0.2, accent_color),
                ft.colors.with_opacity(0.1, ft.colors.BLUE_GREY_900),
            ],
        ),
    )

    page.controls.clear()
    page.add(background)
    fetch_teacher_courses()
    page.update()

if __name__ == "__main__":
    ft.app(target=lambda page: main(page, teacher_id=1))