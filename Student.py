import flet as ft
import mysql.connector
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main(page: ft.Page):
    logging.debug("Starting student management page")
    page.title = "Student Management - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0

    # Custom colors
    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900]
    )

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
    section_id = ft.TextField(
        label="Section ID",
        hint_text="Enter section ID",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.GROUP,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        input_filter=ft.InputFilter(regex_string=r"^[0-9]*$"),
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
    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
    border_radius=10,
    prefix_icon=ft.icons.PHOTO,
    text_style=ft.TextStyle(
        color=ft.colors.WHITE,       # MATCHED
        size=16,                     # Set size explicitly
        weight=ft.FontWeight.W_400,  # Same as typical TextField text
    ),
    label_style=ft.TextStyle(color=ft.colors.BLUE_200),
    hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
    width=750,
)

    status_text = ft.Text("", color=ft.colors.RED_400, size=14, weight=ft.FontWeight.W_500)

    # Search field
    search_field = ft.TextField(
        label="Search by Full Name",
        hint_text="Enter name to search",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.SEARCH,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
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
                query += " WHERE Full_Name LIKE %s"
                cursor.execute(query, (f"%{search_term}%",))
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            logging.debug(f"Fetched {len(rows)} students")
            conn.close()
            return rows
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            status_text.value = f"Database Error: {err}"
            status_text.color = ft.colors.RED_400
            page.update()
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
                photo_sample.value = student[3]  # Set Dropdown to Yes/No or None
                status_text.value = "Student selected for editing"
                status_text.color = ft.colors.BLUE_200
                logging.debug("Form populated with selected student data")
            page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            status_text.value = f"Database Error: {err}"
            status_text.color = ft.colors.RED_400
            page.update()

    def add_click(e):
        roll = roll_no.value.strip()
        name = full_name.value.strip()
        section = section_id.value.strip()
        photo = photo_sample.value  # Yes, No, or None

        if not roll or not name or not section:
            status_text.value = "Roll Number, Full Name, and Section ID are required!"
            status_text.color = ft.colors.RED_400
            logging.warning("Add failed: Missing required fields")
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
            status_text.value = "Student added successfully!"
            status_text.color = ft.colors.GREEN_400
            logging.info(f"Added student: {roll}")
            clear_form()
            update_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            status_text.value = f"Database Error: {err}"
            status_text.color = ft.colors.RED_400
            page.update()

    def update_click(e):
        if not selected_roll_no.current:
            status_text.value = "Please select a student to update!"
            status_text.color = ft.colors.RED_400
            logging.warning("Update failed: No student selected")
            page.update()
            return

        roll = roll_no.value.strip()
        name = full_name.value.strip()
        section = section_id.value.strip()
        photo = photo_sample.value  # Yes, No, or None

        if not roll or not name or not section:
            status_text.value = "Roll Number, Full Name, and Section ID are required!"
            status_text.color = ft.colors.RED_400
            logging.warning("Update failed: Missing required fields")
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
            status_text.value = "Student updated successfully!"
            status_text.color = ft.colors.GREEN_400
            logging.info(f"Updated student: {roll}")
            clear_form()
            update_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            status_text.value = f"Database Error: {err}"
            status_text.color = ft.colors.RED_400
            page.update()

    def delete_click(e):
        if not selected_roll_no.current:
            status_text.value = "Please select a student to delete!"
            status_text.color = ft.colors.RED_400
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
            status_text.value = "Student deleted successfully!"
            status_text.color = ft.colors.GREEN_400
            logging.info(f"Deleted student: {selected_roll_no.current}")
            clear_form()
            update_table()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            status_text.value = f"Database Error: {err}"
            status_text.color = ft.colors.RED_400
            page.update()

    def take_photo_click(e):
        # Placeholder for camera functionality
        # TODO: Add camera integration (e.g., using OpenCV or a webcam library)
        status_text.value = "Camera functionality not implemented yet."
        status_text.color = ft.colors.BLUE_200
        logging.debug("Take Photo button clicked")
        page.update()

    def clear_form():
        roll_no.value = ""
        full_name.value = ""
        section_id.value = ""
        photo_sample.value = None
        selected_roll_no.current = None
        status_text.value = ""
        logging.debug("Form cleared")
        page.update()

    def search_click(e):
        search_term = search_field.value.strip()
        status_text.value = ""
        logging.debug(f"Searching with term: {search_term}")
        update_table(search_term)

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
    search_btn = ft.ElevatedButton(
        text="Search",
        on_click=search_click,
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
                ft.Row(
                    [search_field, search_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
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
                status_text,
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