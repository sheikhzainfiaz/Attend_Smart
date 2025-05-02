import flet as ft
import os
import traceback
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def open_student_details(page: ft.Page):
    page.controls.clear()
    import Student
    Student.main(page)

def open_teacher_details(page: ft.Page):
    page.controls.clear()
    import teacher
    teacher.main(page)
    
def open_course_details(page: ft.Page):
    page.controls.clear()
    import Course
    Course.main(page)
    
def open_section_details(page: ft.Page):
    page.controls.clear()
    import Section
    Section.main(page)

def open_enrollment_details(page: ft.Page):
    page.controls.clear()
    import Enrollment
    Enrollment.main(page)
    
def open_train_data(page: ft.Page):
    page.controls.clear()
    import train
    train.main(page)

def show_main(page: ft.Page):
    logging.debug("Starting main function")
    page.title = "Face Recognition System"
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None

    # Dark Theme Colors
    primary_color = ft.Colors.BLUE_600
    accent_color = ft.Colors.CYAN_400
    text_color = ft.Colors.WHITE
    sub_text_color = ft.Colors.BLUE_200
    button_bg = ft.Colors.BLUE_700

    def show_error(message):
        logging.error(f"Error: {message}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.RED_600),
            bgcolor=ft.Colors.WHITE,
        )
        page.snack_bar.open = True
        page.update()

    def show_alert_dialog(title, message, is_success=False, is_error=False):
        logging.debug(f"Attempting to show AlertDialog: Title='{title}', Message='{message}', IsSuccess={is_success}, IsError={is_error}")
        try:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title, style=ft.TextStyle(color=text_color)),
                content=ft.Text(
                    message,
                    color=ft.Colors.GREEN_600 if is_success else ft.Colors.RED_600 if is_error else ft.Colors.BLACK
                ),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.Colors.WHITE
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
            page.add(ft.Text(f"Error: {ex}", color=ft.Colors.RED_600))
            page.update()

    def show_confirm_dialog(title, message, on_confirm):
        async def handle_confirm(e):
            dialog.open = False
            page.update()
            await on_confirm()  # Await the asynchronous on_confirm

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Yes", on_click=handle_confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def show_sub_page(title_text):
        try:
            page.controls.clear()
            page.update()

            content = ft.Column(
                [
                    ft.Text(
                        f"{title_text} Window",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=text_color,
                    ),
                    ft.Text(
                        f"This is the {title_text} page.",
                        size=16,
                        color=sub_text_color,
                    ),
                    ft.ElevatedButton(
                        "Back to Home",
                        on_click=lambda e: show_home_page(),
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            elevation=5,
                            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,
            )

            page.add(
                ft.Container(
                    content=content,
                    expand=True,
                    alignment=ft.alignment.center,
                    gradient=ft.RadialGradient(
                        center=ft.Alignment(0, -0.8),
                        radius=1.5,
                        colors=[
                            ft.Colors.with_opacity(0.2, primary_color),
                            ft.Colors.with_opacity(0.1, accent_color),
                            ft.Colors.BLACK,
                        ],
                    ),
                )
            )
            page.update()
        except Exception as e:
            show_error(f"Sub-page failed: {str(e)}\n{traceback.format_exc()}")

    async def show_home_page():
        try:
            page.controls.clear()
            page.update()

            title = ft.Text(
                "Face Recognition Attendance System",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=text_color,
                text_align=ft.TextAlign.CENTER,
            )
            subtitle = ft.Text(
                "Manage your attendance system",
                size=18,
                color=sub_text_color,
                text_align=ft.TextAlign.CENTER,
            )

            button_data_row1 = [
                ("Train Data", ft.Icons.CAST_FOR_EDUCATION, lambda e: open_train_data(page)),
                ("Student Details", ft.Icons.PERSON, lambda e: open_student_details(page)),
                ("Teacher Details", ft.Icons.PERSON_OUTLINE, lambda e: open_teacher_details(page)),
                ("Course Details", ft.Icons.BOOK, lambda e: open_course_details(page)),
            ]
            
            button_data_row2 = [
                ("Section Details", ft.Icons.VIEW_LIST, lambda e: open_section_details(page)),
                ("Enrollment Details", ft.Icons.HOW_TO_REG, lambda e: open_enrollment_details(page)),
                ("Exit", ft.Icons.EXIT_TO_APP, lambda e: show_confirm_dialog(
                    "Confirm Logout",
                    "Are you sure you want to log out?",
                    logout
                )),
            ]

            async def logout():
                logging.debug("Logout started")
                page.session.clear()  # Clear session if used
                page.controls.clear()
                page.update()  # Immediate UI update to show logout
                await redirect_to_login(page)  # Wait for login redirection

            async def redirect_to_login(page):
                try:
                    from login import main as login_main  # Import login form
                    login_main(page)  # Redirect to login page
                    page.update()  # Update after login is rendered
                    logging.debug("Logout completed")
                except Exception as e:
                    logging.error(f"Error in redirect_to_login: {str(e)}\n{traceback.format_exc()}")
                    show_error(f"Failed to redirect to login: {str(e)}")

            buttons_row1 = []
            buttons_row2 = []

            for text, icon, handler in button_data_row1 + button_data_row2:
                btn = ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(icon, size=100, color=ft.Colors.WHITE),
                                ft.Text(
                                    text,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=text_color,
                                    text_align=ft.TextAlign.CENTER,
                                    max_lines=2,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        padding=20,
                        bgcolor=button_bg,
                        border_radius=16,
                        width=200,
                        height=200,
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=16),
                        padding=0,
                        overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                        elevation={"": 4, "hovered": 8},
                        side={"hovered": ft.BorderSide(width=2, color=ft.Colors.CYAN_400)},
                    ),
                    on_click=handler,
                )
                if (text, icon, handler) in button_data_row1:
                    buttons_row1.append(btn)
                else:
                    buttons_row2.append(btn)

            # Header with title and subtitle centered
            header = ft.Column(
                [title, subtitle],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )

            row1 = ft.Row(
                controls=buttons_row1,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25,
            )

            row2 = ft.Row(
                controls=buttons_row2,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25,
            )

            page.add(
                ft.Container(
                    content=ft.Column(
                        [header, row1, row2],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=30,
                        expand=True,
                    ),
                    expand=True,
                    padding=20,
                    gradient=ft.RadialGradient(
                        center=ft.Alignment(0, -0.8),
                        radius=1.5,
                        colors=[
                            ft.Colors.with_opacity(0.2, primary_color),
                            ft.Colors.with_opacity(0.1, accent_color),
                            ft.Colors.BLACK,
                        ],
                    ),
                )
            )
            page.update()
        except Exception as e:
            show_error(f"Home page failed: {str(e)}\n{traceback.format_exc()}")
            page.add(ft.Text(f"Error rendering home page: {str(e)}", color=ft.Colors.RED_600))
            page.update()

    async def start_app():
        logging.debug("Rendering home page")
        await show_home_page()

    try:
        asyncio.run(start_app())
    except Exception as e:
        show_error(f"Initial render failed: {str(e)}\n{traceback.format_exc()}")
        page.add(ft.Text(f"Initial render failed: {str(e)}", color=ft.Colors.RED_600))
        page.update()

if __name__ == "__main__":
    logging.debug("Running Flet app")
    ft.app(target=show_main)