import flet as ft
import mysql.connector
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def show_manage_attendance_page(page: ft.Page, teacher_id: int, on_back):
    page.controls.clear()
    page.title = "Manage Attendance - Face Recognition System"
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

    def show_message(message, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(
                message,
                color=ft.colors.WHITE,
                weight=ft.FontWeight.W_500,
                size=14,
            ),
            bgcolor=ft.colors.RED_600 if is_error else ft.colors.GREEN_600,
            duration=3000,
            padding=10,
        )
        page.snack_bar.open = True
        page.update()

    # Date Picker
    date_picker = ft.DatePicker(
        on_change=lambda e: update_attendance_table(),
        first_date=datetime(2020, 1, 1),
        last_date=datetime.now(),
        field_label_text="Select Date",
    )
    page.overlay.append(date_picker)

    date_button = ft.ElevatedButton(
        "Pick Date",
        icon=ft.icons.CALENDAR_TODAY,
        on_click=lambda e: date_picker.pick_date(),
        style=ft.ButtonStyle(
            bgcolor=primary_color,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=15,
        ),
    )

    # Dropdown for selecting a course the teacher teaches
    course_dropdown = ft.Dropdown(
        label="Course",
        hint_text="Select a course",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.BOOK,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
        on_change=lambda e: update_attendance_table(),
    )

    # Data table to display attendance records
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
            ft.DataColumn(ft.Text("Attendance ID", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Roll No", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Full Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Course Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Section Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Status", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Timestamp", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Action", color=ft.colors.WHITE)),
        ],
        rows=[],
    )

    def fetch_teacher_courses():
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="face_db", port=3306
            )
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
            show_message(f"Database Error: {err}", is_error=True)

    def fetch_attendance_records(course_id=None, section_id=None, selected_date=None):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="face_db", port=3306
            )
            cursor = conn.cursor()
            if course_id and section_id and selected_date:
                query = """
                    SELECT a.AttendanceID, a.Roll_no, s.Full_Name, c.CourseName, sec.Name, a.Status, a.Attendance_Timestamp
                    FROM attendance a
                    JOIN student s ON a.Roll_no = s.Roll_no
                    JOIN course_help c ON a.CourseID = c.CourseID
                    JOIN section sec ON a.SectionID = sec.SectionID
                    WHERE a.Teacher_ID = %s AND a.CourseID = %s AND a.SectionID = %s
                    AND DATE(a.Attendance_Timestamp) = %s
                """
                cursor.execute(query, (teacher_id, course_id, section_id, selected_date))
            elif course_id and section_id:
                query = """
                    SELECT a.AttendanceID, a.Roll_no, s.Full_Name, c.CourseName, sec.Name, a.Status, a.Attendance_Timestamp
                    FROM attendance a
                    JOIN student s ON a.Roll_no = s.Roll_no
                    JOIN course c ON a.CourseID = c.CourseID
                    JOIN section sec ON a.SectionID = sec.SectionID
                    WHERE a.Teacher_ID = %s AND a.CourseID = %s AND a.SectionID = %s
                """
                cursor.execute(query, (teacher_id, course_id, section_id))
            else:
                query = """
                    SELECT a.AttendanceID, a.Roll_no, s.Full_Name, c.CourseName, sec.Name, a.Status, a.Attendance_Timestamp
                    FROM attendance a
                    JOIN student s ON a.Roll_no = s.Roll_no
                    JOIN course c ON a.CourseID = c.CourseID
                    JOIN section sec ON a.SectionID = sec.SectionID
                    WHERE a.Teacher_ID = %s
                """
                cursor.execute(query, (teacher_id,))
            records = cursor.fetchall()
            conn.close()
            logging.debug(f"Fetched {len(records)} attendance records")
            return records
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            return []

    def update_attendance_table():
        data_table.rows.clear()
        selected_date = date_picker.value.strftime("%Y-%m-%d") if date_picker.value else None
        if not course_dropdown.value:
            records = fetch_attendance_records(selected_date=selected_date)
        else:
            course_id, section_id = map(int, course_dropdown.value.split(":"))
            records = fetch_attendance_records(course_id, section_id, selected_date)
        for record in records:
            attendance_id, roll_no, full_name, course_name, section_name, status, timestamp = record
            delete_btn = ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color=ft.colors.RED_600,
                on_click=lambda e, aid=attendance_id: delete_attendance(aid),
            )
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(attendance_id), color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(roll_no, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(full_name, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(course_name, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(section_name, color=ft.colors.WHITE)),
                        ft.DataCell(
                            ft.Text(
                                status,
                                color=ft.colors.GREEN_400 if status == "Present" else ft.colors.RED_400,
                            )
                        ),
                        ft.DataCell(ft.Text(str(timestamp), color=ft.colors.WHITE)),
                        ft.DataCell(delete_btn),
                    ]
                )
            )
        page.update()

    def delete_attendance(attendance_id):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="face_db", port=3306
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE AttendanceID = %s", (attendance_id,))
            conn.commit()
            conn.close()
            show_message("Attendance record deleted successfully!")
            logging.info(f"Deleted attendance record: {attendance_id}")
            update_attendance_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    data_table_container = ft.Container(
        content=ft.Column(
            [data_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        padding=10,
        expand=True,
        alignment=ft.alignment.center,
        height=300,
    )

    card = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Manage Attendance",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "View and manage attendance records",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Row(
                    [date_button, course_dropdown],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Back to Dashboard",
                            on_click=on_back,
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
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                data_table_container,
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

    page.add(background)
    fetch_teacher_courses()
    update_attendance_table()
    page.update()