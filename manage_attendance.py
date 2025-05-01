import flet as ft
import mysql.connector
import logging
from datetime import datetime
import re
import threading

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main_manage(page: ft.Page, teacher_id=1):
    page.title = "Attendance Management - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 1920
    page.window_height = 800

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

    def go_back(e):
        if len(page.views) > 1:  # Ensure there's a previous view to go back to
            page.views.pop()  # Remove the current view
            page.go(page.views[-1].route)  # Navigate to the previous view
        else:
            show_alert_dialog("Info", "No previous page to go back to.")

    # Dummy Teacher_ID for testing
    DUMMY_TEACHER_ID = teacher_id

    # Single Dropdown for Course and Section
    course_section_dropdown = ft.Dropdown(
        label="Select Course and Section",
        options=[],
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
        on_change=lambda e: update_table()
    )

    # Date input
    selected_date = ft.Ref[str]()
    selected_date.current = datetime.now().strftime("%Y-%m-%d")

    date_input = ft.TextField(
        label="Select Date (YYYY-MM-DD)",
        value=selected_date.current,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_submit=lambda e: update_selected_date(e.control.value)
    )

    # Status message
    status_text = ft.Text("", color=ft.colors.GREEN_400, size=16, text_align=ft.TextAlign.CENTER)

    def clear_status_text():
        status_text.value = ""
        page.update()

    def set_status_text(message, duration=3):
        status_text.value = message
        page.update()
        threading.Timer(duration, clear_status_text).start()

    def update_selected_date(date_value):
        logging.debug(f"Date input changed to: {date_value}")
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not date_value or not re.match(date_pattern, date_value):
            show_alert_dialog("Invalid Date", "Please enter date in YYYY-MM-DD format (e.g., 2025-05-01).")
            date_input.value = selected_date.current
            page.update()
            return
        
        try:
            year, month, day = map(int, date_value.split("-"))
            datetime(year, month, day)
            if year < 2023 or year > 2025:
                show_alert_dialog("Invalid Date", "Please select a date between 2023 and 2025.")
                date_input.value = selected_date.current
                page.update()
                return
            
            selected_date.current = date_value
            date_input.value = selected_date.current
            logging.debug(f"Date updated to: {selected_date.current}")
            update_table()
        except ValueError:
            show_alert_dialog("Invalid Date", "Please enter a valid date (e.g., 2025-05-01).")
            date_input.value = selected_date.current
        page.update()

    # Data table for students and attendance (editable)
    data_table = ft.DataTable(
        border=ft.Border(
            top=ft.BorderSide(1, ft.colors.BLUE_200),
            bottom=ft.BorderSide(1, ft.colors.BLUE_200),
            left=ft.BorderSide(1, ft.colors.BLUE_200),
            right=ft.BorderSide(1, ft.colors.BLUE_200),
        ),
        heading_row_color=ft.colors.with_opacity(0.1, ft.colors.BLUE_600),
        heading_text_style=ft.TextStyle(color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
        columns=[
            ft.DataColumn(ft.Text("Roll No", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Status", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Time", color=ft.colors.WHITE)),
        ],
        rows=[]
    )

    def update_course_section_dropdown():
        course_section_dropdown.options = []
        data_table.rows = []
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_db",
                port=3306
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.CourseID, c.CourseName, e.SectionID, s.Name
                FROM enrollment e
                JOIN course c ON e.CourseID = c.CourseID
                JOIN section s ON e.SectionID = s.SectionID
                WHERE e.Teacher_ID = %s
            """, (DUMMY_TEACHER_ID,))
            course_sections = cursor.fetchall()
            conn.close()
            course_section_dropdown.options = [
                ft.dropdown.Option(
                    key=f"{course_id}:{section_id}",
                    text=f"{course_name} - {section_name}"
                )
                for course_id, course_name, section_id, section_name in course_sections
            ]
            page.update()
            update_table()
        except Exception as e:
            show_alert_dialog("Error", f"Error fetching courses and sections: {e}")
            logging.error(f"Error fetching courses and sections: {e}")

    def update_attendance(roll_no, course_id, section_id, new_status, old_status):
        logging.debug(f"Updating attendance for Roll No: {roll_no}, New Status: {new_status}, Old Status: {old_status}")
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_db",
                port=3306
            )
            cursor = conn.cursor()
            
            if new_status == "Not Recorded":
                cursor.execute("""
                    DELETE FROM attendance
                    WHERE Roll_no = %s
                    AND Teacher_ID = %s
                    AND CourseID = %s
                    AND SectionID = %s
                    AND Attendance_Date = %s
                """, (roll_no, DUMMY_TEACHER_ID, course_id, section_id, selected_date.current))
                conn.commit()
                logging.debug(f"Deleted attendance record for Roll No: {roll_no}")
                set_status_text(f"Attendance removed for Roll No: {roll_no}")
            
            elif old_status == "Not Recorded":
                now = datetime.now()
                cursor.execute("""
                    INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Date, Attendance_Time, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (DUMMY_TEACHER_ID, course_id, section_id, roll_no, selected_date.current, now.time(), new_status))
                conn.commit()
                logging.debug(f"Inserted new attendance record for Roll No: {roll_no}, Status: {new_status}")
                set_status_text(f"Attendance set to {new_status} for Roll No: {roll_no}")
            
            else:
                now = datetime.now()
                cursor.execute("""
                    UPDATE attendance
                    SET Status = %s, Attendance_Time = %s
                    WHERE Roll_no = %s
                    AND Teacher_ID = %s
                    AND CourseID = %s
                    AND SectionID = %s
                    AND Attendance_Date = %s
                """, (new_status, now.time(), roll_no, DUMMY_TEACHER_ID, course_id, section_id, selected_date.current))
                conn.commit()
                logging.debug(f"Updated attendance for Roll No: {roll_no} to Status: {new_status}")
                set_status_text(f"Attendance updated to {new_status} for Roll No: {roll_no}")

            conn.close()
            update_table()
        except Exception as e:
            logging.error(f"Error updating attendance: {e}")
            show_alert_dialog("Error", f"Failed to update attendance: {e}")

    def update_table():
        logging.debug("Updating table...")
        data_table.rows = []

        date_value = date_input.value
        logging.debug(f"Fetching data for date: {date_value}")

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not date_value or not re.match(date_pattern, date_value):
            logging.debug("Invalid date format in date_input")
            show_alert_dialog("Invalid Date", "Please enter date in YYYY-MM-DD format (e.g., 2025-05-01).")
            date_input.value = selected_date.current
            page.update()
            return
        
        try:
            year, month, day = map(int, date_value.split("-"))
            datetime(year, month, day)
            if year < 2023 or year > 2025:
                logging.debug("Date out of range")
                show_alert_dialog("Invalid Date", "Please select a date between 2023 and 2025.")
                date_input.value = selected_date.current
                page.update()
                return
        except ValueError:
            logging.debug("Invalid date value")
            show_alert_dialog("Invalid Date", "Please enter a valid date (e.g., 2025-05-01).")
            date_input.value = selected_date.current
            page.update()
            return

        selected_date.current = date_value
        logging.debug(f"Synchronized selected_date.current to: {selected_date.current}")

        if not course_section_dropdown.value:
            logging.debug("No course-section selected")
            page.update()
            return

        try:
            course_id, section_id = map(int, course_section_dropdown.value.split(":"))
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_db",
                port=3306
            )
            cursor = conn.cursor()
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
            params = (DUMMY_TEACHER_ID, course_id, section_id, date_value, section_id)
            logging.debug(f"Executing query: {query % params}")
            cursor.execute(query, params)
            students = cursor.fetchall()
            logging.debug(f"Fetched students: {students}")
            conn.close()
            
            if not students:
                logging.debug(f"No data found for date {date_value}")
                show_alert_dialog("No Data", f"No attendance records found for {date_value}.")
                page.update()
                return
            
            for roll_no, full_name, status, attendance_time in students:
                current_status = status if status else "Not Recorded"
                time_display = str(attendance_time) if attendance_time else "Not Recorded"
                status_dropdown = ft.Dropdown(
                    value=current_status,
                    options=[
                        ft.dropdown.Option("Present"),
                        ft.dropdown.Option("Absent"),
                        ft.dropdown.Option("Not Recorded")
                    ],
                    border_color=accent_color,
                    focused_border_color=primary_color,
                    text_style=ft.TextStyle(color=ft.colors.WHITE),
                    on_change=lambda e, rn=roll_no, cs=current_status: update_attendance(
                        rn, course_id, section_id, e.control.value, cs
                    )
                )
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(roll_no, color=ft.colors.WHITE)),
                            ft.DataCell(ft.Text(full_name, color=ft.colors.WHITE)),
                            ft.DataCell(status_dropdown),
                            ft.DataCell(ft.Text(time_display, color=ft.colors.WHITE)),
                        ]
                    )
                )
            logging.debug(f"Table updated with {len(data_table.rows)} rows")
            page.update()
        except Exception as e:
            logging.debug(f"Error fetching data: {e}")
            show_alert_dialog("Error", f"Error fetching students: {e}")

    # Back button
    back_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.icons.ARROW_BACK, color=ft.colors.WHITE),
            ft.Text("Back", color=ft.colors.WHITE, size=16, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        on_click=go_back,
        bgcolor=primary_color,
        style=ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=10),
        )
    )

    # Buttons
    btns = ft.Row([
        date_input,
        ft.ElevatedButton(
            "Fetch",
            on_click=lambda e: update_table(),
            bgcolor=primary_color,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
            )
        ),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    card = ft.Container(
        content=ft.Column([
            ft.Row([back_button], alignment=ft.MainAxisAlignment.START),  # Back button at top-left
            ft.Text("Attendance Management", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            course_section_dropdown,
            btns,
            status_text,
            ft.Container(
                content=ft.Column([
                    data_table
                ], scroll=ft.ScrollMode.AUTO),
                padding=0,
                margin=0,
                bgcolor=card_bg,
                border_radius=10,
                expand=True,
                width=750
            )
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, spread_radius=5, color=ft.colors.with_opacity(0.3, ft.colors.BLACK)),
        expand=True
    )

    background = ft.Container(
        content=card,
        alignment=ft.alignment.center,
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.Alignment(0, -0.8),
            radius=1.5,
            colors=[
                ft.colors.with_opacity(0.2, primary_color),
                ft.colors.with_opacity(0.1, accent_color),
                ft.colors.BLACK,
            ],
        )
    )

    page.add(background)
    update_course_section_dropdown()

if __name__ == "__main__":
    ft.app(target=lambda page: main_manage(page, teacher_id=1))