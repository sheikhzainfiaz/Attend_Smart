import flet as ft
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def main(page: ft.Page):
    page.title = "Teacher Management - Face Recognition System"
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

    full_name = ft.TextField(
        label="Full Name",
        hint_text="Enter teacher’s full name",
        prefix_icon=ft.icons.PERSON,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720
    )
    email = ft.TextField(
        label="Email",
        hint_text="Enter email address",
        prefix_icon=ft.icons.EMAIL,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720
    )
    phone = ft.TextField(
        label="Phone",
        hint_text="Enter phone number",
        prefix_icon=ft.icons.PHONE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720
    )
    username = ft.TextField(
        label="Username",
        hint_text="Enter username",
        prefix_icon=ft.icons.ACCOUNT_CIRCLE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720
    )
    password = ft.TextField(
        label="Password",
        hint_text="Enter password",
        prefix_icon=ft.icons.LOCK,
        password=True,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        width=720
    )

    search_field = ft.TextField(
        label="Search by Full Name",
        hint_text="Enter name",
        prefix_icon=ft.icons.SEARCH,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_change=lambda e: update_table(e.control.value.strip()),
        width=600
    )

    selected_id = ft.Ref[str]()

    def clear_form():
        full_name.value = ""
        email.value = ""
        phone.value = ""
        username.value = ""
        password.value = ""
        search_field.value = ""
        selected_id.current = None
        update_table()
        page.update()

    def fetch_teachers(search_term=""):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            if search_term:
                cursor.execute("SELECT Teacher_ID, Full_Name, Email, Phone, Username FROM teachers WHERE Full_Name LIKE %s", (f"%{search_term}%",))
            else:
                cursor.execute("SELECT Teacher_ID, Full_Name, Email, Phone, Username FROM teachers")
            data = cursor.fetchall()
            conn.close()
            logging.debug(f"Fetched {len(data)} teachers")
            return data
        except mysql.connector.Error as e:
            logging.error(f"Database error: {e}")
            show_alert_dialog("Database Error", f"Error fetching teachers: {e}", is_error=True)
            return []

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
            ft.DataColumn(ft.Text("Name", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Email", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Phone", color=ft.colors.WHITE)),
            ft.DataColumn(ft.Text("Username", color=ft.colors.WHITE)),
        ],
        rows=[]
    )

    def update_table(search_term=""):
        data_table.rows.clear()
        for row in fetch_teachers(search_term):
            teacher_id, name, mail, phone_val, user = row
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(name, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(mail, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(phone_val, color=ft.colors.WHITE)),
                        ft.DataCell(ft.Text(user, color=ft.colors.WHITE)),
                    ],
                    on_select_changed=lambda e, tid=teacher_id: select_teacher(tid)
                )
            )
        logging.debug(f"Table updated with {len(data_table.rows)} rows")
        page.update()

    def select_teacher(teacher_id):
        selected_id.current = teacher_id
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Full_Name, Email, Phone, Username, Password FROM teachers WHERE Teacher_ID=%s", (teacher_id,))
            t = cursor.fetchone()
            conn.close()
            if t:
                full_name.value, email.value, phone.value, username.value, password.value = t
                logging.debug("Form populated with selected teacher data")
            page.update()
        except mysql.connector.Error as e:
            logging.error(f"Database error: {e}")
            show_alert_dialog("Database Error", f"Error selecting teacher: {e}", is_error=True)
            page.update()

    def add_teacher(e):
        logging.debug("Add button clicked")
        name = full_name.value.strip() if full_name.value else ""
        mail = email.value.strip() if email.value else ""
        phone_val = phone.value.strip() if phone.value else ""
        user = username.value.strip() if username.value else ""
        pwd = password.value.strip() if password.value else ""

        # Validate fields
        missing_fields = []
        if not name:
            missing_fields.append("Full Name")
        if not mail:
            missing_fields.append("Email")
        if not phone_val:
            missing_fields.append("Phone")
        if not user:
            missing_fields.append("Username")
        if not pwd:
            missing_fields.append("Password")

        if missing_fields:
            error_message = f"Missing: {', '.join(missing_fields)}"
            logging.warning(f"Add failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            page.update()
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO teachers (Full_Name, Email, Phone, Username, Password) VALUES (%s, %s, %s, %s, %s)",
                           (name, mail, phone_val, user, pwd))
            conn.commit()
            conn.close()
            show_alert_dialog("Success", "Teacher added successfully")
            logging.info(f"Added teacher: {name}")
            clear_form()
            update_table()
        except mysql.connector.Error as e:
            logging.error(f"Database error: {e}")
            show_alert_dialog("Database Error", f"Error adding teacher: {e}", is_error=True)
            page.update()

    def update_teacher(e):
        logging.debug("Update button clicked")
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Please select a teacher to update!", is_error=True)
            logging.warning("Update failed: No teacher selected")
            page.update()
            return

        name = full_name.value.strip() if full_name.value else ""
        mail = email.value.strip() if email.value else ""
        phone_val = phone.value.strip() if phone.value else ""
        user = username.value.strip() if username.value else ""
        pwd = password.value.strip() if password.value else ""

        # Validate fields
        missing_fields = []
        if not name:
            missing_fields.append("Full Name")
        if not mail:
            missing_fields.append("Email")
        if not phone_val:
            missing_fields.append("Phone")
        if not user:
            missing_fields.append("Username")
        if not pwd:
            missing_fields.append("Password")

        if missing_fields:
            error_message = f"Missing: {', '.join(missing_fields)}"
            logging.warning(f"Update failed: {error_message}")
            show_alert_dialog("Validation Error", error_message, is_error=True)
            page.update()
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("UPDATE teachers SET Full_Name=%s, Email=%s, Phone=%s, Username=%s, Password=%s WHERE Teacher_ID=%s",
                           (name, mail, phone_val, user, pwd, selected_id.current))
            conn.commit()
            conn.close()
            show_alert_dialog("Success", "Teacher updated successfully")
            logging.info(f"Updated teacher: {name}")
            clear_form()
            update_table()
        except mysql.connector.Error as e:
            logging.error(f"Database error: {e}")
            show_alert_dialog("Database Error", f"Error updating teacher: {e}", is_error=True)
            page.update()

    def delete_teacher(e):
        logging.debug("Delete button clicked")
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Please select a teacher to delete!", is_error=True)
            logging.warning("Delete failed: No teacher selected")
            page.update()
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM teachers WHERE Teacher_ID=%s", (selected_id.current,))
            conn.commit()
            conn.close()
            show_alert_dialog("Success", "Teacher deleted successfully")
            logging.info(f"Deleted teacher: {selected_id.current}")
            clear_form()
            update_table()
        except mysql.connector.Error as e:
            logging.error(f"Database error: {e}")
            show_alert_dialog("Database Error", f"Error deleting teacher: {e}", is_error=True)
            page.update()

    def search_click(e):
        logging.debug("Search button clicked")
        update_table(search_field.value.strip())

    btns = ft.Row([
        ft.ElevatedButton(
            text="Add",
            on_click=add_teacher,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                bgcolor=ft.colors.BLUE_600,
                color=ft.colors.WHITE,
                elevation={"default": 5, "hovered": 8},
                animation_duration=300,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            )
        ),
        ft.ElevatedButton(
            text="Update",
            on_click=update_teacher,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                bgcolor=ft.colors.AMBER_600,
                color=ft.colors.WHITE,
                elevation={"default": 5, "hovered": 8},
                animation_duration=300,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            )
        ),
        ft.ElevatedButton(
            text="Delete",
            on_click=delete_teacher,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                bgcolor=ft.colors.RED_600,
                color=ft.colors.WHITE,
                elevation={"default": 5, "hovered": 8},
                animation_duration=300,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            )
        ),
        ft.ElevatedButton(
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
            )
        ),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    search_row = ft.Row([
        search_field,
        ft.ElevatedButton(
            text="Search",
            on_click=search_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                bgcolor=ft.colors.BLUE_600,
                color=ft.colors.WHITE,
                elevation={"default": 5, "hovered": 8},
                animation_duration=300,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            )
        )
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    data_table_container = ft.Container(
        content=ft.Column(
            [data_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        padding=10,
        expand=True,
        height=300
    )

    card = ft.Container(
        content=ft.Column([
            ft.Text(
                "Teacher Management",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.WHITE,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Add, update, or delete teacher records",
                size=16,
                color=ft.colors.BLUE_200,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            full_name,
            email,
            phone,
            username,
            password,
            btns,
            search_row,
            data_table_container
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, spread_radius=5, color=ft.colors.with_opacity(0.3, ft.colors.BLACK))
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
        )
    )
    page.add(background)
    update_table()

if __name__ == "__main__":
    ft.app(target=main)