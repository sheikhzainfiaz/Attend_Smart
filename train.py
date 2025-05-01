import flet as ft
import os
import pickle
import cv2
import numpy as np
import face_recognition
import logging

# Constants
IMAGE_DIR = "photos"
ENCODE_FILE = "EncodeFile.p"

def main(page: ft.Page):
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.debug("Starting face recognition training application")

    # Window settings
    page.title = "Face Recognition System - Train"
    page.window_width = 1920  # Simulate maximized window
    page.window_height = 1080
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # Colors
    primary_color = ft.colors.BLUE_600
    accent_color = ft.colors.CYAN_400
    card_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[ft.colors.BLUE_GREY_800, ft.colors.BLUE_GREY_900]
    )

    def show_alert_dialog(title, message):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dialog():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Train button functionality
    def train_classifier(e):
        """Encode all faces in the Images directory and save to a pickle file."""
        if not os.path.exists(IMAGE_DIR):
            show_alert_dialog("Error", f"Directory {IMAGE_DIR} does not exist.")
            return

        encode_list = []
        student_ids = []

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

        if not encode_list:
            show_alert_dialog("Error", "No faces encoded.")
            return

        try:
            with open(ENCODE_FILE, 'wb') as file:
                pickle.dump((encode_list, student_ids), file)
            show_alert_dialog("Success", f"Encoding complete. Total faces encoded: {len(encode_list)}")
        except Exception as e:
            show_alert_dialog("Error", f"Failed to save encodings: {str(e)}")

    # Train button
    train_button = ft.ElevatedButton(
        text="Train",
        on_click=train_classifier,
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
    )

    # Card layout
    card = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Train Face Recognition Model",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Click the button below to encode student faces",
                    size=16,
                    color=ft.colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Row(
                    [train_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
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

    # Background with radial gradient
    background = ft.Container(
        content=card,
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

    page.controls.clear()
    page.add(background)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)