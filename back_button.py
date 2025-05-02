import flet as ft
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def create_back_button(page, dashboard_func, primary_color=ft.Colors.BLUE_600, teacher_id=None, on_click=None):
    """
    Creates a styled Back button for Flet applications that returns to the specified dashboard.
    
    Args:
        page (ft.Page): The Flet page object for navigation.
        dashboard_func (callable): Function to render the dashboard (e.g., Dash.show_main or teacher_dashboard).
        primary_color (str): Button background color (default: ft.Colors.BLUE_600).
        teacher_id (int, optional): Teacher ID for teacher dashboard (default: None).
        on_click (callable, optional): Custom click handler (default: None).
    
    Returns:
        ft.ElevatedButton: A styled Back button with a chevron left icon.
    """
    def default_on_click(e):
        logging.debug("Back button clicked")
        page.controls.clear()
        if on_click:
            on_click(e)
        elif teacher_id is not None:
            logging.debug(f"Redirecting to teacher dashboard with teacher_id={teacher_id}")
            dashboard_func(page, teacher_id)
        else:
            logging.debug("Redirecting to admin dashboard")
            dashboard_func(page)
        page.update()
    
    # Set tooltip based on whether it's admin or teacher dashboard
    tooltip = "Back to Teacher Dashboard" if teacher_id is not None else "Back to Admin Dashboard"
    
    return ft.ElevatedButton(
        content=ft.Icon(ft.icons.CHEVRON_LEFT, color=ft.Colors.WHITE),
        on_click=default_on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.all(10),
            bgcolor=primary_color,
            color=ft.Colors.WHITE,
            elevation={"default": 5, "hovered": 8},
            animation_duration=300,
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        ),
        tooltip=tooltip,
    )