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

    full_name = ft.TextField(label="Full Name", prefix_icon=ft.icons.PERSON, text_style=ft.TextStyle(color=ft.colors.WHITE))
    email = ft.TextField(label="Email", prefix_icon=ft.icons.EMAIL, text_style=ft.TextStyle(color=ft.colors.WHITE))
    phone = ft.TextField(label="Phone", prefix_icon=ft.icons.PHONE, text_style=ft.TextStyle(color=ft.colors.WHITE))
    username = ft.TextField(label="Username", prefix_icon=ft.icons.ACCOUNT_CIRCLE, text_style=ft.TextStyle(color=ft.colors.WHITE))
    password = ft.TextField(label="Password", prefix_icon=ft.icons.LOCK, password=True, text_style=ft.TextStyle(color=ft.colors.WHITE))

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
    )

    for field in [full_name, email, phone, username, password]:
        field.border_color = accent_color
        field.focused_border_color = primary_color
        field.filled = True
        field.bgcolor = ft.colors.with_opacity(0.05, ft.colors.WHITE)
        field.border_radius = 10
        field.label_style = ft.TextStyle(color=ft.colors.BLUE_200)
        field.hint_style = ft.TextStyle(color=ft.colors.BLUE_200)

    status_text = ft.Text("", color=ft.colors.RED_400)
    selected_id = ft.Ref[str]()

    def clear_form():
        full_name.value = email.value = phone.value = username.value = password.value = ""
        search_field.value = ""
        selected_id.current = None
        status_text.value = ""
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
            return data
        except Exception as e:
            status_text.value = f"Error fetching data: {e}"
            return []

    data_table = ft.DataTable(
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
                status_text.value = "Selected for update"
            page.update()
        except Exception as e:
            status_text.value = f"Select error: {e}"
            page.update()

    def add_teacher(e):
        if not all([full_name.value.strip(), email.value.strip(), phone.value.strip(), username.value.strip(), password.value.strip()]):
            status_text.value = "All fields are required!"
            status_text.color = ft.colors.RED_400
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO teachers (Full_Name, Email, Phone, Username, Password) VALUES (%s, %s, %s, %s, %s)",
                           (full_name.value, email.value, phone.value, username.value, password.value))
            conn.commit()
            conn.close()
            status_text.value = "Teacher added successfully"
            clear_form()
            update_table()
        except Exception as e:
            status_text.value = f"Add error: {e}"
        page.update()

    def update_teacher(e):
        if not selected_id.current:
            status_text.value = "Select a teacher to update"
        elif not all([full_name.value.strip(), email.value.strip(), phone.value.strip(), username.value.strip(), password.value.strip()]):
            status_text.value = "All fields are required!"
        else:
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                cursor = conn.cursor()
                cursor.execute("UPDATE teachers SET Full_Name=%s, Email=%s, Phone=%s, Username=%s, Password=%s WHERE Teacher_ID=%s",
                               (full_name.value, email.value, phone.value, username.value, password.value, selected_id.current))
                conn.commit()
                conn.close()
                status_text.value = "Teacher updated successfully"
                clear_form()
                update_table()
            except Exception as e:
                status_text.value = f"Update error: {e}"
        page.update()

    def delete_teacher(e):
        if not selected_id.current:
            status_text.value = "Select a teacher to delete"
        else:
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teachers WHERE Teacher_ID=%s", (selected_id.current,))
                conn.commit()
                conn.close()
                status_text.value = "Teacher deleted successfully"
                clear_form()
                update_table()
            except Exception as e:
                status_text.value = f"Delete error: {e}"
        page.update()

    def search_click(e):
        update_table(search_field.value.strip())

    btns = ft.Row([
        ft.ElevatedButton("Add", on_click=add_teacher, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE),
        ft.ElevatedButton("Update", on_click=update_teacher, bgcolor=ft.colors.AMBER_600, color=ft.colors.WHITE),
        ft.ElevatedButton("Delete", on_click=delete_teacher, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
        ft.ElevatedButton("Clear", on_click=lambda e: clear_form(), bgcolor=ft.colors.GREY_600, color=ft.colors.WHITE),
    ], alignment=ft.MainAxisAlignment.CENTER)

    search_row = ft.Row([
        search_field,
        ft.ElevatedButton("Search", on_click=search_click, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)
    ], alignment=ft.MainAxisAlignment.CENTER)

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
    )

    card = ft.Container(
        content=ft.Column([
            ft.Text("Teacher Management", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            full_name, email, phone, username, password,
            btns,
            search_row,
            data_table_container,
            status_text
        ], spacing=15),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, spread_radius=5, color=ft.colors.with_opacity(0.3, ft.colors.BLACK))
    )

    background = ft.Container(content=card, alignment=ft.alignment.center, expand=True)
    page.add(background)
    update_table()

if __name__ == "__main__":
    ft.app(target=main)