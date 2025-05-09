import flet as ft
import time
import login  # Importing the login module (teacher management page)

def main(page: ft.Page):
    # Configure the splash screen to match teacher management page styling
    page.title = "Teacher Management - Face Recognition System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    # page.scroll = ft.ScrollMode.AUTO

    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900]
    )

   

    # Logo with animation (fade-in and scale)
    logo = ft.Image(
        src="assests\logo.png",  # Local image in assets folder
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
        opacity=0,  # Start invisible for fade-in
        animate_opacity=ft.Animation(duration=1000, curve=ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(duration=1000, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    # Progress bar
    progress_bar = ft.ProgressBar(
        width=400,
        value=0,
        bar_height=10,
        color=accent_color,  # Match accent color (CYAN_400)
        bgcolor=ft.colors.BLUE_GREY_900,  # Match card background
    )

    # Loading text
    loading_text = ft.Text(
        value="Loading...",
        size=20,
        font_family="Helvetica",
        style=ft.TextStyle(italic=True),
        color=accent_color,  # Match accent color
        weight=ft.FontWeight.BOLD,
    )

    # Card container for splash screen content
    splash_card = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Attend Smart",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                logo,
                progress_bar,
                loading_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        padding=40,
        width=800,
        bgcolor=card_bg,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, spread_radius=5, color=ft.colors.with_opacity(0.3, ft.colors.BLACK)),
    )

    # Background with radial gradient
    background = ft.Container(
        content=ft.Stack([splash_card]),
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

    # Add content to the page
    page.add(background)

    # Animate logo (fade-in and scale up slightly)
    logo.opacity = 1
    logo.scale = 1.1  # Slight scale-up effect
    logo.update()

    # Animate progress bar
    steps = 10
    for i in range(steps + 1):
        progress_bar.value = i / steps
        progress_bar.update()
        time.sleep(3 / steps)  # Spread over 3 seconds

    # Clear splash screen and transition to login page
    page.controls.clear()
    page.update()

    # Call the login page's main function (teacher management page)
    login.main(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")