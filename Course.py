import flet as ft
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main(page: ft.Page):
    page.title = "Course Management - Face Recognition System"
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

    def show_alert_dialog(title, message, is_success=False, is_error=False):
        logging.debug(f"Attempting to show AlertDialog: Title='{title}', Message='{message}', IsSuccess={is_success}, IsError={is_error}")
        try:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(
                    message,
                    color=ft.colors.GREEN_600 if is_success else ft.colors.RED_600 if is_error else ft.colors.BLACK
                ),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.colors.WHITE
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
            bgcolor=ft.colors.BLUE_800
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Text field for CourseCode
    course_code = ft.TextField(
        label="Course Code",
        hint_text="Enter course code (e.g., CS420)",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.CODE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )

    # Text field for CourseName
    course_name = ft.TextField(
        label="Course Name",
        hint_text="Enter course name (e.g., Construction)",
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

    # Dropdown for CreditHours
    credit_hours = ft.Dropdown(
        label="Credit Hours",
        hint_text="Select credit hours",
        value=None,
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3"),
        ],
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(1, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.HOURGLASS_TOP,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )

    # Search field
    search_field = ft.TextField(
        label="Search by Course Code",
        hint_text="Enter course code",
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
            ft.DataColumn(ft.Text("Course ID", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Course Code", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Course Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Credit Hours", color=ft.colors.WHITE)),
        ],
        rows=[]
    )

    selected_id = ft.Ref[str]()

    def reset_field_borders():
        course_code.border_color = accent_color
        course_name.border_color = accent_color
        credit_hours.border_color = accent_color
        page.update()

    def validate_fields(fields):
        reset_field_borders()
        missing_fields = []
        for field, value in fields:
            if not value:
                field.border_color = ft.colors.RED_400
                missing_fields.append(field.label)
        page.update()
        if len(missing_fields) == 1:
            return f"{missing_fields[0]} is required!"
        elif missing_fields:
            return f"The following fields are required: {', '.join(missing_fields)}"
        return None

    def clear_form():
        course_code.value = ""
        course_name.value = ""
        credit_hours.value = None
        search_field.value = ""
        selected_id.current = None
        reset_field_borders()
        update_table()
        page.update()

    def fetch_courses(search_term=""):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            if search_term:
                cursor.execute("SELECT CourseID, CourseCode, CourseName, CreditHours FROM course WHERE CourseCode LIKE %s", (f"%{search_term}%",))
            else:
                cursor.execute("SELECT CourseID, CourseCode, CourseName, CreditHours FROM course")
            data = cursor.fetchall()
            conn.close()
            logging.debug(f"Fetched {len(data)} courses")
            return data
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
            return []

    def update_table(search_term=""):
        data_table.rows.clear()
        for row in fetch_courses(search_term):
            course_id, course_code_val, course_name_val, credit_hours_val = row
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(course_id), color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(course_code_val, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(course_name_val, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(str(credit_hours_val), color=ft.colors.WHITE)),
                    ],
                    on_select_changed=lambda e, cid=course_id: select_course(cid)
                )
            )
        logging.debug(f"Table updated with {len(data_table.rows)} rows")
        page.update()

    def select_course(course_id):
        selected_id.current = course_id
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT CourseCode, CourseName, CreditHours FROM course WHERE CourseID=%s", (course_id,))
            c = cursor.fetchone()
            conn.close()
            if c:
                course_code.value, course_name.value, credit_hours.value = c[0], c[1], str(c[2])
                logging.debug("Form populated with selected course data")
            reset_field_borders()
            page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
            page.update()

    def add_course(e):
        logging.debug("Add Course button clicked")
        code = course_code.value.strip() if course_code.value else ""
        name = course_name.value.strip() if course_name.value else ""
        credits = credit_hours.value

        # Validate fields
        fields = [
            (course_code, code),
            (course_name, name),
            (credit_hours, credits),
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
                "INSERT INTO course (CourseCode, CourseName, CreditHours) VALUES (%s, %s, %s)",
                (code, name, credits)
            )
            conn.commit()
            conn.close()
            reset_field_borders()
            show_alert_dialog("Success", "Course added successfully!", is_success=True)
            logging.info(f"Added course: {code} - {name}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
            page.update()

    def update_course(e):
        logging.debug("Update button clicked")
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Please select a course to update!", is_error=True)
            logging.warning("Update failed: No course selected")
            page.update()
            return

        code = course_code.value.strip() if course_code.value else ""
        name = course_name.value.strip() if course_name.value else ""
        credits = credit_hours.value

        # Validate fields
        fields = [
            (course_code, code),
            (course_name, name),
            (credit_hours, credits),
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
                    "UPDATE course SET CourseCode=%s, CourseName=%s, CreditHours=%s WHERE CourseID=%s",
                    (code, name, credits, selected_id.current)
                )
                conn.commit()
                conn.close()
                reset_field_borders()
                show_alert_dialog("Success", "Course updated successfully!", is_success=True)
                logging.info(f"Updated course: {code} - {name}")
                clear_form()
            except mysql.connector.Error as err:
                logging.error(f"Database error: {err}")
                show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
                page.update()

        show_confirm_dialog("Confirm Update", "Are you sure you want to update this course?", confirm_update)

    def delete_course(e):
        logging.debug("Delete button clicked")
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Please select a course to delete!", is_error=True)
            logging.warning("Delete failed: No course selected")
            page.update()
            return

        def confirm_delete():
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM course WHERE CourseID=%s", (selected_id.current,))
                conn.commit()
                conn.close()
                reset_field_borders()
                show_alert_dialog("Success", "Course deleted successfully!", is_success=True)
                logging.info(f"Deleted course: {selected_id.current}")
                clear_form()
            except mysql.connector.Error as err:
                logging.error(f"Database error: {err}")
                show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)
                page.update()

        show_confirm_dialog("Confirm Delete", "Are you sure you want to delete this course?", confirm_delete)

    add_btn = ft.ElevatedButton(
        text="Add Course",
        on_click=add_course,
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
        on_click=update_course,
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
        on_click=delete_course,
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
                    "Course Management",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Add, update, or delete course records",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Column(
                    [
                        course_code,
                        course_name,
                        credit_hours,
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
        on_hover=lambda e: card.update(scale=ft.transform.Scale(scale=1.02 if e.data == "true" else 1.0))
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
    update_table()

if __name__ == "__main__":
    ft.app(target=main)