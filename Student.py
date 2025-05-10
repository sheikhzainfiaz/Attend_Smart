import flet as ft
import mysql.connector
import logging
import cv2
import os
import re
from back_button import create_back_button
from Dash import show_main

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Department code mapping
DEPARTMENT_CODES = {
    "Department of Computer Science": ["CS"],
    "Department of Textile Engineering": ["TE"],
    "Department of Textile Technology": ["TT"],
    "Department of Materials": ["PE"],
    "Department of Applied Science": ["CH", "PH", "MM"],
    "Faisalabad Business School": ["BA"],
    "Department of Clothing": ["AM"],
    "School of Arts & Design": ["DD"]
}

# Function to fetch sections from the MySQL database
def get_sections_from_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="face_db",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT SectionID, Name, Department FROM section")
        sections = [{"id": row[0], "name": row[1], "department": row[2]} for row in cursor.fetchall()]
        conn.close()
        logging.debug(f"Fetched {len(sections)} sections: {sections}")
        return sections
    except mysql.connector.Error as err:
        logging.error(f"Database error fetching sections: {err}")
        return []

# Function to get department by SectionID
def get_department_by_section(section_id):
    if not section_id:
        return None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="face_db",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT Department FROM section WHERE SectionID = %s", (section_id,))
        department = cursor.fetchone()
        conn.close()
        return department[0] if department else None
    except mysql.connector.Error as err:
        logging.error(f"Database error fetching department: {err}")
        return None

# Function to validate roll number format
def validate_roll_number(roll_no, department):
    if not roll_no or not department:
        return False, "Roll number and section are required!"
    
    # Expected format: YY-NTU-DD-NNNN
    pattern = r"^\d{2}-NTU-[A-Z]{2}-\d{4}$"
    if not re.match(pattern, roll_no):
        return False, "Invalid roll number format! Use YY-NTU-DD-NNNN (e.g., 23-NTU-CS-1200)"

    # Extract department code
    dept_code = roll_no.split('-')[2]
    valid_codes = DEPARTMENT_CODES.get(department, [])
    if dept_code not in valid_codes:
        return False, f"Invalid department code '{dept_code}' for {department}!"

    # Validate year (e.g., 20-25 for 2020-2025)
    year = int(roll_no[:2])
    if not (20 <= year <= 25):
        return False, "Invalid year in roll number! Use 20-25."

    # Validate number part
    number = roll_no[-4:]
    if not number.isdigit():
        return False, "Last 4 characters must be digits!"

    return True, ""

# Function to validate full name
def validate_full_name(name):
    if not name:
        return False, "Full name is required!"
    if len(name) < 2 or len(name) > 50:
        return False, "Full name must be between 2 and 50 characters!"
    if not re.match(r"^[A-Za-z\s]+$", name):
        return False, "Full name can only contain letters and spaces!"
    return True, ""

