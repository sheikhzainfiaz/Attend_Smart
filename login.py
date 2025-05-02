import flet as ft
import mysql.connector
from Dash import show_main
from teacher_dashboard import teacher_dashboard

def main(page: ft.Page):
    page.title = "Login - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.scroll = None

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
            bgcolor=ft.colors.WHITE
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Input fields with modern styling
    username = ft.TextField(
        label="Username",
        hint_text="Enter your username",
        autofocus=True,
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
    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.LOCK_OUTLINE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
    )
    role_dropdown = ft.Dropdown(
        label="Login As",
        options=[
            ft.dropdown.Option("admin", text="Admin"),
            ft.dropdown.Option("teacher", text="Teacher")
        ],
        hint_text="Select Role",
        value=None,
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.25, ft.colors.BLACK),
        border_radius=10,
        prefix_icon=ft.icons.GROUP,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
    )

    # Helper function to reset field borders
    def reset_field_borders():
        username.border_color = accent_color
        password.border_color = accent_color
        role_dropdown.border_color = accent_color
        page.update()

    # Helper function to highlight empty fields and get error message
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

    def login_click(e):
        uname = username.value.strip() if username.value else ""
        pwd = password.value.strip() if password.value else ""
        role = role_dropdown.value

        # Validate all fields
        fields = [
            (username, uname),
            (password, pwd),
            (role_dropdown, role),
        ]
        error_message = validate_fields(fields)
        if error_message:
            show_alert_dialog("Validation Error", error_message, is_error=True)
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

            table = "admins" if role == "admin" else "teachers"
            # Modified query to fetch both password and name (for teachers)
            if role == "admin":
                cursor.execute(f"SELECT password FROM {table} WHERE username=%s", (uname,))
            else:
                cursor.execute(f"SELECT password, Teacher_ID FROM {table} WHERE username=%s", (uname,))
            
            result = cursor.fetchone()
            conn.close()

            if result:
                if result[0] == pwd:
                    show_alert_dialog("Success", "Login successful!", is_success=True)
                    if role == "admin":
                        show_main(page)
                    else:
                        # For teachers, get the name from the query result (second column)
                        teacher_id = result[1] if result[1] else "Teacher"  # Fallback if name is null
                        teacher_dashboard(page, teacher_id)
                    return
                else:
                    show_alert_dialog("Login Failed", "Incorrect password", is_error=True)
            else:
                show_alert_dialog("Login Failed", "Username not found", is_error=True)

        except mysql.connector.Error as err:
            show_alert_dialog("Database Error", f"Database Error: {err}", is_error=True)

    # Login button with hover effect
    login_btn = ft.ElevatedButton(
        text="Login",
        on_click=login_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            bgcolor=primary_color,
            color=ft.colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        ),
    )

    # Card with gradient background and subtle animation
    card = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Face Recognition System",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Login to continue",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                username,
                password,
                role_dropdown,
                login_btn,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        padding=40,
        width=420,
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

    # Background gradient overlay
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
    ft.app(target=main)