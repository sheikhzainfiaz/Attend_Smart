import flet as ft
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main(page: ft.Page):
    page.title = "Section Management - Face Recognition System"
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

    name = ft.TextField(
        label="Section Name",
        hint_text="Enter section name (e.g., SEA)",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.LABEL,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,  # Match the content width of the card (800 - 40 padding on each side)
    )
    semester = ft.Dropdown(
        label="Semester",
        hint_text="Select a semester",
        options=[
            ft.dropdown.Option("1st"),
            ft.dropdown.Option("2nd"),
            ft.dropdown.Option("3rd"),
            ft.dropdown.Option("4th"),
            ft.dropdown.Option("5th"),
            ft.dropdown.Option("6th"),
            ft.dropdown.Option("7th"),
            ft.dropdown.Option("8th"),
        ],
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.CALENDAR_TODAY,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,  # Match the width of other text fields
    )
    department = ft.TextField(
        label="Department",
        hint_text="Enter department (e.g., Computer Science)",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.SCHOOL,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,  # Match the width of other fields
    )

    search_field = ft.TextField(
        label="Search by Section Name",
        hint_text="Enter section name",
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
        width=720,  # Match the width of other fields
    )

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
            ft.DataColumn(ft.Text("Section ID", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Section Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Semester", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Department", color=ft.colors.WHITE)),
        ],
        rows=[]
    )

    selected_id = ft.Ref[str]()

    def clear_form():
        name.value = ""
        semester.value = None
        department.value = ""
        search_field.value = ""
        selected_id.current = None
        update_table()
        page.update()

    def fetch_sections(search_term=""):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            if search_term:
                cursor.execute("SELECT SectionID, Name, Semester, Department FROM section WHERE Name LIKE %s", (f"%{search_term}%",))
            else:
                cursor.execute("SELECT SectionID, Name, Semester, Department FROM section")
            data = cursor.fetchall()
            conn.close()
            logging.debug(f"Fetched {len(data)} sections")
            return data
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            return []

    def update_table(search_term=""):
        data_table.rows.clear()
        for row in fetch_sections(search_term):
            section_id, sec_name, sem, dept = row
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(section_id), color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(sec_name, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(sem, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(dept, color=ft.colors.WHITE)),
                    ],
                    on_select_changed=lambda e, sid=section_id: select_section(sid)
                )
            )
        logging.debug(f"Table updated with {len(data_table.rows)} rows")
        page.update()

    def select_section(section_id):
        selected_id.current = section_id
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Name, Semester, Department FROM section WHERE SectionID=%s", (section_id,))
            s = cursor.fetchone()
            conn.close()
            if s:
                name.value, semester.value, department.value = s
                show_message("Section selected for editing")
                logging.debug("Form populated with selected section data")
            page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    def add_section(e):
        if not all([name.value.strip(), semester.value, department.value.strip()]):
            show_message("All fields are required!", is_error=True)
            logging.warning("Add failed: Missing required fields")
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO section (Name, Semester, Department) VALUES (%s, %s, %s)",
                           (name.value, semester.value, department.value))
            conn.commit()
            conn.close()
            show_message("Section added successfully!")
            logging.info(f"Added section: {name.value}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    def update_section(e):
        if not selected_id.current:
            show_message("Please select a section to update!", is_error=True)
            logging.warning("Update failed: No section selected")
            page.update()
            return
        if not all([name.value.strip(), semester.value, department.value.strip()]):
            show_message("All fields are required!", is_error=True)
            logging.warning("Update failed: Missing required fields")
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("UPDATE section SET Name=%s, Semester=%s, Department=%s WHERE SectionID=%s",
                           (name.value, semester.value, department.value, selected_id.current))
            conn.commit()
            conn.close()
            show_message("Section updated successfully!")
            logging.info(f"Updated section: {name.value}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    def delete_section(e):
        if not selected_id.current:
            show_message("Please select a section to delete!", is_error=True)
            logging.warning("Delete failed: No section selected")
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM section WHERE SectionID=%s", (selected_id.current,))
            conn.commit()
            conn.close()
            show_message("Section deleted successfully!")
            logging.info(f"Deleted section: {selected_id.current}")
            clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            page.update()

    add_btn = ft.ElevatedButton(
        text="Add Section",
        on_click=add_section,
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
        on_click=update_section,
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
        on_click=delete_section,
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
                    "Section Management",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Add, update, or delete section records",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Column(
                    [
                        name,
                        semester,
                        department,
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
    update_table()

if __name__ == "__main__":
    ft.app(target=main)