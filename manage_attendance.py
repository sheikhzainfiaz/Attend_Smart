import flet as ft
import mysql.connector
import logging
from datetime import datetime

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

    # Date picker
    selected_date = ft.Ref[str]()
    selected_date.current = datetime.now().strftime("%Y-%m-%d")
    
    date_picker = ft.DatePicker(
        on_change=lambda e: update_selected_date(e.control.value),
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2025, 12, 31),
        value=datetime.now()
    )
    page.overlay.append(date_picker)

    date_button = ft.ElevatedButton(
        "Select Date",
        icon=ft.icons.CALENDAR_TODAY,
        on_click=lambda e: date_picker.open(),
        bgcolor=ft.colors.BLUE_800,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            text_style=ft.TextStyle(size=14)
        )
    )

    date_display = ft.Text(
        value=selected_date.current,
        color=ft.colors.WHITE,
        size=14
    )

    def update_selected_date(date_value):
        if date_value:
            selected_date.current = date_value.strftime("%Y-%m-%d")
            date_display.value = selected_date.current
            update_table()
            page.update()

    # Data table for students and attendance
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
        data_table.rows = []
        if not all([course_dropdown.value, section_dropdown.value, selected_date.current]):
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.Roll_no, s.Full_Name, a.Status
                FROM student s
                LEFT JOIN attendance a ON s.Roll_no = a.Roll_no
                    AND a.Teacher_ID = %s
                    AND a.CourseID = %s
                    AND a.SectionID = %s
                    AND a.Attendance_Date = %s
                WHERE s.SectionID = %s
            """, (DUMMY_TEACHER_ID, course_dropdown.value, section_dropdown.value, selected_date.current, section_dropdown.value))
            students = cursor.fetchall()
            conn.close()
            
            for roll_no, full_name, status in students:
                status_text = status if status else "Absent"
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(roll_no, color=ft.colors.WHITE)),
                            ft.DataCell(ft.Text(full_name, color=ft.colors.WHITE)),
                            ft.DataCell(
                                ft.Dropdown(
                                    value=status_text,
                                    options=[
                                        ft.dropdown.Option("Present"),
                                        ft.dropdown.Option("Absent")
                                    ],
                                    border_color=accent_color,
                                    focused_border_color=primary_color,
                                    filled=True,
                                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                                    text_style=ft.TextStyle(color=ft.colors.WHITE),
                                    on_change=lambda e, rn=roll_no: update_attendance(rn, e.control.value)
                                )
                            ),
                        ]
                    )
                )
            page.update()
        except Exception as e:
            show_alert_dialog("Error", f"Error fetching students: {e}")

    def update_attendance(roll_no, status):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            # Check if attendance record exists for the selected date
            cursor.execute("""
                SELECT AttendanceID FROM attendance
                WHERE Roll_no = %s
                AND Teacher_ID = %s
                AND CourseID = %s
                AND SectionID = %s
                AND Attendance_Date = %s
            """, (roll_no, DUMMY_TEACHER_ID, course_dropdown.value, section_dropdown.value, selected_date.current))
            existing = cursor.fetchone()
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE attendance
                    SET Status = %s, Attendance_Time = %s
                    WHERE AttendanceID = %s
                """, (status, current_time, existing[0]))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO attendance (Teacher_ID, CourseID, SectionID, Roll_no, Attendance_Date, Attendance_Time, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (DUMMY_TEACHER_ID, course_dropdown.value, section_dropdown.value, roll_no, selected_date.current, current_time, status))
            
            conn.commit()
            conn.close()
            show_alert_dialog("Success", f"Attendance updated for {roll_no}")
            update_table()
        except Exception as e:
            show_alert_dialog("Error", f"Error updating attendance: {e}")

    # Buttons
    btns = ft.Row([
        date_button,
        date_display,
        ft.ElevatedButton(
            "Refresh",
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
