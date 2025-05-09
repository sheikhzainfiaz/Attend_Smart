import flet as ft
import os
import pickle
import cv2
import numpy as np
import face_recognition
import logging
import asyncio
from back_button import create_back_button
from Dash import show_main

# Constants
IMAGE_DIR = "photos"
ENCODE_FILE = "EncodeFile.p"

def main(page: ft.Page):
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.debug("Starting face recognition training application")

    # Window settings
    page.title = "Face Recognition System - Train"
    page.window_width = 1920
    page.window_height = 1080
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.scroll = None

    # Colors and styles
    primary_color = ft.colors.BLUE_500
    accent_color = ft.colors.BLUE_800
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.GREY_900, ft.colors.BLUE_GREY_800]
    )

    # Progress bar components
    progress_bar = ft.ProgressBar(value=0, width=400, color=accent_color, bgcolor=ft.Colors.GREY_600, visible=False)
    progress_text = ft.Text("Training: 0%", color=ft.Colors.WHITE, size=14, visible=False)

    def show_alert_dialog(title, message):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=ft.Colors.WHITE),
            content=ft.Text(message, color=ft.Colors.WHITE),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(dialog))],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.BLUE_GREY_900,
        )

        def close_dialog(dlg):
            dlg.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def train_classifier_async():
        """Encode all faces in the Images directory and save to a pickle file asynchronously."""
        encode_list = []
        student_ids = []

        if not os.path.exists(IMAGE_DIR):
            show_alert_dialog("Error", f"Directory {IMAGE_DIR} does not exist.")
            progress_bar.visible = False
            progress_text.visible = False
            page.update()
            return

        # Count total images for progress calculation
        total_images = 0
        for student_folder in os.listdir(IMAGE_DIR):
            folder_path = os.path.join(IMAGE_DIR, student_folder)
            if os.path.isdir(folder_path):
                total_images += len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

        if total_images == 0:
            show_alert_dialog("Error", "No images found in the directory.")
            progress_bar.visible = False
            progress_text.visible = False
            page.update()
            return

        processed_images = 0

        for student_folder in os.listdir(IMAGE_DIR):
            folder_path = os.path.join(IMAGE_DIR, student_folder)
            if not os.path.isdir(folder_path):
                continue

            for filename in os.listdir(folder_path):
                img_path = os.path.join(folder_path, filename)
                img = cv2.imread(img_path)
                if img is None:
                    show_alert_dialog("Error", f"Could not load image {img_path}")
                    continue

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                faces = face_recognition.face_encodings(img_rgb)

                if faces:
                    encode_list.append(faces[0])
                    student_ids.append(student_folder)
                else:
                    show_alert_dialog("Error", f"No face found in {img_path}")

                # Update progress
                processed_images += 1
                progress = processed_images / total_images
                progress_bar.value = progress
                progress_text.value = f"Training: {int(progress * 100)}%"
                page.update()
                await asyncio.sleep(0)  # Yield control to event loop

        if not encode_list:
            show_alert_dialog("Error", "No faces encoded.")
            progress_bar.visible = False
            progress_text.visible = False
            page.update()
            return

        try:
            with open(ENCODE_FILE, 'wb') as file:
                pickle.dump((encode_list, student_ids), file)
            show_alert_dialog("Success", f"Encoding complete. Total faces encoded: {len(encode_list)}")
        except Exception as e:
            show_alert_dialog("Error", f"Failed to save encodings: {str(e)}")
        finally:
            progress_bar.visible = False
            progress_text.visible = False
            page.update()

    def train_classifier(e):
        """Start the training process with a progress bar."""
        progress_bar.visible = True
        progress_text.visible = True
        progress_bar.value = 0
        progress_text.value = "Training: 0%"
        page.update()

        async def run_training():
            await train_classifier_async()

        asyncio.run_coroutine_threadsafe(run_training(), page.loop)

    # Train button with spherical design and icon only
    train_button = ft.ElevatedButton(
        content=ft.Icon(ft.icons.FACE_6, color=ft.Colors.WHITE, size=28),
        on_click=train_classifier,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=50),
            padding=ft.padding.all(20),
            bgcolor=primary_color,
            color=ft.Colors.WHITE,
            elevation={"default": 10, "hovered": 15},
            animation_duration=400,
            overlay_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            side=ft.BorderSide(2, ft.Colors.with_opacity(0.4, ft.Colors.WHITE)),
            shadow_color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
        ),
        tooltip="Start training the face recognition model",
    )

    # Card layout with integrated progress bar
    card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.icons.SCHOOL, color=accent_color, size=36),
                        ft.Text(
                            "Train Face Recognition Model",
                            size=32,
                            weight=ft.FontWeight.W_700,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                ft.Text(
                    "Encode student faces for recognition",
                    size=18,
                    color=ft.Colors.GREY_300,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    [train_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    [
                        progress_bar,
                        ft.Container(width=20),
                        progress_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
        ),
        padding=60,
        width=950,
        bgcolor=card_bg,
        border_radius=28,
        shadow=ft.BoxShadow(
            blur_radius=50,
            spread_radius=10,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        ),
        animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
        scale=ft.transform.Scale(scale=1.0),
        on_hover=lambda e: setattr(
            e.control, "scale", ft.transform.Scale(scale=1.04 if e.data == "true" else 1.0)
        ),
    )

    # Create back button for admin dashboard (unchanged)
    back_btn = create_back_button(
        page,
        show_main,
        primary_color=primary_color,
        teacher_id=None,
        on_click=lambda e: [page.controls.clear(), show_main(page)]
    )

    # Background with radial gradient
    background = ft.Container(
        content=ft.Stack([
            card,
            ft.Container(
                content=back_btn,
                top=20,
                left=20,
            ),
        ]),
        alignment=ft.alignment.center,
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.Alignment(0, -0.5),
            radius=1.5,
            colors=[
                ft.Colors.with_opacity(0.6, primary_color),
                ft.Colors.with_opacity(0.4, accent_color),
                ft.Colors.BLACK,
            ],
        ),
    )

    page.controls.clear()
    page.add(background)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)