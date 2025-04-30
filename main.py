import flet as ft
import os
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def main(page: ft.Page):
    logging.debug("Starting main function")
    page.title = "Face Recognition System"
    page.bgcolor = ft.Colors.WHITE  # Light background
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Colors
    primary_color = ft.Colors.TEAL_600
    accent_color = ft.Colors.PINK_400
    button_bg = ft.Colors.TEAL_50

    # Title
    try:
        title = ft.Text(
            "Face Recognition Attendance System",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREY_900,
            text_align=ft.TextAlign.CENTER,
        )
        subtitle = ft.Text(
            "Manage your attendance system",
            size=18,
            color=ft.Colors.TEAL_700,
            text_align=ft.TextAlign.CENTER,
        )
    except Exception as e:
        logging.error(f"Title creation failed: {str(e)}")
        page.add(ft.Text(f"Error: {str(e)}", color=ft.Colors.RED_700))
        page.update()
        return

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

            # Grid layout
            try:
                grid = ft.GridView(
                    runs_count=4,  # 4 columns (4 buttons on top, 4 below)
                    max_extent=250,  # Larger buttons
                    child_aspect_ratio=1.0,
                    spacing=25,
                    run_spacing=25,
                    controls=buttons,
                    padding=25,
                )
            except Exception as e:
                logging.error(f"GridView failed: {str(e)}")
                grid = ft.Column(buttons, spacing=10)  # Fallback

            page.add(
                ft.Container(
                    content=ft.Column(
                        [title, subtitle, grid],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=30,
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

    # Start with home page
    try:
        logging.debug("Rendering home page")
        show_home_page()
    except Exception as e:
        show_error(f"Initial render failed: {str(e)}\n{traceback.format_exc()}")
        page.add(ft.Text(f"Initial render failed: {str(e)}", color=ft.Colors.RED_700))
        page.update()


if __name__ == "__main__":
    logging.debug("Running Flet app")
    ft.app(target=main)