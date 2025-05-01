import flet as ft
import os
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def open_student_details(page: ft.Page):
    # Add the student management page (the existing code of student.py)
    page.controls.clear()
    import Student  # This imports the student.py script
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
    
    
def show_main(page: ft.Page):
    logging.debug("Starting main function")
    page.title = "Face Recognition System"
    page.bgcolor = ft.colors.BLACK
    page.padding = 0  # Remove padding to eliminate extra space
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None  # Disable scroll to prevent extra space

    # Dark Theme Colors
    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    text_color = ft.colors.WHITE
    sub_text_color = ft.colors.BLUE_200
    button_bg = ft.colors.BLUE_700  # Consistent background color for all buttons

    def show_error(message):
        logging.error(f"Error: {message}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.RED_400),
            bgcolor=ft.colors.BLUE_GREY_800,
        )
        page.snack_bar.open = True
        page.update()

    def show_sub_page(title_text):
        try:
            # Clear all existing controls to ensure the new page replaces the dashboard
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
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            elevation=5,
                            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,  # Ensure the column takes up all available space
            )

            page.add(
                ft.Container(
                    content=content,
                    expand=True,  # Ensure the container takes up the full page
                    alignment=ft.alignment.center,
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
            # Clear all existing controls to ensure a clean slate
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
    ("Train Data", ft.Icons.TRAIN, lambda e: show_sub_page("Train Data")),
    ("Face Detection", ft.Icons.FACE, lambda e: show_sub_page("Face Detection")),
    ("Student Details", ft.Icons.PERSON, lambda e: open_student_details(page)),
    ("Teacher Details", ft.Icons.PERSON_OUTLINE, lambda e: open_teacher_details(page)),
    ("Course Details", ft.Icons.BOOK, lambda e: open_course_details(page)),
]
            
            button_data_row2 = [
    ("Section Details", ft.Icons.VIEW_LIST, lambda e: open_section_details(page)),
    ("Enrollment Details", ft.Icons.HOW_TO_REG, lambda e: open_enrollment_details(page)),
    ("Photos", ft.Icons.PHOTO_LIBRARY, lambda e: open_images()),
    ("Developer", ft.Icons.CODE, lambda e: show_sub_page("Developer")),
    ("Exit", ft.Icons.EXIT_TO_APP, lambda e: page.window_close()),
]

            buttons_row1 = []
            buttons_row2 = []

            for text, icon, handler in button_data_row1 + button_data_row2:
                btn = ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(icon, size=150, color=accent_color),
                                ft.Text(
                                    text,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=text_color,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=25,
                        bgcolor=button_bg,
                        border_radius=16,
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=16),
                        padding=0,
                        overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                        elevation={"": 4, "hovered": 8},
                    ),
                    on_click=handler,
                    scale=ft.transform.Scale(scale=1.0),
                    on_hover=lambda e: e.control.update(
                        scale=ft.transform.Scale(scale=1.05 if e.data == "true" else 1.0),
                    ),
                )
                if (text, icon, handler) in button_data_row1:
                    buttons_row1.append(btn)
                else:
                    buttons_row2.append(btn)

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
                        [title, subtitle, row1, row2],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=30,
                        expand=True,  # Ensure the column takes up all available space
                    ),
                    expand=True,  # Ensure the container takes up the full page
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
            )
            page.update()
        except Exception as e:
            show_error(f"Home page failed: {str(e)}\n{traceback.format_exc()}")
            page.add(ft.Text(f"Error rendering home page: {str(e)}", color=ft.colors.RED_400))
            page.update()

    try:
        logging.debug("Rendering home page")
        show_home_page()
    except Exception as e:
        show_error(f"Initial render failed: {str(e)}\n{traceback.format_exc()}")
        page.add(ft.Text(f"Initial render failed: {str(e)}", color=ft.colors.RED_400))
        page.update()

if __name__ == "__main__":
    logging.debug("Running Flet app")
    ft.app(target=show_main)