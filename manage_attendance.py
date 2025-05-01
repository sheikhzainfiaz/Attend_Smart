import flet as ft
import mysql.connector
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main_manage(page: ft.Page,teacher_id=1):
    page.title = "Attendance Management - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

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

    # Dummy Teacher_ID for testing
    DUMMY_TEACHER_ID = teacher_id  # Kasloom from your sample data

    # Dropdowns
    course_dropdown = ft.Dropdown(
        label="Select Course",
        options=[],
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_change=lambda e: update_section_dropdown()
    )

    section_dropdown = ft.Dropdown(
        label="Select Section",
        options=[],
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_change=lambda e: update_table()
    )

    # Date input
    selected_date = ft.Ref[str]()
    selected_date.current = datetime.now().strftime("%Y-%m-%d")  # Today's date (2025-05-01)

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

    # Data table for students and attendance (view-only)
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
        ],
        rows=[]
    )

    def update_course_dropdown():
        course_dropdown.options = []
        section_dropdown.options = []
        data_table.rows = []
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT c.CourseID, c.CourseName
                FROM course c
                JOIN enrollment e ON c.CourseID = e.CourseID
                WHERE e.Teacher_ID = %s
            """, (DUMMY_TEACHER_ID,))
            courses = cursor.fetchall()
            conn.close()
            course_dropdown.options = [
                ft.dropdown.Option(key=str(course_id), text=course_name)
                for course_id, course_name in courses
            ]
            page.update()
            update_section_dropdown()
        except Exception as e:
            show_alert_dialog("Error", f"Error fetching courses: {e}")

    def update_section_dropdown():
        section_dropdown.options = []
        data_table.rows = []
        if not course_dropdown.value:
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT s.SectionID, s.Name
                FROM section s
                JOIN enrollment e ON s.SectionID = e.SectionID
                WHERE e.Teacher_ID = %s AND e.CourseID = %s
            """, (DUMMY_TEACHER_ID, course_dropdown.value))
            sections = cursor.fetchall()
            conn.close()
            section_dropdown.options = [
                ft.dropdown.Option(key=str(section_id), text=section_name)
                for section_id, section_name in sections
            ]
            page.update()
            update_table()
        except Exception as e:
            show_alert_dialog("Error", f"Error fetching sections: {e}")

    def update_table():
        logging.debug("Updating table...")
        data_table.rows = []  # Clear existing rows

        # Use date_input.value instead of selected_date.current
        date_value = date_input.value
        logging.debug(f"Fetching data for date: {date_value}")

        # Validate the date before proceeding
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

        # Synchronize selected_date.current with date_input.value
        selected_date.current = date_value
        logging.debug(f"Synchronized selected_date.current to: {selected_date.current}")

        if not all([course_dropdown.value, section_dropdown.value]):
            logging.debug("Missing required fields for table update (course or section).")
            page.update()
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            query = """
                SELECT s.Roll_no, s.Full_Name, a.Status
                FROM student s
                LEFT JOIN attendance a ON s.Roll_no = a.Roll_no
                    AND a.Teacher_ID = %s
                    AND a.CourseID = %s
                    AND a.SectionID = %s
                    AND a.Attendance_Date = %s
                WHERE s.SectionID = %s
            """
            params = (DUMMY_TEACHER_ID, course_dropdown.value, section_dropdown.value, date_value, section_dropdown.value)
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
            
            for roll_no, full_name, status in students:
                status_text = status if status else "Not Recorded"
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(roll_no, color=ft.colors.WHITE)),
                            ft.DataCell(ft.Text(full_name, color=ft.colors.WHITE)),
                            ft.DataCell(ft.Text(status_text, color=ft.colors.WHITE)),
                        ]
                    )
                )
            logging.debug(f"Table updated with {len(data_table.rows)} rows")
            page.update()
        except Exception as e:
            logging.debug(f"Error fetching data: {e}")
            show_alert_dialog("Error", f"Error fetching students: {e}")

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
            ft.Text("Attendance Management", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            course_dropdown,
            section_dropdown,
            btns,
            ft.Container(
                content=ft.Column([
                    data_table
                ], scroll=ft.ScrollMode.AUTO),
                padding=10,
                bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                border_radius=10,
                height=350,
                alignment=ft.alignment.center,
                width=750
            )
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, spread_radius=5, color=ft.colors.with_opacity(0.3, ft.colors.BLACK))
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
    update_course_dropdown()

