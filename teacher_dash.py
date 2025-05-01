import flet as ft
import mysql.connector
import logging
from manage_attendance import main_manage
from mark_attendance import main

def configure_logging():
    """Configure logging after all imports are resolved to avoid circular imports."""
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def teacher_dashboard(page: ft.Page, teacher_id: int):
    # Configure logging
    configure_logging()
    logging.debug("Starting teacher_dashboard function")

    page.title = "Teacher Dashboard - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0  # Remove padding to eliminate extra space
    page.scroll = None  # Disable scroll to prevent extra space

    # Colors
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

    # Fetch teacher's name from the database
    def fetch_teacher_name():
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="face_db", port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT Full_Name FROM teachers WHERE Teacher_ID = %s", (teacher_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            else:
                show_message("Teacher not found!", is_error=True)
                return "Unknown Teacher"
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            show_message(f"Database Error: {err}", is_error=True)
            return "Unknown Teacher"

    teacher_name = fetch_teacher_name()

    def create_welcome_section():
        return ft.Column(
            [
                ft.Text(
                    f"Welcome, {teacher_name}",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Face Recognition Attendance System",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

    def show_dummy_page(page_title):
        page.controls.clear()
        page.update()

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        page_title,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"Teacher ID: {teacher_id}",
                        size=16,
                        color=ft.colors.BLUE_200,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "Back to Dashboard",
                        on_click=lambda e: show_home_page(),
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
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                expand=True,  # Ensure the column takes up all available space
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
            expand=True,  # Ensure the container takes up the full page
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
        page.update()

    def show_home_page():
        page.controls.clear()
        page.update()

        button_data = [
            ("Mark Attendance", ft.icons.EVENT, lambda e: main(page, teacher_id)),
            ("Manage Attendance", ft.icons.LIST, lambda e: main_manage(page, teacher_id)),
            ("Exit", ft.icons.EXIT_TO_APP, lambda e: page.window_close()),
        ]

        buttons = []
        for text, icon, handler in button_data:
            btn = ft.ElevatedButton(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(icon, size=70, color=ft.colors.WHITE),
                            ft.Text(
                                text,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15,
                    ),
                    padding=25,
                ),
                style=ft.ButtonStyle(
                    bgcolor=primary_color,
                    elevation={"pressed": 5, "": 3},
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=0,
                    overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                ),
                on_click=handler,
                scale=ft.transform.Scale(scale=1.0),
                on_hover=lambda e: e.control.update(
                    scale=ft.transform.Scale(scale=1.05 if e.data == "true" else 1.0),
                    elevation=6 if e.data == "true" else 3,
                ),
            )
            buttons.append(btn)

        grid = ft.GridView(
            runs_count=3,
            max_extent=250,
            child_aspect_ratio=1.0,
            spacing=25,
            run_spacing=25,
            controls=buttons,
            padding=25,
        )

        card = ft.Container(
            content=ft.Column(
                [
                    create_welcome_section(),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    ft.Text(
                        "Manage your attendance system",
                        size=18,
                        color=ft.colors.BLUE_200,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    grid,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                expand=True,  # Ensure the column takes up all available space
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
            expand=True,  # Ensure the container takes up the full page
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
        page.update()

    try:
        logging.debug("Rendering home page")
        show_home_page()
    except Exception as e:
        show_message(f"Initial render failed: {str(e)}", is_error=True)
        page.add(ft.Text(f"Initial render failed: {str(e)}", color=ft.colors.RED_700))
        page.update()

if __name__ == "__main__":
    configure_logging()
    logging.debug("Running Flet app")
    ft.app(target=lambda page: teacher_dashboard(page, teacher_id=1))