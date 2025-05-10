import flet as ft
import mysql.connector
import logging
import re
from back_button import create_back_button
from Dash import show_main
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def send_teacher_notification(teacher_email, teacher_name, teacher_phone, username, password, action="added"):
    if not teacher_email or not isinstance(teacher_email, str) or teacher_email.strip() == "":
        return  # Skip if email is invalid or empty

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action_text = "added to" if action == "added" else "updated in"
    message = Mail(
        from_email='support@mzstyle.top',
        to_emails=teacher_email,
        subject=f'Attend Smart: Teacher {action.capitalize()} Notification',
        html_content=f"""
        <h2>Teacher {action.capitalize()} Notification</h2>
        <p>Hello, <strong>{teacher_name}</strong></p>
        <p>Your details have been {action_text} the Attend Smart - Facial Recognition Attendance System at <strong>{current_time}</strong>.</p>
        <p><strong>Your Details:</strong></p>
        <ul>
            <li>Name: {teacher_name}</li>
            <li>Email: {teacher_email}</li>
            <li>Phone: {teacher_phone}</li>
        </ul>
        
        <p><strong>Your Key Credentials:</strong></p>
        <ul>
            <li>Username: {username}</li>
            <li>Password: {password}</li>
        </ul>
        <p>Please keep your credentials secure and do not share them.</p>
        <p>Best regards,<br>Attend Smart Team</p>
        """
    )

    try:
        sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent to {teacher_email}: {response.status_code}")
    except Exception as e:
        print(f"Error sending email to {teacher_email}: {e}")

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

    show_password = ft.Ref[bool]()
    show_password.current = False

    def toggle_password_visibility(e):
        show_password.current = not show_password.current
        password.password = not show_password.current
        password.suffix = ft.IconButton(
            icon=ft.icons.VISIBILITY_OFF if show_password.current else ft.icons.VISIBILITY,
            on_click=toggle_password_visibility,
            icon_color=ft.colors.BLUE_200,
            style=ft.ButtonStyle(padding=0)
        )
        page.update()

    # Add custom input filters before TextField definitions
    class LettersAndSpacesInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[a-zA-Z\s]*$')

    class EmailInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[a-zA-Z0-9._%+-@]*$')

    class UsernameInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[a-zA-Z0-9_]*$')

    class PasswordInputFilter(ft.InputFilter):
        def __init__(self):
            super().__init__(regex_string=r'^[a-zA-Z0-9@#$%!&*-_+?=]*$')

    # Updated TextField definitions
    full_name = ft.TextField(
        label="Full Name",
        prefix_icon=ft.icons.PERSON,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        max_length=50,
        input_filter=LettersAndSpacesInputFilter(),
        on_change=lambda e: validate_full_name(e.control.value)
    )
    email = ft.TextField(
        label="Email",
        prefix_icon=ft.icons.EMAIL,
        max_length=30,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        input_filter=EmailInputFilter(),
        on_change=lambda e: validate_email(e.control.value)
    )
    phone = ft.TextField(
        label="Phone",
        prefix_icon=ft.icons.PHONE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=11,
        on_change=lambda e: validate_phone(e.control.value)
    )
    username = ft.TextField(
        label="Username",
        prefix_icon=ft.icons.ACCOUNT_CIRCLE,
        max_length=12,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        input_filter=UsernameInputFilter(),
        on_change=lambda e: validate_username(e.control.value)
    )
    password = ft.TextField(
        label="Password",
        prefix_icon=ft.icons.LOCK,
        password=True,
        max_length=16,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        input_filter=PasswordInputFilter(),  # Restrict password input
        suffix=ft.IconButton(
            icon=ft.icons.VISIBILITY,
            on_click=toggle_password_visibility,
            icon_color=ft.colors.BLUE_200,
            style=ft.ButtonStyle(padding=0)
        ),
        on_change=lambda e: validate_password(e.control.value)
    )

    def validate_full_name(value):
        if not value:
            full_name.border_color = accent_color
            full_name.error_text = None
        elif len(value) < 4:
            full_name.border_color = ft.colors.RED_400
            full_name.error_text = "Full name must be at least 4 characters"
        elif len(value) > 50:
            full_name.border_color = ft.colors.RED_400
            full_name.error_text = "Full name cannot exceed 50 characters"
        else:
            full_name.border_color = ft.colors.GREEN_600
            full_name.error_text = None
        page.update()

    # Validation function for email
    def validate_email(value):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not value:
            email.border_color = accent_color
            email.error_text = None
        elif len(value) > 30:
            email.border_color = ft.colors.RED_400
            email.error_text = "Email cannot exceed 30 characters"
        elif not re.match(email_pattern, value):
            email.border_color = ft.colors.RED_400
            email.error_text = "Invalid email format"
        else:
            email.border_color = ft.colors.GREEN_600
            email.error_text = None
        page.update()

    # Validation function for phone
    def validate_phone(value):
        if not value:
            phone.border_color = accent_color
            phone.error_text = None
        elif len(value) != 11:
            phone.border_color = ft.colors.RED_400
            phone.error_text = "Phone must be exactly 11 digits"
        else:
            phone.border_color = ft.colors.GREEN_600
            phone.error_text = None
        page.update()

    # Validation function for username
    def validate_username(value):
        username_pattern = r'^[a-zA-Z0-9_]{4,12}$'
        if not value:
            username.border_color = accent_color
            username.error_text = None
            page.update()
            return
        if len(value) < 4:
            username.border_color = ft.colors.RED_400
            username.error_text = "Username must be at least 4 characters"
            page.update()
            return
        if len(value) > 12:
            username.border_color = ft.colors.RED_400
            username.error_text = "Username cannot exceed 12 characters"
            page.update()
            return
        if not re.match(username_pattern, value):
            username.border_color = ft.colors.RED_400
            username.error_text = "Username must be 4-12 characters, only letters, digits, or underscore"
            page.update()
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM teachers WHERE Username=%s AND Teacher_ID!=%s", (value, selected_id.current or 0))
            if cursor.fetchone():
                username.border_color = ft.colors.RED_400
                username.error_text = "Username already in use"
            else:
                username.border_color = ft.colors.GREEN_600
                username.error_text = None
            conn.close()
        except Exception as e:
            username.border_color = ft.colors.RED_400
            username.error_text = "Error checking username"
        page.update()

    # Validation function for password
    def validate_password(value):
        password_pattern = r'^[a-zA-Z0-9@#$%]*$'
        if not value:
            password.border_color = accent_color
            password.error_text = None
        elif len(value) < 7:
            password.border_color = ft.colors.RED_400
            password.error_text = "Password must be at least 7 characters"
        elif len(value) > 16:
            password.border_color = ft.colors.RED_400
            password.error_text = "Password cannot exceed 16 characters"
        elif not re.match(password_pattern, value):
            password.border_color = ft.colors.RED_400
            password.error_text = "Password can only contain letters, digits, and special characters"
        else:
            password.border_color = ft.colors.GREEN_600
            password.error_text = None
        page.update()

    search_field = ft.TextField(
        label="Search Teachers",
        hint_text="Enter name or username",
        prefix_icon=ft.icons.SEARCH,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
        on_change=lambda e: update_table(e.control.value.strip())
    )

    for field in [full_name, email, phone, username, password]:
        field.border_color = accent_color
        field.focused_border_color = primary_color
        field.filled = True
        field.bgcolor = ft.colors.with_opacity(0.05, ft.colors.WHITE)
        field.border_radius = 10
        field.label_style = ft.TextStyle(color=ft.colors.BLUE_200)
        field.hint_style = ft.TextStyle(color=ft.colors.BLUE_200)

    selected_id = ft.Ref[str]()

    def reset_field_borders():
        for field in [full_name, email, phone, username, password]:
            field.border_color = accent_color
            field.error_text = None
        page.update()

    def validate_fields(fields):
        reset_field_borders()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        username_pattern = r'^[a-zA-Z0-9_]{4,12}$'
        password_pattern = r'^[a-zA-Z0-9@#$%]*$'
        missing_fields = []
        for field, value in fields:
            if not value:
                field.border_color = ft.colors.RED_400
                missing_fields.append(field.label)
            elif field == phone and len(value) != 11:
                field.border_color = ft.colors.RED_400
                field.error_text = "Phone must be 11 digits"
                missing_fields.append(field.label)
            elif field == email and not re.match(email_pattern, value):
                field.border_color = ft.colors.RED_400
                field.error_text = "Invalid email format"
                missing_fields.append(field.label)
            elif field == username:
                if not re.match(username_pattern, value):
                    field.border_color = ft.colors.RED_400
                    field.error_text = "Username must be 4-12 characters, only letters, digits, or underscore"
                    missing_fields.append(field.label)
                else:
                    try:
                        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                        cursor = conn.cursor()
                        cursor.execute("SELECT Username FROM teachers WHERE Username=%s AND Teacher_ID!=%s", (value, selected_id.current or 0))
                        if cursor.fetchone():
                            field.border_color = ft.colors.RED_400
                            field.error_text = "Username already in use"
                            missing_fields.append(field.label)
                        conn.close()
                    except Exception as e:
                        field.border_color = ft.colors.RED_400
                        field.error_text = "Error checking username"
                        missing_fields.append(field.label)
            elif field == password:
                if not re.match(password_pattern, value):
                    field.border_color = ft.colors.RED_400
                    field.error_text = "Password can only contain letters, digits, and @#$%"
                    missing_fields.append(field.label)
                elif len(value) < 7 or len(value) > 16:
                    field.border_color = ft.colors.RED_400
                    field.error_text = "Password must be 7-16 characters"
                    missing_fields.append(field.label)
            elif field == full_name and len(value) > 50:
                field.border_color = ft.colors.RED_400
                field.error_text = "Name cannot exceed 50 characters"
                missing_fields.append(field.label)
        page.update()
        if len(missing_fields) == 1:
            return f"{missing_fields[0]} is required!"
        elif missing_fields:
            return f"The following fields are required: {', '.join(missing_fields)}"
        return None

    def clear_form():
        full_name.value = email.value = phone.value = username.value = password.value = ""
        search_field.value = ""
        selected_id.current = None
        reset_field_borders()
        update_table()
        page.update()

    def fetch_teachers(search_term=""):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            if search_term:
                cursor.execute("SELECT Teacher_ID, Full_Name, Email, Phone, Username FROM teachers WHERE Full_Name LIKE %s OR Username LIKE %s", (f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT Teacher_ID, Full_Name, Email, Phone, Username FROM teachers")
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            show_alert_dialog("Error", f"Error fetching data: {e}", is_error=True)
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
            reset_field_borders()
            page.update()
        except Exception as e:
            show_alert_dialog("Error", f"Select error: {e}", is_error=True)

    def add_teacher(e):
        fields = [
            (full_name, full_name.value.strip()),
            (email, email.value.strip()),
            (phone, phone.value.strip()),
            (username, username.value.strip()),
            (password, password.value.strip()),
        ]
        error_message = validate_fields(fields)
        if error_message:
            show_alert_dialog("Validation Error", error_message, is_error=True)
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO teachers (Full_Name, Email, Phone, Username, Password) VALUES (%s, %s, %s, %s, %s)",
                           (full_name.value, email.value, phone.value, username.value, password.value))
            conn.commit()
            conn.close()
            # Send email notification
            send_teacher_notification(
                teacher_email=email.value.strip(),
                teacher_name=full_name.value.strip(),
                teacher_phone=phone.value.strip(),
                username=username.value.strip(),
                password=password.value.strip(),
                action="added"
            )
            reset_field_borders()
            show_alert_dialog("Success", "Teacher added successfully!", is_success=True)
            clear_form()
            update_table()
        except Exception as e:
            show_alert_dialog("Error", f"Add error: {e}", is_error=True)

    def update_teacher(e):
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Select a teacher to update", is_error=True)
            return

        fields = [
            (full_name, full_name.value.strip()),
            (email, email.value.strip()),
            (phone, phone.value.strip()),
            (username, username.value.strip()),
            (password, password.value.strip()),
        ]
        error_message = validate_fields(fields)
        if error_message:
            show_alert_dialog("Validation Error", error_message, is_error=True)
            return

        def confirm_update():
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                cursor = conn.cursor()
                cursor.execute("UPDATE teachers SET Full_Name=%s, Email=%s, Phone=%s, Username=%s, Password=%s WHERE Teacher_ID=%s",
                               (full_name.value, email.value, phone.value, username.value, password.value, selected_id.current))
                conn.commit()
                conn.close()
                # Send email notification
                send_teacher_notification(
                    teacher_email=email.value.strip(),
                    teacher_name=full_name.value.strip(),
                    teacher_phone=phone.value.strip(),
                    username=username.value.strip(),
                    password=password.value.strip(),
                    action="updated"
                )
                reset_field_borders()
                show_alert_dialog("Success", "Teacher updated successfully!", is_success=True)
                clear_form()
                update_table()
            except Exception as e:
                show_alert_dialog("Error", f"Update error: {e}", is_error=True)

        show_confirm_dialog("Confirm Update", "Are you sure you want to update this teacher?", confirm_update)

    def delete_teacher(e):
        if not selected_id.current:
            show_alert_dialog("Validation Error", "Select a teacher to delete", is_error=True)
            return

        def confirm_delete():
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teachers WHERE Teacher_ID=%s", (selected_id.current,))
                conn.commit()
                conn.close()
                reset_field_borders()
                show_alert_dialog("Success", "Teacher deleted successfully!", is_success=True)
                clear_form()
                update_table()
            except Exception as e:
                show_alert_dialog("Error", f"Delete error: {e}", is_error=True)

        show_confirm_dialog("Confirm Delete", "Are you sure you want to delete this teacher?", confirm_delete)

    btns = ft.Row([
        ft.ElevatedButton("Add Teacher", on_click=add_teacher, bgcolor=primary_color, color=ft.colors.WHITE,
                          style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20, vertical=15), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))),
        ft.ElevatedButton("Update", on_click=update_teacher, bgcolor=ft.colors.AMBER_600, color=ft.colors.WHITE,
                          style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20, vertical=15), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))),
        ft.ElevatedButton("Delete", on_click=delete_teacher, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE,
                          style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20, vertical=15), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))),
        ft.ElevatedButton("Clear", on_click=lambda e: clear_form(), bgcolor=ft.colors.GREY_600, color=ft.colors.WHITE,
                          style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20, vertical=15), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))),
    ], alignment=ft.MainAxisAlignment.CENTER)

    card = ft.Container(
        content=ft.Column([
            ft.Text("Teacher Management", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            full_name, email, phone, username, password,
            btns,
            search_field,
            ft.Container(
                content=ft.Column([
                    data_table
                ], scroll=ft.ScrollMode.AUTO),
                padding=10,
                bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                border_radius=10,
                height=250,
                alignment=ft.alignment.center,
                width=750
            )
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, spread_radius=5, color=ft.colors.with_opacity(0.3, ft.colors.BLACK))
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
    ft.app(target=main)