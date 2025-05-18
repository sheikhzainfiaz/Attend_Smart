import flet as ft
import mysql.connector
import logging
import re
from db_connection import DatabaseConnection
from back_button import create_back_button
from Dash import show_main

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
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

        # Custom input filter for section name
    class SectionNameInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[A-Z0-9-]*$')

    # Updated TextField with input filter and max_length
    name = ft.TextField(
        label="Section Name",
        hint_text="Enter section name (e.g., SE1-A)",
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.LABEL,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
        max_length=10,  # Enforce maximum length
        input_filter=SectionNameInputFilter(),  # Restrict to uppercase letters, digits, hyphens
        on_change=lambda e: validate_section_name(e.control.value)
    )
    semester = ft.Dropdown(
        label="Semester",
        hint_text="Select a Semester",
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
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        border_radius=10,
        prefix_icon=ft.icons.CALENDAR_TODAY,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )
    department = ft.Dropdown(
        label="Department",
        hint_text="Select a Department",
        value=None,
        options=[
            ft.dropdown.Option("Department of Computer Science"),
            ft.dropdown.Option("Department of Textile Engineering"),
            ft.dropdown.Option("Department of Textile Technology"),
            ft.dropdown.Option("Department of Materials"),
            ft.dropdown.Option("Department of Applied Science"),
            ft.dropdown.Option("Faisalabad Business School"),
            ft.dropdown.Option("Department of Clothing"),
            ft.dropdown.Option("School of Arts & Design"),
        ],
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=False,
        border_radius=10,
        prefix_icon=ft.icons.SCHOOL,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720,
    )

    search_field = ft.TextField(
        label="Search Sections",
        hint_text="Enter name for search",
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

    def reset_field_borders():
        name.border_color = accent_color
        name.error_text = None
        semester.border_color = accent_color
        department.border_color = accent_color
        page.update()

    def validate_section_name(value):
        section_pattern = r'^[A-Z0-9-]{3,10}$'
        if value:
            if len(value) < 3:
                name.border_color = ft.colors.RED_400
                name.error_text = "Section name must be at least 3 characters"
                page.update()
                return
            try:
                with DatabaseConnection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT Name FROM section WHERE Name=%s AND SectionID!=%s", (value, selected_id.current or 0))
                    if cursor.fetchone():
                        name.border_color = ft.colors.RED_400
                        name.error_text = "Section name already in use"
                    else:
                        name.border_color = ft.colors.GREEN_600
                        name.error_text = None
            except mysql.connector.Error as err:
                name.border_color = ft.colors.RED_400
                name.error_text = "Error checking section name"
                logging.error(f"Database error in validate_section_name: {err}")
        else:
            name.border_color = accent_color
            name.error_text = None
        page.update()

    def validate_fields(fields):
        reset_field_borders()
        section_pattern = r'^[A-Z0-9-]{3,10}$'
        missing_fields = []
        for field, value in fields:
            if not value:
                field.border_color = ft.colors.RED_400
                missing_fields.append(field.label)
            elif field == name:
                if len(value) < 3:
                    field.border_color = ft.colors.RED_400
                    field.error_text = "Section name must be at least 3 characters"
                    missing_fields.append(field.label)
                else:
                    try:
                        with DatabaseConnection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT Name FROM section WHERE Name=%s AND SectionID!=%s", (value, selected_id.current or 0))
                            if cursor.fetchone():
                                field.border_color = ft.colors.RED_400
                                field.error_text = "Section name already in use"
                                missing_fields.append(field.label)
                            else:
                                field.border_color = ft.colors.GREEN_600
                                field.error_text = None
                    except mysql.connector.Error as err:
                        field.border_color = ft.colors.RED_400
                        field.error_text = "Error checking section name"
                        missing_fields.append(field.label)
                        logging.error(f"Database error in validate_fields: {err}")
        page.update()
        if len(missing_fields) == 1:
            return f"{missing_fields[0]} is required!"
        elif missing_fields:
            return f"The following fields are required: {', '.join(missing_fields)}"
        return None

    def clear_form():
        name.value = ""
        semester.value = None
        department.value = None
        search_field.value = ""
        selected_id.current = None
        reset_field_borders()
        update_table()
        page.update()

    def fetch_sections(search_term=""):
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                if search_term:
                    query = "SELECT SectionID, Name, Semester, Department FROM section WHERE Name LIKE %s OR Department LIKE %s"
                    cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
                else:
                    cursor.execute("SELECT SectionID, Name, Semester, Department FROM section")
                data = cursor.fetchall()
                
                logging.debug(f"Fetched {len(data)} sections: {data}")
                return data
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error fetching sections: {err}", is_error=True)
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
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Name, Semester, Department FROM section WHERE SectionID=%s", (section_id,))
                s = cursor.fetchone()
                if s:
                    name.value, semester.value, department.value = s
                    logging.debug("Form populated with selected section data")
                reset_field_borders()
                page.update()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error selecting section: {err}", is_error=True)
            page.update()

    def add_section(e):
        logging.debug("Add Section button clicked")
        section_name = name.value.strip() if name.value else ""
        sem = semester.value
        dept = department.value

        fields = [
            (name, section_name),
            (semester, sem),
            (department, dept),
        ]
        error_message = validate_fields(fields)
        if error_message:
            logging.warning(f"Add failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            return

        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO section (Name, Semester, Department) VALUES (%s, %s, %s)",
                            (section_name, sem, dept))
                conn.commit()
                reset_field_borders()
                show_alert_dialog("Success", "Section added successfully!", is_success=True)
                logging.info(f"Added section: {section_name}")
                clear_form()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_alert_dialog("Database Error", f"Error adding section: {err}", is_error=True)
            page.update()

    def update_section(e):
        logging.debug("Update button clicked")
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Please select a section to update!", is_error=True)
            logging.warning("Update failed: No section selected")
            page.update()
            return

        section_name = name.value.strip() if name.value else ""
        sem = semester.value
        dept = department.value

        fields = [
            (name, section_name),
            (semester, sem),
            (department, dept),
        ]
        error_message = validate_fields(fields)
        if error_message:
            logging.warning(f"Update failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            return

        def confirm_update():
            try:
                with DatabaseConnection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE section SET Name=%s, Semester=%s, Department=%s WHERE SectionID=%s",
                                (section_name, sem, dept, selected_id.current))
                    conn.commit()
                    reset_field_borders()
                    show_alert_dialog("Success", "Section updated successfully!", is_success=True)
                    logging.info(f"Updated section: {section_name}")
                    clear_form()
            except mysql.connector.Error as err:
                logging.error(f"Database error: {err}")
                show_alert_dialog("Database Error", f"Error updating section: {err}", is_error=True)
                page.update()

        show_confirm_dialog("Confirm Update", "Are you sure you want to update this section?", confirm_update)

    def delete_section(e):
        logging.debug("Delete button clicked")
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Please select a section to delete!", is_error=True)
            logging.warning("Delete failed: No section selected")
            page.update()
            return

        def confirm_delete():
            try:
                with DatabaseConnection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM section WHERE SectionID=%s", (selected_id.current,))
                    conn.commit()
                    reset_field_borders()
                    show_alert_dialog("Success", "Section deleted successfully!", is_success=True)
                    logging.info(f"Deleted section: {selected_id.current}")
                    clear_form()
            except mysql.connector.Error as err:
                logging.error(f"Database error: {err}")
                show_alert_dialog("Database Error", f"Error deleting section: {err}", is_error=True)
                page.update()

        show_confirm_dialog("Confirm Delete", "Are you sure you want to delete this section?", confirm_delete)

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
    )

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