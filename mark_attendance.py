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

# Constants
ENCODE_FILE = "EncodeFile.p"
FACE_DISTANCE_THRESHOLD = 0.6  # Increased to allow more matches
SOUND_FILE = "beep.wav"  # Optional: Provide a .wav file for non-Windows systems

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Slower speech

def play_beep_sound():
    if platform.system() == "Windows":
        winsound.Beep(1000, 200)  # Frequency 1000 Hz, duration 200 ms
    else:
        try:
            if os.path.exists(SOUND_FILE):
                os.system(f"aplay {SOUND_FILE}")  # Linux (requires aplay)
            else:
                logging.warning("Sound file not found for non-Windows system.")
        except Exception as e:
            logging.error(f"Failed to play sound: {str(e)}")

def play_tts_message(message):
    try:
        tts_engine.say(message)
        tts_engine.runAndWait()
    except Exception as e:
        logging.error(f"Failed to play TTS message: {str(e)}")

def main(page: ft.Page, teacher_id=1):  # Default teacher_id=1 (Kasloom) for standalone testing
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.debug("Starting mark attendance application")

    # Window settings
    page.title = "Mark Attendance - Face Recognition System"
    page.window_width = 1920
    page.window_height = 1080
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # Colors
    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900]
    )

    def show_alert_dialog(title, message):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog())],
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

    def fetch_teacher_courses():
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
                    key=f"{course[0]}:{course[1]}",  # CourseID:SectionID
                    text=f"{course[2]} - {course[3]} (Section: {course[4]})"
                ) for course in courses
            ]
            page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")

    def fetch_students(course_id, section_id):
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
            logging.debug(f"Fetched students for SectionID {section_id}: {students}")
            return students
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")
            return []

    def fetch_student_details(roll_no):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Roll_no, Full_Name FROM student WHERE Roll_no=%s", (roll_no,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0], result[1]  # Roll_no, Name
            return roll_no, "Unknown"
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")
            return roll_no, "Unknown"

    def check_if_already_marked(roll_no, course_id, section_id, teacher_id):
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
            logging.debug(f"Checked if already marked for Roll No {roll_no}: {'Yes' if count > 0 else 'No'}")
            return count > 0
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")
            return False

    def mark_attendance(roll_no, course_id, section_id, status, name):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            now=datetime.now()
            date=now.date()
            time=now.time()
            cursor.execute("""
                INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Date, Attendance_Time, Status)
                VALUES (%s, %s, %s, %s,%s, %s, %s)
            """, (teacher_id, course_id, section_id, roll_no, date,time, status))
            conn.commit()
            conn.close()
            logging.info(f"Marked {status} for Roll No: {roll_no}")
            if status == "Present":
                play_beep_sound()  # Play beep sound
                play_tts_message(f"Attendance marked for {name}")  # Play TTS message
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Error", f"Database Error: {err}")

    def mark_attendance_with_camera(e):
        if not course_dropdown.value:
            show_alert_dialog("Error", "Please select a course and section!")
            return

        course_id, section_id = map(int, course_dropdown.value.split(":"))
        present_students = set()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            show_alert_dialog("Error", "Could not open camera!")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                show_alert_dialog("Error", "Failed to capture video frame!")
                break

            # Convert frame to RGB (no resizing for better detection)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find faces in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            logging.debug(f"Detected {len(face_locations)} faces in the frame")

            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                # Compare with known encodings
                matches = face_recognition.compare_faces(encode_list_known, face_encoding, tolerance=FACE_DISTANCE_THRESHOLD)
                face_distances = face_recognition.face_distance(encode_list_known, face_encoding)
                best_match_index = np.argmin(face_distances)

                # Prepare bounding box for cvzone
                bbox = (left, top, right - left, bottom - top)
                label = "Unknown"
                color = (0, 0, 255)  # Red for unrecognized

                if matches[best_match_index]:
                    roll_no = roll_numbers[best_match_index]
                    logging.debug(f"Match found: Roll No {roll_no}, Distance: {face_distances[best_match_index]}")
                    # Verify the student belongs to the selected section
                    students_in_section = fetch_students(course_id, section_id)
                    if roll_no in students_in_section:
                        # Fetch student details only if in section
                        roll_no, name = fetch_student_details(roll_no)
                        label = f"ID: {roll_no} ({name})"
                        color = (0, 255, 0)  # Green for recognized and in section
                        if roll_no not in present_students:
                            # Check if already marked today for this course and teacher
                            if not check_if_already_marked(roll_no, course_id, section_id, teacher_id):
                                present_students.add(roll_no)
                                mark_attendance(roll_no, course_id, section_id, "Present", name)
                                show_alert_dialog("Success", f"Marked Present for Roll No: {roll_no}")
                            else:
                                logging.debug(f"Roll No {roll_no} already marked today, skipping.")
                    else:
                        logging.debug(f"Student {roll_no} not enrolled in this section (SectionID: {section_id})")
                        # Treat as Unknown, do not fetch or display details
                        label = "Unknown"
                        color = (0, 0, 255)  # Red for recognized but not in section
                else:
                    logging.debug("No match found for detected face")

                # Draw cornered rectangle and text using cvzone
                cvzone.cornerRect(frame, bbox, rt=0, colorR=color)
                x, y, w, h = bbox
                cvzone.putTextRect(frame, label, (x, y - 20), scale=1, thickness=2, colorR=color)

            # Display the video feed
            cv2.imshow("Face Recognition Attendance", frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()

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
                            [mark_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
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

    # Background with radial gradient
    background = ft.Container(
        content=card,
        alignment=ft.alignment.center,
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.Alignment(0, 0),
            radius=2.0,
            colors=[
                ft.colors.with_opacity(0.4, primary_color),
                ft.colors.with_opacity(0.2, accent_color),
                ft.colors.BLACK,
            ],
        ),
    )

    page.controls.clear()
    page.add(background)
    fetch_teacher_courses()
    page.update()

if __name__ == "__main__":
    ft.app(target=lambda page: main(page, teacher_id=1))