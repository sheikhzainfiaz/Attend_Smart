import flet as ft
import mysql.connector


def main(page: ft.Page):
    page.title = "Login - Face Recognition System"
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
        border_color=accent_color,
        focused_border_color=primary_color,
        filled=True,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
        border_radius=10,
        prefix_icon=ft.icons.GROUP,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        label_style=ft.TextStyle(color=ft.colors.BLUE_200),
        hint_style=ft.TextStyle(color=ft.colors.BLUE_200),
    )
    status_text = ft.Text("", color=ft.colors.RED_400, size=14, weight=ft.FontWeight.W_500)

    def login_click(e):
        uname = username.value.strip()
        pwd = password.value.strip()
        role = role_dropdown.value

        if not uname or not pwd or not role:
            status_text.value = "All fields are required!"
            status_text.color = ft.colors.RED_400
            page.update()
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="face_recognizer_db",
                port=3306
            )
            cursor = conn.cursor()

            table = "admins" if role == "admin" else "teachers"
            cursor.execute(f"SELECT password FROM {table} WHERE username=%s", (uname,))
            result = cursor.fetchone()
            conn.close()

            if result:
                if result[0] == pwd:
                    status_text.color = ft.colors.GREEN_400
                    status_text.value = f"{role.capitalize()} Login Successful!"
                else:
                    status_text.color = ft.colors.RED_400
                    status_text.value = "Incorrect password"
            else:
                status_text.color = ft.colors.RED_400
                status_text.value = "Username not found"

        except mysql.connector.Error as err:
            status_text.color = ft.colors.RED_400
            status_text.value = f"Database Error: {err}"

        page.update()

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
                status_text,
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