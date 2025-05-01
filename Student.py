import flet as ft
import mysql.connector
import logging
import cv2
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

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
        cursor.execute("SELECT SectionID, Name FROM section")
        sections = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        conn.close()
        logging.debug(f"Fetched {len(sections)} sections")
        return sections
    except mysql.connector.Error as err:
        logging.error(f"Database error fetching sections: {err}")
        return []

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

    # Function to show AlertDialog
    def show_alert_dialog(title, message, is_error=False):
        logging.debug(f"Attempting to show AlertDialog: Title='{title}', Message='{message}', IsError={is_error}")
        try:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END
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

    # Function to capture photos
    def take_photo_and_save(roll_number):
        """Capture up to 5 photos and overwrite in a loop using the roll_number as folder."""
        if not roll_number:
            show_alert_dialog("Error", "Enter roll number before taking a photo!", is_error=True)
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

            if key == ord('s'):  # Capture on 's'
                # Make the image square
                height, width, _ = img.shape
                square_size = min(height, width)
                x = (width - square_size) // 2
                y = (height - square_size) // 2
                square_img = img[y:y + square_size, x:x + square_size]

                # Resize to standard
                square_img = cv2.resize(square_img, (224, 224))

                # Save image with overwrite logic
                filename = os.path.join(save_path, f"{roll_number}_{count}.jpg")
                cv2.imwrite(filename, square_img)
                logging.debug(f"Saved {filename}")
                count += 1

            elif key == ord('q'):  # Quit on 'q'
                break

        cap.release()
        cv2.destroyAllWindows()

        if count > 1:  # At least one photo was saved
            return filename
        else:
            show_alert_dialog("Warning", "No photos were saved!", is_error=True)
            return None

    # Form fields
    roll_no = ft.TextField(
        label="Roll Number",
        hint_text="Enter student roll number",
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
        ] if sections else [ft.dropdown.Option(text="No sections available")],
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
    )

    photo_sample = ft.Dropdown(
        label="Photo Sample",
        hint_text="Select Yes or No",
        options=[
            ft.dropdown.Option("Yes"),
            ft.dropdown.Option("No"),
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

    # Search field
    search_field = ft.TextField(
        label="Search Students",
        hint_text="Search by name, roll number, or section ID",
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
                section_id.value = str(student[2])
                photo_sample.value = student[3]
                show_alert_dialog("Success", "Student selected for editing")
                logging.debug("Form populated with selected student data")
            else:
                show_alert_dialog("Error", "Student not found!", is_error=True)
            page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error selecting student: {err}", is_error=True)
            page.update()

    def add_click(e):
        logging.debug("Add button clicked")
        roll = roll_no.value.strip() if roll_no.value else ""
        name = full_name.value.strip() if full_name.value else ""
        section = section_id.value
        photo = photo_sample.value

        # Validate all fields
        missing_fields = []
        if not roll:
            missing_fields.append("Roll Number")
        if not name:
            missing_fields.append("Full Name")
        if not section:
            missing_fields.append("Section")
        if not photo:
            missing_fields.append("Photo Sample")

        if missing_fields:
            error_message = f"Missing: {', '.join(missing_fields)}"
            logging.warning(f"Add failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            page.update()
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
            show_alert_dialog("Success", "Student added successfully!")
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
            logging.warning("Update failed: No student selected")
            page.update()
            return
        
        roll = roll_no.value.strip() if roll_no.value else ""
        name = full_name.value.strip() if full_name.value else ""
        section = section_id.value
        photo = photo_sample.value

        # Validate all fields
        missing_fields = []
        if not roll:
            missing_fields.append("Roll Number")
        if not name:
            missing_fields.append("Full Name")
        if not section:
            missing_fields.append("Section")
        if not photo:
            missing_fields.append("Photo Sample")

        if missing_fields:
            error_message = f"Missing: {', '.join(missing_fields)}"
            logging.warning(f"Update failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            page.update()
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
                "UPDATE student SET Roll_no=%s, Full_Name=%s, SectionID=%s, PhotoSample=%s WHERE Roll_no=%s",
                (roll, name, section, photo, selected_roll_no.current)
            )
            conn.commit()
            conn.close()
            show_alert_dialog("Success", "Student updated successfully!")
            logging.info(f"Updated student: {roll}")
            clear_form()
            update_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error updating student: {err}", is_error=True)
            page.update()

    def delete_click(e):
        logging.debug("Delete button clicked")
        if not selected_roll_no.current:
            show_alert_dialog("Validation Error", "Please select a student to delete!", is_error=True)
            logging.warning("Delete failed: No student selected")
            page.update()
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
            cursor.execute("DELETE FROM student WHERE Roll_no=%s", (selected_roll_no.current,))
            conn.commit()
            conn.close()
            show_alert_dialog("Success", "Student deleted successfully!")
            logging.info(f"Deleted student: {selected_roll_no.current}")
            clear_form()
            update_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error deleting student: {err}", is_error=True)
            page.update()

    def take_photo_click(e):
        logging.debug("Take Photo button clicked")
        roll = roll_no.value.strip() if roll_no.value else ""
        if not roll:
            show_alert_dialog("Validation Error", "Enter roll number before taking a photo!", is_error=True)
            logging.warning("Take photo failed: No roll number provided")
            return

        filename = take_photo_and_save(roll)
        if filename:
            show_alert_dialog("Success", "Photo captured and saved!")
            photo_sample.value = "Yes"
            page.update()

    def clear_form():
        roll_no.value = ""
        full_name.value = ""
        section_id.value = None
        photo_sample.value = None
        selected_roll_no.current = None
        search_field.value = ""
        logging.debug("Form cleared")
        update_table()
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

    # Background
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

if __name__ == "__main__":
    logging.debug("Running Flet app")
    ft.app(target=main)