def main(page: ft.Page):
    logging.debug("Starting student management page")
    page.title = "Student Management - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # Custom colors
    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900]
    )

    # AlertDialog function (unchanged)
    def show_alert_dialog(title, message, is_success=False, is_error=False):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(
                message,
                color=ft.colors.GREEN_600 if is_success else ft.colors.RED_600 if is_error else ft.colors.BLACK
            ),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Confirm dialog function (unchanged)
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
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Function to capture photos (unchanged)
    def take_photo_and_save(roll_number):
        if not roll_number:
            show_alert_dialog("Error", "Roll Number is required!", is_error=True)
            return None

        save_path = os.path.join("photos", roll_number)
        os.makedirs(save_path, exist_ok=True)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            show_alert_dialog("Error", "Failed to open camera!", is_error=True)
            logging.error("Camera could not be opened")
            return None

        count = 1
        max_photos = 5

        while count <= max_photos:
            success, img = cap.read()
            if not success:
                show_alert_dialog("Error", "Failed to capture image!", is_error=True)
                logging.error("Failed to capture image")
                break

            cv2.imshow("Take Photo", img)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                height, width, _ = img.shape
                square_size = min(height, width)
                x = (width - square_size) // 2
                y = (height - square_size) // 2
                square_img = img[y:y + square_size, x:x + square_size]
                square_img = cv2.resize(square_img, (224, 224))
                filename = os.path.join(save_path, f"{roll_number}_{count}.jpg")
                cv2.imwrite(filename, square_img)
                logging.debug(f"Saved {filename}")
                count += 1

            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if count > 1:
            return filename
        else:
            show_alert_dialog("Warning", "No photos were saved!", is_error=True)
            return None

    # Form fields
    roll_no = ft.TextField(
        label="Roll Number",
        hint_text="e.g., 23-NTU-CS-1200",
        autofocus=True,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.NUMBERS,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_change=lambda e: validate_roll_no_live(e.control.value.strip()),
    )
    full_name = ft.TextField(
        label="Full Name",
        hint_text="Enter student full name",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.PERSON_OUTLINE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
    )

    # Fetch sections from the database
    sections = get_sections_from_db()

    # Dropdown for section_id
    section_id = ft.Dropdown(
        label="Section",
        hint_text="Select a section",
        options=[
            ft.dropdown.Option(key=str(section["id"]), text=section["name"])
            for section in sections
        ] if sections else [ft.dropdown.Option(key="0", text="No sections available")],
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        bgcolor=ft.colors.with_opacity(1, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.GROUP,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=750,
        on_change=lambda e: validate_roll_no_live(roll_no.value.strip()),
    )

    photo_sample = ft.Dropdown(
        label="Photo Sample",
        hint_text="Select Yes or No",
        options=[
            ft.dropdown.Option(key="Yes", text="Yes"),
            ft.dropdown.Option(key="No", text="No"),
        ],
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        bgcolor=ft.colors.with_opacity(1, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.PHOTO,
        text_style=ft.TextStyle(
            color=ft.colors.WHITE,
            size=16,
            weight=ft.FontWeight.W_400,
        ),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=750,
    )

    # Search field (unchanged)
    search_field = ft.TextField(
        label="Search Students",
        hint_text="Search by name or roll number",
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
    )

    # DataTable (unchanged)
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
            ft.DataColumn(ft.Text("Full Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Section ID", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Photo Sample", color=ft.colors.WHITE)),
        ],
        rows=[],
    )

    selected_roll_no = ft.Ref[str]()

    # Helper function to reset field borders
    def reset_field_borders():
        roll_no.border_color = accent_color
        full_name.border_color = accent_color
        section_id.border_color = accent_color
        photo_sample.border_color = accent_color
        page.update()

    # Helper function to validate fields
    def validate_fields(fields, check_roll_no=True, check_name=True):
        reset_field_borders()
        errors = []
        for field, value, label in fields:
            if not value:
                field.border_color = ft.colors.RED_400
                errors.append(f"{label} is required!")
            elif field == roll_no and check_roll_no:
                department = get_department_by_section(section_id.value)
                is_valid, error = validate_roll_number(value, department)
                if not is_valid:
                    field.border_color = ft.colors.RED_400
                    errors.append(error)
            elif field == full_name and check_name:
                is_valid, error = validate_full_name(value)
                if not is_valid:
                    field.border_color = ft.colors.RED_400
                    errors.append(error)
        page.update()
        return errors

    # Live validation for roll number
    def validate_roll_no_live(roll):
        reset_field_borders()
        if roll and section_id.value:
            department = get_department_by_section(section_id.value)
            is_valid, error = validate_roll_number(roll, department)
            if not is_valid:
                roll_no.border_color = ft.colors.RED_400
                roll_no.error_text = error
            else:
                roll_no.error_text = None
        else:
            roll_no.error_text = None
        page.update()

    def fetch_students(search_term=""):
        logging.debug(f"Fetching students with search term: {search_term}")
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_db",
                port=3306
            )
            cursor = conn.cursor()
            query = "SELECT Roll_no, Full_Name, SectionID, PhotoSample FROM student"
            if search_term:
                query += " WHERE Full_Name LIKE %s OR Roll_no LIKE %s OR SectionID LIKE %s"
                cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            logging.debug(f"Fetched {len(rows)} students")
            conn.close()
            return rows
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error fetching students: {err}", is_error=True)
            return []

    def update_table(search_term=""):
        logging.debug("Updating table")
        data_table.rows.clear()
        students = fetch_students(search_term)
        for student in students:
            roll_no_val, full_name_val, section_id_val, photo_sample_val = student
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(roll_no_val, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(full_name_val, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(str(section_id_val), color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(photo_sample_val or "N/A", color=ft.colors.WHITE)),
                    ],
                    on_select_changed=lambda e, roll=roll_no_val: select_row(roll),
                )
            )
        logging.debug(f"Table updated with {len(data_table.rows)} rows")
        page.update()

    def select_row(roll):
        logging.debug(f"Selected row with Roll_no: {roll}")
        selected_roll_no.current = roll
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_db",
                port=3306
            )
            cursor = conn.cursor()
            cursor.execute("SELECT Roll_no, Full_Name, SectionID, PhotoSample FROM student WHERE Roll_no=%s", (roll,))
            student = cursor.fetchone()
            conn.close()
            if student:
                roll_no.value = student[0]
                full_name.value = student[1]
                section_id.value = str(student[2]) if student[2] else None
                photo_sample.value = student[3] if student[3] else None
                logging.debug(f"Selected student - Section: {section_id.value}, Photo Sample: {photo_sample.value}")
            reset_field_borders()
            roll_no.error_text = None
            page.update()
        except mysql.connector.Error as err:
            show_alert_dialog("Database Error", f"Error selecting student: {err}", is_error=True)

    def add_click(e):
        logging.debug("Add button clicked")
        roll = roll_no.value.strip() if roll_no.value else ""
        name = full_name.value.strip() if full_name.value else ""
        section = section_id.value
        photo = photo_sample.value

        # Validate all fields
        fields = [
            (roll_no, roll, "Roll Number"),
            (full_name, name, "Full Name"),
            (section_id, section, "Section"),
            (photo_sample, photo, "Photo Sample")
        ]
        errors = validate_fields(fields)
        if errors:
            logging.warning(f"Add failed: {'; '.join(errors)}")
            show_alert_dialog("Validation Error", "\n".join(errors), is_error=True)
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_db",
                port=3306
            )
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO student (Roll_no, Full_Name, SectionID, PhotoSample) VALUES (%s, %s, %s, %s)",
                (roll, name, section, photo)
            )
            conn.commit()
            conn.close()
            reset_field_borders()
            show_alert_dialog("Success", "Student added successfully!", is_success=True)
            logging.info(f"Added student: {roll}")
            clear_form()
            update_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error adding student: {err}", is_error=True)
            page.update()

    def update_click(e):
        logging.debug("Update button clicked")
        if not selected_roll_no.current:
            show_alert_dialog("Validation Error", "Please select a student to update!", is_error=True)
            return

        roll = roll_no.value.strip() if roll_no.value else ""
        name = full_name.value.strip() if full_name.value else ""
        section = section_id.value
        photo = photo_sample.value

        # Validate all fields (skip roll number format validation if unchanged)
        check_roll_no = roll != selected_roll_no.current
        fields = [
            (roll_no, roll, "Roll Number"),
            (full_name, name, "Full Name"),
            (section_id, section, "Section"),
            (photo_sample, photo, "Photo Sample")
        ]
        errors = validate_fields(fields, check_roll_no=check_roll_no)
        if errors:
            logging.warning(f"Update failed: {'; '.join(errors)}")
            show_alert_dialog("Validation Error", "\n".join(errors), is_error=True)
            return

        def confirm_update():
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="root",
                    database="face_db",
                    port=3306
                )
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE student SET Roll_no=%s, Full_Name=%s, SectionID=%s, PhotoSample=%s WHERE Roll_no=%s",
                    (roll, name, section, photo, selected_roll_no.current)
                )
                conn.commit()
                conn.close()
                reset_field_borders()
                show_alert_dialog("Success", "Student updated successfully!", is_success=True)
                clear_form()
                update_table()
            except mysql.connector.Error as err:
                show_alert_dialog("Database Error", f"Error updating student: {err}", is_error=True)

        show_confirm_dialog("Confirm Update", "Are you sure you want to update this student?", confirm_update)

    def delete_click(e):
        logging.debug("Delete button clicked")
        if not selected_roll_no.current:
            show_alert_dialog("Validation Error", "Please select a student to delete!", is_error=True)
            return

        def confirm_delete():
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="root",
                    database="face_db",
                    port=3306
                )
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student WHERE Roll_no=%s", (selected_roll_no.current,))
                conn.commit()
                conn.close()
                reset_field_borders()
                show_alert_dialog("Success", "Student deleted successfully!", is_success=True)
                clear_form()
                update_table()
            except mysql.connector.Error as err:
                show_alert_dialog("Database Error", f"Error deleting student: {err}", is_error=True)

        show_confirm_dialog("Confirm Delete", "Are you sure you want to delete this student?", confirm_delete)

    def take_photo_click(e):
        logging.debug("Take Photo button clicked")
        roll = roll_no.value.strip() if roll_no.value else ""
        department = get_department_by_section(section_id.value)
        is_valid, error = validate_roll_number(roll, department)
        if not roll or not is_valid:
            show_alert_dialog("Validation Error", error or "Roll Number is required!", is_error=True)
            logging.warning("Take photo failed: Invalid roll number")
            return

        filename = take_photo_and_save(roll)
        if filename:
            show_alert_dialog("Success", "Photo captured and saved!", is_success=True)
            photo_sample.value = "Yes"
            reset_field_borders()
            page.update()

    def clear_form():
        roll_no.value = ""
        full_name.value = ""
        section_id.value = None
        photo_sample.value = None
        selected_roll_no.current = None
        search_field.value = ""
        roll_no.error_text = None
        reset_field_borders()
        logging.debug(f"Form cleared - Section: {section_id.value}, Photo Sample: {photo_sample.value}")
        section_id.update()
        photo_sample.update()
        page.update()

    # Buttons (unchanged)
    add_btn = ft.ElevatedButton(
        text="Add Student",
        on_click=add_click,
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
        on_click=update_click,
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
        on_click=delete_click,
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
    take_photo_btn = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.icons.CAMERA, color=ft.colors.WHITE),
                ft.Text("Take Photo", color=ft.colors.WHITE),
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        on_click=take_photo_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.colors.CYAN_600,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )

    # Initial table load
    logging.debug("Loading initial table data")
    update_table()

    # Card container (unchanged)
    card = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Student Management",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Add, update, or delete student records",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Column(
                    [
                        roll_no,
                        full_name,
                        section_id,
                        photo_sample,
                        ft.Row(
                            [add_btn, update_btn, delete_btn, clear_btn, take_photo_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                search_field,
                ft.Container(
                    content=ft.Column(
                        [data_table],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    border_radius=10,
                    height=300,
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
    )

    # Create back button for admin dashboard (unchanged)
    back_btn = create_back_button(
        page,
        show_main,
        primary_color=primary_color,
        teacher_id=None,
        on_click=lambda e: [page.controls.clear(), show_main(page)]
    )

    # Background with radial gradient (unchanged)
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
    update_table()

if __name__ == "__main__":
    logging.debug("Running Flet app")
    ft.app(target=main)