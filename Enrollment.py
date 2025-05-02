import flet as ft
import mysql.connector
import logging
from back_button import create_back_button
from Dash import show_main

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main(page: ft.Page):
    page.title = "Enrollment Management - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    primary_color = ft.Colors.BLUE_600
    accent_color = ft.Colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.Colors.BLUE_GREY_800, ft.Colors.BLUE_GREY_900]
    )

    def show_alert_dialog(title, message, is_success=False, is_error=False):
        logging.debug(f"Attempting to show AlertDialog: Title='{title}', Message='{message}', IsSuccess={is_success}, IsError={is_error}")
        try:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(
                    message,
                    color=ft.Colors.GREEN_600 if is_success else ft.Colors.RED_600 if is_error else ft.Colors.BLACK
                ),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.Colors.WHITE
            )

            def close_dialog():
                logging.debug("Closing AlertDialog")
                dialog.open = False
                page.update()

            page.overlay.append(dialog)
            dialog.open = True
            logging.debug("Dialog added to overlay, calling page.update()")
            page.update()
            logging.debug("AlertDialog should now be visible")
        except Exception as ex:
            logging.error(f"Error displaying dialog: {ex}")
            page.add(ft.Text(f"Error: {ex}"))
            page.update()

    def show_confirm_dialog(title, message, on_confirm):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Yes", on_click=lambda e: (close_dialog(), on_confirm()))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Dropdown for Teacher_ID
    teacher_dropdown = ft.Dropdown(
        label="Teacher",
        hint_text="Select a teacher",
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        bgcolor=ft.Colors.with_opacity(1, ft.Colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.PERSON,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        width=720,
    )

    # Dropdown for CourseID
    course_dropdown = ft.Dropdown(
        label="Course",
        hint_text="Select a course",
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        bgcolor=ft.Colors.with_opacity(1, ft.Colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.BOOK,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        width=720,
    )

    # Dropdown for SectionID
    section_dropdown = ft.Dropdown(
        label="Section",
        hint_text="Select a section",
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        bgcolor=ft.Colors.with_opacity(1, ft.Colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.CLASS_,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        width=720,
    )

    # Search field
    search_field = ft.TextField(
        label="Search by Teacher Name",
        hint_text="Enter teacher name",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.SEARCH,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        on_change=lambda e: update_table(e.control.value.strip()),
        width=720,
    )

    # Data table
    data_table = ft.DataTable(
        border=ft.Border(
            top=ft.BorderSide(1, ft.Colors.BLUE_200),
            bottom=ft.BorderSide(1, ft.Colors.BLUE_200),
            left=ft.BorderSide(1, ft.Colors.BLUE_200),
            right=ft.BorderSide(1, ft.Colors.BLUE_200),
        ),
        heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_600),
        heading_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        columns=[
            ft.DataColumn(ft.Text("Teacher Name", color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Course Name", color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Section Name", color=ft.Colors.WHITE)),
        ],
        rows=[]
    )

    selected_ids = ft.Ref[dict]()

    def reset_field_borders():
        teacher_dropdown.border_color = accent_color
        course_dropdown.border_color = accent_color
        section_dropdown.border_color = accent_color
        page.update()

    def validate_fields(fields):
        reset_field_borders()
        missing_fields = []
        for field, value in fields:
            if not value:
                field.border_color = ft.Colors.RED_400
                missing_fields.append(field.label)
        page.update()
        if len(missing_fields) == 1:
            return f"{missing_fields[0]} is required!"
        elif missing_fields:
            return f"The following fields are required: {', '.join(missing_fields)}"
        return None

    def clear_form():
        teacher_dropdown.value = None
        course_dropdown.value = None
        section_dropdown.value = None
        search_field.value = ""
        selected_ids.current = None
        reset_field_borders()
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
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)

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
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
            return []

    def update_table(search_term=""):
        data_table.rows.clear()
        for row in fetch_enrollments(search_term):
            teacher_id, course_id, section_id, teacher_name, course_name, section_name = row
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(teacher_name, color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(course_name, color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(section_name, color=ft.Colors.WHITE)),
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
        logging.debug("Form populated with selected enrollment data")
        reset_field_borders()
        page.update()

    def add_enrollment(e):
        logging.debug("Add Enrollment button clicked")
        teacher = teacher_dropdown.value
        course = course_dropdown.value
        section = section_dropdown.value

        # Validate fields
        fields = [
            (teacher_dropdown, teacher),
            (course_dropdown, course),
            (section_dropdown, section),
        ]
        error_message = validate_fields(fields)
        if error_message:
            logging.warning(f"Add failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO enrollment (Teacher_ID, CourseID, SectionID) VALUES (%s, %s, %s)",
                (teacher, course, section)
            )
            conn.commit()
            conn.close()
            reset_field_borders()
            show_alert_dialog("Success", "Enrollment added successfully!", is_success=True)
            logging.info(f"Added enrollment: Teacher {teacher}, Course {course}, Section {section}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
            page.update()

    def update_enrollment(e):
        logging.debug("Update button clicked")
        if not selected_ids.current:
            show_alert_dialog("Validation Error", "Please select an enrollment to update!", is_error=True)
            logging.warning("Update failed: No enrollment selected")
            page.update()
            return

        teacher = teacher_dropdown.value
        course = course_dropdown.value
        section = section_dropdown.value

        # Validate fields
        fields = [
            (teacher_dropdown, teacher),
            (course_dropdown, course),
            (section_dropdown, section),
        ]
        error_message = validate_fields(fields)
        if error_message:
            logging.warning(f"Update failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            return

        def confirm_update():
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE enrollment SET Teacher_ID=%s, CourseID=%s, SectionID=%s WHERE Teacher_ID=%s AND CourseID=%s AND SectionID=%s",
                    (
                        teacher,
                        course,
                        section,
                        selected_ids.current["Teacher_ID"],
                        selected_ids.current["CourseID"],
                        selected_ids.current["SectionID"]
                    )
                )
                conn.commit()
                conn.close()
                reset_field_borders()
                show_alert_dialog("Success", "Enrollment updated successfully!", is_success=True)
                logging.info(f"Updated enrollment: Teacher {teacher}, Course {course}, Section {section}")
                clear_form()
            except mysql.connector.Error as err:
                logging.error(f"Database error: {err}")
                show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
                page.update()

        show_confirm_dialog("Confirm Update", "Are you sure you want to update this enrollment?", confirm_update)

    def delete_enrollment(e):
        logging.debug("Delete button clicked")
        if not selected_ids.current:
            show_alert_dialog("Validation Error", "Please select an enrollment to delete!", is_error=True)
            logging.warning("Delete failed: No enrollment selected")
            page.update()
            return

        def confirm_delete():
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
                reset_field_borders()
                show_alert_dialog("Success", "Enrollment deleted successfully!", is_success=True)
                logging.info(f"Deleted enrollment: Teacher {selected_ids.current['Teacher_ID']}, Course {selected_ids.current['CourseID']}, Section {selected_ids.current['SectionID']}")
                clear_form()
            except mysql.connector.Error as err:
                logging.error(f"Database error: {err}")
                show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
                page.update()

        show_confirm_dialog("Confirm Delete", "Are you sure you want to delete this enrollment?", confirm_delete)

    add_btn = ft.ElevatedButton(
        text="Add Enrollment",
        on_click=add_enrollment,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=primary_color,
            color=ft.Colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        ),
    )
    update_btn = ft.ElevatedButton(
        text="Update",
        on_click=update_enrollment,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.AMBER_600,
            color=ft.Colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        ),
    )
    delete_btn = ft.ElevatedButton(
        text="Delete",
        on_click=delete_enrollment,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        ),
    )
    clear_btn = ft.ElevatedButton(
        text="Clear",
        on_click=lambda e: clear_form(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.GREY_600,
            color=ft.Colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        ),
    )

    data_table_container = ft.Container(
        content=ft.Column(
            [data_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
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
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Add, update, or delete enrollment records",
                    size=16,
                    color=ft.Colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
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
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
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
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
        ),
        animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
        scale=ft.transform.Scale(scale=1.0),
        on_hover=lambda e: card.update(scale=ft.transform.Scale(scale=1.02 if e.data == "true" else 1.0))
    )

    # Create back button for admin dashboard
    back_btn = create_back_button(
        page,
        show_main,
        primary_color=primary_color,
        teacher_id=None,
        on_click=lambda e: [page.controls.clear(), show_main(page)]
    )

    background = ft.Container(
        content=ft.Stack([
            card,
            ft.Container(
                content=back_btn,
                top=10,
                left=10,
            ),
        ]),
        alignment=ft.alignment.center,
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.Alignment(0, -0.8),
            radius=1.5,
            colors=[
                ft.Colors.with_opacity(0.2, primary_color),
                ft.Colors.with_opacity(0.1, accent_color),
                ft.Colors.BLACK,
            ],
        ),
    )

    page.add(background)
    fetch_dropdown_data()
    update_table()

if __name__ == "__main__":
    ft.app(target=main)