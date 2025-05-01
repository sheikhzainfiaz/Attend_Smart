import flet as ft
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main(page: ft.Page):
    page.title = "Enrollment Management - Face Recognition System"
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

    # Dropdown for Teacher_ID
    teacher_dropdown = ft.Dropdown(
        label="Teacher",
        hint_text="Select a teacher",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.PERSON,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )

    # Dropdown for CourseID
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
    )

    # Dropdown for SectionID
    section_dropdown = ft.Dropdown(
        label="Section",
        hint_text="Select a section",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.CLASS_,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )

    # Search field
    search_field = ft.TextField(
        label="Search by Teacher Name",
        hint_text="Enter teacher name",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.SEARCH,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_change=lambda e: update_table(e.control.value.strip()),
        width=720,
    )

    # Data table
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
            ft.DataColumn(ft.Text("Teacher Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Course Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Section Name", color=ft.colors.WHITE)),
        ],
        rows=[]
    )

    selected_ids = ft.Ref[dict]()

    def clear_form():
        teacher_dropdown.value = None
        course_dropdown.value = None
        section_dropdown.value = None
        search_field.value = ""
        selected_ids.current = None
        update_table()
        page.update()

    def fetch_dropdown_data():
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()

            # Fetch teachers
            cursor.execute("SELECT Teacher_ID, Full_Name FROM teachers")
            teachers = cursor.fetchall()
            teacher_dropdown.options = [ft.dropdown.Option(key=str(t[0]), text=f"{t[0]} - {t[1]}") for t in teachers]

            # Fetch courses
            cursor.execute("SELECT CourseID, CourseCode, CourseName FROM course")
            courses = cursor.fetchall()
            course_dropdown.options = [ft.dropdown.Option(key=str(c[0]), text=f"{c[1]} - {c[2]}") for c in courses]

            # Fetch sections
            cursor.execute("SELECT SectionID, Name FROM section")
            sections = cursor.fetchall()
            section_dropdown.options = [ft.dropdown.Option(key=str(s[0]), text=f"{s[0]} - {s[1]}") for s in sections]

            conn.close()
            page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)

    def fetch_enrollments(search_term=""):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            if search_term:
                query = """
                    SELECT e.Teacher_ID, e.CourseID, e.SectionID, t.Full_Name, c.CourseName, s.Name
                    FROM enrollment e
                    JOIN teachers t ON e.Teacher_ID = t.Teacher_ID
                    JOIN course c ON e.CourseID = c.CourseID
                    JOIN section s ON e.SectionID = s.SectionID
                    WHERE t.Full_Name LIKE %s
                """
                cursor.execute(query, (f"%{search_term}%",))
            else:
                query = """
                    SELECT e.Teacher_ID, e.CourseID, e.SectionID, t.Full_Name, c.CourseName, s.Name
                    FROM enrollment e
                    JOIN teachers t ON e.Teacher_ID = t.Teacher_ID
                    JOIN course c ON e.CourseID = c.CourseID
                    JOIN section s ON e.SectionID = s.SectionID
                """
                cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            logging.debug(f"Fetched {len(data)} enrollments")
            return data
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            return []

    def update_table(search_term=""):
        data_table.rows.clear()
        for row in fetch_enrollments(search_term):
            teacher_id, course_id, section_id, teacher_name, course_name, section_name = row
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(teacher_name, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(course_name, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(section_name, color=ft.colors.WHITE)),
                    ],
                    on_select_changed=lambda e, tid=teacher_id, cid=course_id, sid=section_id: select_enrollment(tid, cid, sid)
                )
            )
        logging.debug(f"Table updated with {len(data_table.rows)} rows")
        page.update()

    def select_enrollment(teacher_id, course_id, section_id):
        selected_ids.current = {"Teacher_ID": teacher_id, "CourseID": course_id, "SectionID": section_id}
        teacher_dropdown.value = str(teacher_id)
        course_dropdown.value = str(course_id)
        section_dropdown.value = str(section_id)
        show_message("Enrollment selected for editing")
        logging.debug("Form populated with selected enrollment data")
        page.update()

    def add_enrollment(e):
        if not all([teacher_dropdown.value, course_dropdown.value, section_dropdown.value]):
            show_message("All fields are required!", is_error=True)
            logging.warning("Add failed: Missing required fields")
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO enrollment (Teacher_ID, CourseID, SectionID) VALUES (%s, %s, %s)",
                (teacher_dropdown.value, course_dropdown.value, section_dropdown.value)
            )
            conn.commit()
            conn.close()
            show_message("Enrollment added successfully!")
            logging.info(f"Added enrollment: Teacher {teacher_dropdown.value}, Course {course_dropdown.value}, Section {section_dropdown.value}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    def update_enrollment(e):
        if not selected_ids.current:
            show_message("Please select an enrollment to update!", is_error=True)
            logging.warning("Update failed: No enrollment selected")
            page.update()
            return
        if not all([teacher_dropdown.value, course_dropdown.value, section_dropdown.value]):
            show_message("All fields are required!", is_error=True)
            logging.warning("Update failed: Missing required fields")
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE enrollment SET Teacher_ID=%s, CourseID=%s, SectionID=%s WHERE Teacher_ID=%s AND CourseID=%s AND SectionID=%s",
                (
                    teacher_dropdown.value,
                    course_dropdown.value,
                    section_dropdown.value,
                    selected_ids.current["Teacher_ID"],
                    selected_ids.current["CourseID"],
                    selected_ids.current["SectionID"]
                )
            )
            conn.commit()
            conn.close()
            show_message("Enrollment updated successfully!")
            logging.info(f"Updated enrollment: Teacher {teacher_dropdown.value}, Course {course_dropdown.value}, Section {section_dropdown.value}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    def delete_enrollment(e):
        if not selected_ids.current:
            show_message("Please select an enrollment to delete!", is_error=True)
            logging.warning("Delete failed: No enrollment selected")
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM enrollment WHERE Teacher_ID=%s AND CourseID=%s AND SectionID=%s",
                (
                    selected_ids.current["Teacher_ID"],
                    selected_ids.current["CourseID"],
                    selected_ids.current["SectionID"]
                )
            )
            conn.commit()
            conn.close()
            show_message("Enrollment deleted successfully!")
            logging.info(f"Deleted enrollment: Teacher {selected_ids.current['Teacher_ID']}, Course {selected_ids.current['CourseID']}, Section {selected_ids.current['SectionID']}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    add_btn = ft.ElevatedButton(
        text="Add Enrollment",
        on_click=add_enrollment,
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
    update_btn = ft.ElevatedButton(
        text="Update",
        on_click=update_enrollment,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.colors.AMBER_600,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )
    delete_btn = ft.ElevatedButton(
        text="Delete",
        on_click=delete_enrollment,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.colors.RED_600,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )
    clear_btn = ft.ElevatedButton(
        text="Clear",
        on_click=lambda e: clear_form(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.colors.GREY_600,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )

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
                    "Enrollment Management",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Add, update, or delete enrollment records",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Column(
                    [
                        teacher_dropdown,
                        course_dropdown,
                        section_dropdown,
                        ft.Row(
                            [add_btn, update_btn, delete_btn, clear_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                search_field,
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
            center=ft.Alignment(0, -0.8),
            radius=1.5,
            colors=[
                ft.colors.with_opacity(0.2, primary_color),
                ft.colors.with_opacity(0.1, accent_color),
                ft.colors.BLACK,
            ],
        ),
    )

    page.add(background)
    fetch_dropdown_data()
    update_table()

if __name__ == "__main__":
    ft.app(target=main)