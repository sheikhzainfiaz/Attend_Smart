import flet as ft
import mysql.connector
import logging
import cv2
import os
import re
from datetime import datetime
from db_connection import DatabaseConnection
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

    # AlertDialog function
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

    # Confirm dialog function
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

        # Custom input filter for full name
    class LettersAndSpacesInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[A-Za-z\s]*$')

    # Custom input filter for roll number
    class RollNoInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[0-9A-Z-]*$')

    # Updated TextField for Roll Number
    roll_no = ft.TextField(
        label="Roll Number",
        hint_text="e.g., 24-NTU-CS-1200 or 1200 or 24-1200",
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
        max_length=14,
        input_filter=RollNoInputFilter(),
        on_change=lambda e: validate_roll_no_live(e.control.value.strip())
    )

    # Updated TextField for Full Name
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
        max_length=50,
        input_filter=LettersAndSpacesInputFilter(),
        on_change=lambda e: validate_full_name_live(e.control.value.strip())
    )
    
         # Function to fetch sections from the MySQL database
    def get_sections_from_db():
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SectionID, Name, Department FROM section")
                sections = [{"id": row[0], "name": row[1], "department": row[2]} for row in cursor.fetchall()]
                
                logging.debug(f"Fetched {len(sections)} sections: {sections}")
                return sections
        except mysql.connector.Error as err:
            logging.error(f"Database error fetching sections: {err}")
            return []
    
       # Fetch sections from the database
    sections = get_sections_from_db()

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
        # bgcolor=ft.colors.with_opacity(1, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.GROUP,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=750,
        on_change=lambda e: generate_roll_number(e.control.value),
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
        # bgcolor=ft.colors.with_opacity(1, ft.colors.WHITE),
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

    # Search field
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
    
    # Updated function to validate and modify roll number (removed length check)
    def validate_and_modify_roll_number(roll_no, department):
        if not roll_no or not department:
            return "", "Roll number and section are required!"

        parts = roll_no.split('-')
        current_year = datetime.now().year % 100 - 1  # e.g., 24 for 2025
        default_dept_code = get_dept_code(department) or "CS"

        # Full format: YY-NTU-DD-NNNN
        if len(parts) == 4:
            year, ntu, dept_code, number = parts
            if (year.isdigit() and len(year) == 2 and
                ntu.upper() == "NTU" and
                number.isdigit() and len(number) == 4 and
                20 <= int(year) <= 25):
                return f"{year}-NTU-{default_dept_code}-{number}", ""  # Update department code if necessary
            return "", "Invalid roll number format! Use YY-NTU-DD-NNNN or convert from XXXX/YY-XXXX."
        # Short formats: XXXX or YY-XXXX
        elif len(parts) == 1 and parts[0].isdigit() and len(parts[0]) == 4:
            return f"{current_year:02d}-NTU-{default_dept_code}-{parts[0]}", ""
        elif len(parts) == 2 and parts[0].isdigit() and len(parts[0]) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
            return f"{parts[0]}-NTU-{default_dept_code}-{parts[1]}", ""
        return "", "Invalid roll number format! Use YY-NTU-DD-NNNN or convert from XXXX/YY-XXXX."

    # Real-time validation for roll number
    def validate_roll_no_live(roll):
        reset_field_borders()
        if roll and section_id.value:
            department = get_department_by_section(section_id.value)
            new_roll, message = validate_and_modify_roll_number(roll, department)
            if new_roll and new_roll != roll:
                roll_no.value = new_roll
            if not new_roll:
                roll_no.border_color = ft.colors.RED_400
                roll_no.error_text = message
            else:
                try:
                    with DatabaseConnection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT Roll_no FROM student WHERE Roll_no=%s AND Roll_no!=%s", (new_roll, selected_roll_no.current or ""))
                        result = cursor.fetchone()
                        logging.debug(f"Duplicate check for {new_roll}, selected_roll_no.current: {selected_roll_no.current}, result: {result}")
                        if result:
                            roll_no.border_color = ft.colors.RED_400
                            roll_no.error_text = "Roll number already in use"
                        else:
                            roll_no.border_color = ft.colors.GREEN_600
                            roll_no.error_text = None
                    
                except mysql.connector.Error as err:
                    roll_no.border_color = ft.colors.RED_400
                    roll_no.error_text = "Error checking roll number"
                    logging.error(f"Database error in validate_roll_no_live: {err}")
        else:
            roll_no.border_color = accent_color
            roll_no.error_text = None
        page.update()

    # Validation function for roll number (removed length check)
    def validate_roll_no(roll, department):
        if not roll:
            roll_no.border_color = accent_color
            roll_no.error_text = None
            page.update()
            return

        new_roll, message = validate_and_modify_roll_number(roll, department)
        if not new_roll:
            roll_no.border_color = ft.colors.RED_400
            roll_no.error_text = message
            page.update()
            return

        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Roll_no FROM student WHERE Roll_no=%s AND Roll_no!=%s", (new_roll, selected_roll_no.current or ""))
                result = cursor.fetchone()
                logging.debug(f"Duplicate check in validate_roll_no for {new_roll}, selected_roll_no.current: {selected_roll_no.current}, result: {result}")
                if result:
                    roll_no.border_color = ft.colors.RED_400
                    roll_no.error_text = "Roll number already in use"
                else:
                    roll_no.border_color = ft.colors.GREEN_600
                    roll_no.error_text = None
            
        except mysql.connector.Error as err:
            roll_no.border_color = ft.colors.RED_400
            roll_no.error_text = "Error checking roll number"
            logging.error(f"Database error in validate_roll_no: {err}")
        page.update()

    # Updated validate_fields function (removed length check)
    def validate_fields(fields, check_roll_no=True, check_name=True):
        reset_field_borders()
        errors = []
        for field, value, label in fields:
            if not value:
                field.border_color = ft.colors.RED_400
                errors.append(f"{label} is required!")
            elif field == roll_no and check_roll_no:
                department = get_department_by_section(section_id.value)
                new_roll, error = validate_and_modify_roll_number(value, department)
                if not new_roll:
                    field.border_color = ft.colors.RED_400
                    errors.append(error)
                else:
                    roll_no.value = new_roll
                    try:
                        with DatabaseConnection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT Roll_no FROM student WHERE Roll_no=%s AND Roll_no!=%s", (new_roll, selected_roll_no.current or ""))
                            result = cursor.fetchone()
                            logging.debug(f"Duplicate check in validate_fields for {new_roll}, selected_roll_no.current: {selected_roll_no.current}, result: {result}")
                            if result:
                                field.border_color = ft.colors.RED_400
                                errors.append("Roll number already in use")
                        
                    except mysql.connector.Error as err:
                        field.border_color = ft.colors.RED_400
                        errors.append("Error checking roll number")
                        logging.error(f"Database error in validate_fields: {err}")
            elif field == full_name and check_name:
                is_valid, error = validate_full_name(value)
                if not is_valid:
                    field.border_color = ft.colors.RED_400
                    errors.append(error)
        page.update()
        return errors

    # Updated select_row function to ensure proper roll number handling
    def select_row(roll):
        logging.debug(f"Selected row with Roll_no: {roll}")
        selected_roll_no.current = roll
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Roll_no, Full_Name, SectionID, PhotoSample FROM student WHERE Roll_no=%s", (roll,))
                student = cursor.fetchone()
                
                if student:
                    roll_no.value = student[0]
                    full_name.value = student[1]
                    section_id.value = str(student[2]) if student[2] else None
                    photo_sample.value = student[3] if student[3] else None
                    logging.debug(f"Selected student - Roll_no: {roll_no.value}, Section: {section_id.value}, Photo Sample: {photo_sample.value}")
                    # Validate the roll number after selection
                    if section_id.value:
                        department = get_department_by_section(section_id.value)
                        validate_roll_no(roll_no.value, department)
                    else:
                        roll_no.border_color = accent_color
                        roll_no.error_text = None
                reset_field_borders()
                page.update()
        except mysql.connector.Error as err:
            show_alert_dialog("Database Error", f"Error selecting student: {err}", is_error=True)

    # Real-time validation for full name
    def validate_full_name_live(name):
        if name:
            if len(name) < 4:
                full_name.border_color = ft.colors.RED_400
                full_name.error_text = "Full name must be at least 4 characters"
            else:
                full_name.border_color = ft.colors.GREEN_600
                full_name.error_text = None
        else:
            full_name.border_color = accent_color
            full_name.error_text = None
        page.update()


    # Updated validate_full_name function
    def validate_full_name(name):
        if not name:
            return False, "Full name is required!"
        if len(name) < 4:
            return False, "Full name must be at least 4 characters"
        return True, ""


    # Updated generate_roll_number function
    def generate_roll_number(section_id):
        if not section_id:
            roll_no.value = ""
            roll_no.error_text = None
            roll_no.update()
            return

        department = get_department_by_section(section_id) or "Department of Computer Science"
        current_year = datetime.now().year % 100 - 1  # e.g., 24 for 2025
        default_dept_code = get_dept_code(department) or "CS"

        new_roll, message = validate_and_modify_roll_number(roll_no.value, department)
        if new_roll:
            roll_no.value = new_roll
            roll_no.error_text = None
        else:
            parts = roll_no.value.split('-')
            if len(parts) == 1 and parts[0].isdigit() and len(parts[0]) == 4:
                roll_no.value = f"{current_year:02d}-NTU-{default_dept_code}-{parts[0]}"
                roll_no.error_text = None
            elif len(parts) == 2 and parts[0].isdigit() and len(parts[0]) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
                roll_no.value = f"{parts[0]}-NTU-{default_dept_code}-{parts[1]}"
                roll_no.error_text = None
            else:
                roll_no.value = f"{current_year:02d}-NTU-{default_dept_code}-0001"
                roll_no.error_text = None

        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Roll_no FROM student WHERE Roll_no=%s AND Roll_no!=%s", (roll_no.value, selected_roll_no.current or ""))
                if cursor.fetchone():
                    roll_no.border_color = ft.colors.RED_400
                    roll_no.error_text = "Roll number already in use"
                else:
                    roll_no.border_color = ft.colors.GREEN_600
                    roll_no.error_text = None
            
        except mysql.connector.Error as err:
            roll_no.border_color = ft.colors.RED_400
            roll_no.error_text = "Error checking roll number"
            logging.error(f"Database error in generate_roll_number: {err}")

        logging.debug(f"Generated/Modified roll number: {roll_no.value} for department: {department}")
        roll_no.update()


    # Function to get department by SectionID
    def get_department_by_section(section_id):
        if not section_id:
            return None
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Department FROM section WHERE SectionID = %s", (section_id,))
                department = cursor.fetchone()
                
                return department[0].strip() if department else None
        except mysql.connector.Error as err:
            logging.error(f"Database error fetching department: {err}")
            return None

    # Function to get department code from department name
    def get_dept_code(department):
        for dept, codes in DEPARTMENT_CODES.items():
            if dept == department:
                return codes[0]  # Return the first valid code
        return None
    
    # DataTable
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
        roll_no.error_text = None
        page.update()
        
    # Function to capture photos
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

    def fetch_students(search_term=""):
        logging.debug(f"Fetching students with search term: {search_term}")
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                query = "SELECT Roll_no, Full_Name, SectionID, PhotoSample FROM student"
                if search_term:
                    query += " WHERE Full_Name LIKE %s OR Roll_no LIKE %s OR SectionID LIKE %s"
                    cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
                else:
                    cursor.execute(query)
                rows = cursor.fetchall()
                logging.debug(f"Fetched {len(rows)} students")
            
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
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO student (Roll_no, Full_Name, SectionID, PhotoSample) VALUES (%s, %s, %s, %s)",
                    (roll, name, section, photo)
                )
                conn.commit()
                
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
        is_valid, error = validate_and_modify_roll_number(roll, department)
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

    # Buttons
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

    # Card container
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

    # Create back button for admin dashboard
    back_btn = create_back_button(
        page,
        show_main,
        primary_color=primary_color,
        teacher_id=None,
        on_click=lambda e: [page.controls.clear(), show_main(page)]
    )

    # Background with radial gradient
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