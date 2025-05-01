import flet as ft
import os
import traceback
import logging

# Do not configure logging here; move it inside a function or after imports

def configure_logging():
    """Configure logging after all imports are resolved to avoid circular imports."""
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def das_show(page: ft.Page, teacher_name="Teacher"):
    # Configure logging here, after imports are complete
    configure_logging()
    logging.debug("Starting das_show function")
    
    page.title = "Face Recognition System"
    page.bgcolor = ft.Colors.WHITE
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # Colors
    primary_color = ft.Colors.TEAL_600
    accent_color = ft.Colors.PINK_400
    button_bg = ft.Colors.TEAL_50

    # Welcome Section with proper styling
    def create_welcome_section():
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Welcome, ",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Container(
                        content=ft.Text(
                            teacher_name,
                            size=36,
                            weight=ft.FontWeight.BOLD,
                            color=accent_color,
                        ),
                        shadow=ft.BoxShadow(
                            blur_radius=4,
                            color=ft.Colors.GREY_400,
                            offset=ft.Offset(2, 2)
                        ),
                    ),
                    ft.Text("👋", size=36),  # Waving hand emoji
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            bgcolor=primary_color,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.GREY_400,
                offset=ft.Offset(0, 5),
            ),
            margin=ft.margin.only(bottom=20),
        )

    def show_error(message):
        logging.error(f"Error: {message}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.RED_700),
            bgcolor=ft.Colors.GREY_800,
        )
        page.snack_bar.open = True
        page.update()

    def show_sub_page(title_text):
        try:
            page.controls.clear()
            content = ft.Column(
                [
                    ft.Text(
                        f"{title_text} Window",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_900,
                    ),
                    ft.Text(
                        f"This is the {title_text} page.",
                        size=16,
                        color=ft.Colors.TEAL_700,
                    ),
                    ft.ElevatedButton(
                        "Back to Home",
                        on_click=lambda e: show_home_page(),
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=15,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )

            page.add(
                ft.Container(
                    content=content,
                    expand=True,
                    alignment=ft.alignment.center,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=[ft.Colors.TEAL_100, ft.Colors.WHITE],
                    ),
                )
            )
            page.update()
        except Exception as e:
            show_error(f"Sub-page failed: {str(e)}\n{traceback.format_exc()}")

    def open_images():
        try:
            os.startfile("data_img")
        except Exception as err:
            show_error(f"Could not open images: {str(err)}")

    def show_home_page():
        try:
            page.controls.clear()
            button_data = [
                ("Student Details", ft.Icons.PERSON, lambda e: show_sub_page("Student Details")),
                ("Face Detection", ft.Icons.CAMERA, lambda e: show_sub_page("Face Detection")),
                ("Attendance", ft.Icons.EVENT, lambda e: show_sub_page("Attendance")),
                ("Help Desk", ft.Icons.HELP_OUTLINE, lambda e: show_sub_page("Help Desk")),
                ("Train Data", ft.Icons.TRAIN, lambda e: show_sub_page("Train Data")),
                ("Photos", ft.Icons.PHOTO_LIBRARY, lambda e: open_images()),
                ("Developer", ft.Icons.CODE, lambda e: show_sub_page("Developer")),
                ("Exit", ft.Icons.EXIT_TO_APP, lambda e: page.window_close()),
            ]

            buttons = []
            for text, icon, handler in button_data:
                btn = ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(icon, size=70, color=accent_color),
                                ft.Text(
                                    text,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREY_900,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        padding=25,
                        bgcolor=button_bg,
                        border_radius=12,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=button_bg,
                        elevation={"pressed": 5, "": 3},
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=0,
                    ),
                    on_click=handler,
                    scale=ft.transform.Scale(scale=1.0),
                    on_hover=lambda e: e.control.update(
                        scale=ft.transform.Scale(scale=1.05 if e.data == "true" else 1.0),
                        elevation=6 if e.data == "true" else 3,
                    ),
                )
                buttons.append(btn)

            try:
                grid = ft.GridView(
                    runs_count=4,
                    max_extent=250,
                    child_aspect_ratio=1.0,
                    spacing=25,
                    run_spacing=25,
                    controls=buttons,
                    padding=25,
                )
            except Exception as e:
                logging.error(f"GridView failed: {str(e)}")
                grid = ft.Column(buttons, spacing=10)

            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            create_welcome_section(),
                            ft.Text(
                                "Face Recognition Attendance System",
                                size=24,
                                color=ft.Colors.TEAL_700,
                                weight=ft.FontWeight.W_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(
                                height=2,
                                width=50,
                                bgcolor=accent_color,
                                border_radius=2,
                                margin=ft.margin.only(bottom=20),
                            ),
                            ft.Text(
                                "Manage your attendance system",
                                size=18,
                                color=ft.Colors.TEAL_700,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            grid
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=[ft.Colors.TEAL_100, ft.Colors.WHITE],
                    ),
                )
            )
            page.update()
        except Exception as e:
            show_error(f"Home page failed: {str(e)}\n{traceback.format_exc()}")
            page.add(ft.Text(f"Error rendering home page: {str(e)}", color=ft.Colors.RED_700))
            page.update()

    try:
        logging.debug("Rendering home page")
        show_home_page()
    except Exception as e:
        show_error(f"Initial render failed: {str(e)}\n{traceback.format_exc()}")
        page.add(ft.Text(f"Initial render failed: {str(e)}", color=ft.Colors.RED_700))
        page.update()

if __name__ == "__main__":
    # Configure logging before running the app
    configure_logging()
    logging.debug("Running Flet app")
    ft.app(target=lambda page: das_show(page))