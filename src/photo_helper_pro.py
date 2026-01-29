"""
PHOTO HELPER PRO - v1.0
A beginner-friendly, all-in-one photo utility app built with Python.
Libraries: PySide6 (GUI), Pillow (Image Processing), rembg (Background Removal)
Author: Abdessamad ER-RAMY 
"""

# --- 1. IMPORTS ---
# We import all necessary libraries at the very top.

import sys
import os
from datetime import datetime

# PySide6 components for the Graphical User Interface (GUI)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
    QLineEdit, QComboBox, QSpinBox, QSlider, QGroupBox, QColorDialog
)
from PySide6.QtGui import QPixmap, QImage, QColor
from PySide6.QtCore import Qt

# Pillow (PIL) components for image processing
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

# rembg component for background removal
from rembg import remove

# --- 2. MAIN APPLICATION WINDOW CLASS ---
# This class defines the entire application, its layout, and all its functions.

class PhotoHelperPro(QMainWindow):
    def __init__(self):
        """
        This is the constructor. It runs when we first create the app window.
        """
        super().__init__()

        # --- Basic Window Setup ---
        self.setWindowTitle("Photo Helper Pro")
        self.setGeometry(100, 100, 1200, 800)  # (x, y, width, height)

        # --- Image Storage Variables ---
        # We need variables to keep track of the images we are working with.
        self.original_image = None  # Stores the image as it was loaded
        self.current_image = None   # Stores the image after effects are applied
        
        # --- Storage for Colors and Paths ---
        # These will be updated by our color pickers and dialogs
        self.current_text_color = (255, 255, 255)  # Default: White
        self.current_border_color = (0, 0, 0)      # Default: Black
        self.current_bg_color = (255, 255, 255)    # Default: White
        self.logo_path = None                      # Path to the logo image

        # --- Initialize the User Interface ---
        self.init_ui()

        # --- Apply the Dark Theme ---
        # We use QSS (Qt Style Sheets), which is like CSS for apps.
        self.setStyleSheet(self.get_dark_theme_stylesheet())

    def init_ui(self):
        """
        Sets up the main layout and all the widgets (buttons, tabs, etc.).
        """
        # --- Main Layout ---
        # We use a QHBoxLayout (Horizontal) to split the app into two parts:
        # 1. Left Panel (for controls)
        # 2. Right Panel (for image preview)
        main_layout = QHBoxLayout()

        # --- 1. Left Panel (Controls) ---
        left_panel_layout = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel_layout)
        left_panel_widget.setFixedWidth(400) # Give the left panel a fixed width

        # --- Top Buttons (Load, Save, Reset) ---
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        left_panel_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save As / Convert")
        self.save_button.clicked.connect(self.save_image)
        left_panel_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Reset to Original")
        self.reset_button.clicked.connect(self.reset_image)
        left_panel_layout.addWidget(self.reset_button)

        # --- Operations Tabs ---
        # QTabWidget is perfect for organizing many functions.
        self.tabs = QTabWidget()
        
        # We create a separate function for each tab to keep the code clean.
        self.tabs.addTab(self.create_resize_tab(), "1. Resize")
        self.tabs.addTab(self.create_crop_tab(), "2. Crop")
        self.tabs.addTab(self.create_flip_rotate_tab(), "3. Flip/Rotate")
        self.tabs.addTab(self.create_filters_tab(), "4. Filters")
        self.tabs.addTab(self.create_text_tab(), "5. Add Text")
        self.tabs.addTab(self.create_logo_tab(), "6. Add Logo")
        self.tabs.addTab(self.create_border_tab(), "7. Add Border")
        self.tabs.addTab(self.create_background_tab(), "8. Background")
        self.tabs.addTab(self.create_enhance_tab(), "9. Enhance")
        # Function 10 (Convert) is handled by the "Save As" button.
        
        left_panel_layout.addWidget(self.tabs)

        # --- 2. Right Panel (Image Preview) ---
        right_panel_layout = QVBoxLayout()
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)

        self.image_preview_label = QLabel("Load an image to start editing")
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setMinimumSize(400, 400) # Min size
        self.image_preview_label.setStyleSheet("border: 2px dashed #555;")
        right_panel_layout.addWidget(self.image_preview_label)

        # --- Add Panels to Main Layout ---
        main_layout.addWidget(left_panel_widget)
        main_layout.addWidget(right_panel_widget, 1) # The '1' makes it stretch

        # --- Set Central Widget ---
        # This is the final container for the window's layout.
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # --- 3. CORE FUNCTIONS (Load, Save, Update) ---

    def load_image(self):
        """
        Opens a file dialog to let the user pick an image.
        """
        # Supported file types
        file_filter = "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        
        # Open the dialog. 'self' means it's a child of the main window.
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", file_filter)
        
        if file_path:  # If the user selected a file
            try:
                # Open the image with Pillow
                self.original_image = Image.open(file_path)
                
                # --- CRITICAL STEP FOR BEGINNERS ---
                # We .convert("RGBA") to make ALL images use the same format
                # (Red, Green, Blue, Alpha/Transparency).
                # This makes all other functions (like filters and saving) MUCH easier.
                self.original_image = self.original_image.convert("RGBA")
                
                # Create a copy for editing
                self.current_image = self.original_image.copy()
                
                # Show the image in the preview area
                self.update_preview()
                
            except Exception as e:
                self.show_error_message(f"Could not load image: {e}")

    def update_preview(self):
        """
        Updates the image preview label with self.current_image.
        This is one of the most important functions!
        """
        if self.current_image is None:
            return  # Do nothing if no image is loaded

        # Get image properties
        width = self.current_image.width
        height = self.current_image.height
        
        # Convert the Pillow Image to a QImage
        # We use .tobytes() to get the raw pixel data
        bytes_per_line = width * 4  # 4 bytes per pixel (R, G, B, A)
        q_image = QImage(self.current_image.tobytes(), width, height, bytes_per_line, QImage.Format_RGBA8888)

        # Convert the QImage to a QPixmap, which is what QLabel uses
        pixmap = QPixmap.fromImage(q_image)

        # --- Scale the pixmap to fit the label ---
        # We want to keep the aspect ratio so the image doesn't look stretched.
        label_size = self.image_preview_label.size()
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set the pixmap on the label
        self.image_preview_label.setPixmap(scaled_pixmap)

    def save_image(self):
        """
        Opens a "Save As" dialog to save the image in different formats.
        This covers "Convert to PNG/JPG/PDF".
        """
        if not self._check_image_loaded():
            return

        # Define the formats we support for saving
        file_filter = "PNG Image (*.png);;JPEG Image (*.jpg);;PDF Document (*.pdf)"
        
        file_path, selected_filter = QFileDialog.getSaveFileName(self, "Save Image As", "", file_filter)

        if file_path:  # If the user chose a location
            try:
                # --- Handle different file formats ---
                
                # PNG supports transparency, so we save it directly
                if selected_filter == "PNG Image (*.png)":
                    if not file_path.endswith(".png"): file_path += ".png"
                    self.current_image.save(file_path, "PNG")

                # JPG and PDF do NOT support transparency.
                # We must .convert("RGB") to remove the Alpha channel.
                elif selected_filter == "JPEG Image (*.jpg)":
                    if not file_path.endswith(".jpg"): file_path += ".jpg"
                    rgb_image = self.current_image.convert("RGB")
                    rgb_image.save(file_path, "JPEG", quality=95)

                elif selected_filter == "PDF Document (*.pdf)":
                    if not file_path.endswith(".pdf"): file_path += ".pdf"
                    rgb_image = self.current_image.convert("RGB")
                    rgb_image.save(file_path, "PDF", resolution=100.0)
                
                self.show_success_message(f"Image saved successfully to:\n{file_path}")

            except Exception as e:
                self.show_error_message(f"Could not save image: {e}")

    def reset_image(self):
        """
        Resets all changes back to the original loaded image.
        """
        if self.original_image:
            # Just make a fresh copy from the original
            self.current_image = self.original_image.copy()
            self.update_preview()
            self.show_success_message("Image has been reset to original.")
        else:
            self.show_error_message("No image is loaded to reset.")

    # --- 4. TAB CREATION FUNCTIONS ---
    # These functions build the UI for each tab.
    # This keeps the init_ui function clean.

    def create_resize_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Width (pixels):"))
        self.resize_width_input = QLineEdit()
        self.resize_width_input.setPlaceholderText("e.g., 1920")
        layout.addWidget(self.resize_width_input)

        layout.addWidget(QLabel("Height (pixels):"))
        self.resize_height_input = QLineEdit()
        self.resize_height_input.setPlaceholderText("e.g., 1080")
        layout.addWidget(self.resize_height_input)

        apply_button = QPushButton("Apply Resize")
        apply_button.clicked.connect(self.apply_resize)
        layout.addWidget(apply_button)
        return widget

    def create_crop_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        
        # We use QSpinBox for numbers, it's safer than QLineEdit
        layout.addWidget(QLabel("Left coordinate (X):"))
        self.crop_left_input = QSpinBox()
        self.crop_left_input.setMaximum(9999)
        layout.addWidget(self.crop_left_input)

        layout.addWidget(QLabel("Top coordinate (Y):"))
        self.crop_top_input = QSpinBox()
        self.crop_top_input.setMaximum(9999)
        layout.addWidget(self.crop_top_input)

        layout.addWidget(QLabel("Right coordinate (X):"))
        self.crop_right_input = QSpinBox()
        self.crop_right_input.setMaximum(9999)
        self.crop_right_input.setValue(100)
        layout.addWidget(self.crop_right_input)

        layout.addWidget(QLabel("Bottom coordinate (Y):"))
        self.crop_bottom_input = QSpinBox()
        self.crop_bottom_input.setMaximum(9999)
        self.crop_bottom_input.setValue(100)
        layout.addWidget(self.crop_bottom_input)

        apply_button = QPushButton("Apply Manual Crop")
        apply_button.clicked.connect(self.apply_crop)
        layout.addWidget(apply_button)
        return widget

    def create_flip_rotate_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        btn_flip_h = QPushButton("Flip Horizontal")
        btn_flip_h.clicked.connect(self.apply_flip_horizontal)
        layout.addWidget(btn_flip_h)

        btn_flip_v = QPushButton("Flip Vertical")
        btn_flip_v.clicked.connect(self.apply_flip_vertical)
        layout.addWidget(btn_flip_v)

        btn_rot_90_cw = QPushButton("Rotate 90° Clockwise")
        btn_rot_90_cw.clicked.connect(self.apply_rotate_cw)
        layout.addWidget(btn_rot_90_cw)

        btn_rot_90_ccw = QPushButton("Rotate 90° Counter-Clockwise")
        btn_rot_90_ccw.clicked.connect(self.apply_rotate_ccw)
        layout.addWidget(btn_rot_90_ccw)
        return widget

    def create_filters_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Select a filter to apply:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Grayscale",
            "Blur",
            "Sharpen",
            "Contour",
            "Emboss"
        ])
        layout.addWidget(self.filter_combo)

        apply_button = QPushButton("Apply Filter")
        apply_button.clicked.connect(self.apply_filter)
        layout.addWidget(apply_button)
        return widget

    def create_text_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Text to add:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Your watermark text...")
        layout.addWidget(self.text_input)

        layout.addWidget(QLabel("Font:"))
        self.font_combo = QComboBox()
        # These are common fonts. We will try to find them on the system.
        self.font_combo.addItems([
            "Arial", 
            "Times New Roman", 
            "Courier New", 
            "Verdana", 
            "Comic Sans MS"
        ])
        layout.addWidget(self.font_combo)

        layout.addWidget(QLabel("Font Size:"))
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 200)
        self.font_size_input.setValue(36)
        layout.addWidget(self.font_size_input)

        layout.addWidget(QLabel("Position:"))
        self.text_position_combo = QComboBox()
        self.text_position_combo.addItems([
            "Top Left", "Top Center", "Top Right",
            "Center",
            "Bottom Left", "Bottom Center", "Bottom Right"
        ])
        self.text_position_combo.setCurrentText("Bottom Right")
        layout.addWidget(self.text_position_combo)

        self.text_color_button = QPushButton("Choose Text Color")
        self.text_color_button.clicked.connect(self.choose_text_color)
        layout.addWidget(self.text_color_button)

        apply_button = QPushButton("Apply Text")
        apply_button.clicked.connect(self.apply_text)
        layout.addWidget(apply_button)
        return widget

    def create_logo_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        load_logo_button = QPushButton("Load Logo Image...")
        load_logo_button.clicked.connect(self.load_logo)
        layout.addWidget(load_logo_button)
        
        self.logo_path_label = QLabel("No logo loaded.")
        layout.addWidget(self.logo_path_label)

        layout.addWidget(QLabel("Logo Position:"))
        self.logo_position_combo = QComboBox()
        self.logo_position_combo.addItems([
            "Top Left", "Top Right",
            "Center",
            "Bottom Left", "Bottom Right"
        ])
        self.logo_position_combo.setCurrentText("Bottom Right")
        layout.addWidget(self.logo_position_combo)
        
        layout.addWidget(QLabel("Logo Size (as % of main image):"))
        self.logo_scale_input = QSpinBox()
        self.logo_scale_input.setRange(1, 100)
        self.logo_scale_input.setValue(20) # Default to 20%
        layout.addWidget(self.logo_scale_input)

        apply_button = QPushButton("Apply Logo")
        apply_button.clicked.connect(self.apply_logo)
        layout.addWidget(apply_button)
        return widget

    def create_border_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        
        layout.addWidget(QLabel("Border Thickness (pixels):"))
        self.border_size_input = QSpinBox()
        self.border_size_input.setRange(1, 200)
        self.border_size_input.setValue(10)
        layout.addWidget(self.border_size_input)
        
        self.border_color_button = QPushButton("Choose Border Color")
        self.border_color_button.clicked.connect(self.choose_border_color)
        layout.addWidget(self.border_color_button)
        
        apply_button = QPushButton("Apply Border")
        apply_button.clicked.connect(self.apply_border)
        layout.addWidget(apply_button)
        return widget

    def create_background_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        # --- Group 1: Remove Background ---
        remove_bg_group = QGroupBox("Remove Background")
        remove_bg_layout = QVBoxLayout(remove_bg_group)

        # A LIL STAR WHEN U FINISH READING THIS LINE ⭐ 
        
        remove_bg_label = QLabel("This will make the background transparent (saves as PNG).")
        remove_bg_label.setWordWrap(True)
        remove_bg_layout.addWidget(remove_bg_label)
        
        remove_bg_button = QPushButton("Remove Background")
        remove_bg_button.clicked.connect(self.apply_remove_background)
        remove_bg_layout.addWidget(remove_bg_button)
        layout.addWidget(remove_bg_group)

        # --- Group 2: Replace Background ---
        replace_bg_group = QGroupBox("Replace Background with Color")
        replace_bg_layout = QVBoxLayout(replace_bg_group)

        replace_bg_label = QLabel("This will remove the background AND add a solid color.")
        replace_bg_label.setWordWrap(True)
        replace_bg_layout.addWidget(replace_bg_label)

        self.bg_color_button = QPushButton("Choose Background Color")
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        replace_bg_layout.addWidget(self.bg_color_button)
        
        apply_color_bg_button = QPushButton("Apply Color Background")
        apply_color_bg_button.clicked.connect(self.apply_color_background)
        replace_bg_layout.addWidget(apply_color_bg_button)
        layout.addWidget(replace_bg_group)
        
        return widget

    def create_enhance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        # We use sliders for this. 10 = 1.0 (no change)
        layout.addWidget(QLabel("Brightness (0.1 to 2.0):"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(1, 20) # We'll divide by 10
        self.brightness_slider.setValue(10)
        layout.addWidget(self.brightness_slider)

        layout.addWidget(QLabel("Contrast (0.1 to 2.0):"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(1, 20) # We'll divide by 10
        self.contrast_slider.setValue(10)
        layout.addWidget(self.contrast_slider)
        
        layout.addWidget(QLabel("Sharpness (0.1 to 2.0):"))
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setRange(1, 20) # We'll divide by 10
        self.sharpness_slider.setValue(10)
        layout.addWidget(self.sharpness_slider)
        
        apply_button = QPushButton("Apply Enhancements")
        apply_button.clicked.connect(self.apply_enhancements)
        layout.addWidget(apply_button)
        return widget

    # --- 5. "APPLY" FUNCTIONS (SLOTS) ---
    # These functions are connected to the "Apply" buttons in each tab.
    # They perform the actual image processing.

    def apply_resize(self):
        if not self._check_image_loaded(): return
        try:
            # Get values from the input boxes
            width = int(self.resize_width_input.text())
            height = int(self.resize_height_input.text())

            if width <= 0 or height <= 0:
                self.show_error_message("Width and height must be positive numbers.")
                return

            # Apply the resize
            self.current_image = self.current_image.resize((width, height), Image.LANCZOS)
            self.update_preview()
            self.show_success_message("Image resized.")

        except ValueError:
            self.show_error_message("Please enter valid numbers for width and height.")
        except Exception as e:
            self.show_error_message(f"Could not resize: {e}")

    def apply_crop(self):
        if not self._check_image_loaded(): return
        try:
            # Get values from the input boxes
            left = self.crop_left_input.value()
            top = self.crop_top_input.value()
            right = self.crop_right_input.value()
            bottom = self.crop_bottom_input.value()

            # Pillow crop box is (left, top, right, bottom)
            box = (left, top, right, bottom)
            
            self.current_image = self.current_image.crop(box)
            self.update_preview()
            self.show_success_message("Image cropped.")
            
        except Exception as e:
            self.show_error_message(f"Could not crop: {e}")

    def apply_flip_horizontal(self):
        if not self._check_image_loaded(): return
        self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.update_preview()

    def apply_flip_vertical(self):
        if not self._check_image_loaded(): return
        self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.update_preview()

    def apply_rotate_cw(self):
        if not self._check_image_loaded(): return
        # Pillow's rotate is counter-clockwise, so -90 is clockwise.
        # expand=True makes sure the image isn't cut off.
        self.current_image = self.current_image.rotate(-90, expand=True)
        self.update_preview()

    def apply_rotate_ccw(self):
        if not self._check_image_loaded(): return
        self.current_image = self.current_image.rotate(90, expand=True)
        self.update_preview()

    def apply_filter(self):
        if not self._check_image_loaded(): return
        
        filter_name = self.filter_combo.currentText()
        
        if filter_name == "Grayscale":
            # .convert("L") converts to Grayscale
            # We .convert("RGBA") back so it fits our standard format
            self.current_image = self.current_image.convert("L").convert("RGBA")
        elif filter_name == "Blur":
            self.current_image = self.current_image.filter(ImageFilter.BLUR)
        elif filter_name == "Sharpen":
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
        elif filter_name == "Contour":
            self.current_image = self.current_image.filter(ImageFilter.CONTOUR)
        elif filter_name == "Emboss":
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
            
        self.update_preview()
        self.show_success_message(f"'{filter_name}' filter applied.")

    def apply_text(self):
        if not self._check_image_loaded(): return

        try:
            text = self.text_input.text()
            if not text:
                self.show_error_message("Please enter text to add.")
                return

            # --- 1. Load Font ---
            font_name = self.font_combo.currentText()
            font_size = self.font_size_input.value()
            
            # Map simple name to a real font file.
            # This is a bit advanced, but it's the right way to do it.
            # We just guess the file extension.
            font_file = f"{font_name.lower().replace(' ', '')}.ttf"
            
            try:
                # Try to load the system font
                font = ImageFont.truetype(font_file, font_size)
            except IOError:
                # If font isn't found, use a simple default font
                self.show_error_message(f"Font '{font_name}' not found. Using default font.")
                font = ImageFont.load_default()

            # --- 2. Prepare to Draw ---
            # We draw on the self.current_image
            draw = ImageDraw.Draw(self.current_image)
            
            # Get image and text size
            img_width, img_height = self.current_image.size
            # getbbox is the modern way to get text size
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # --- 3. Calculate Position ---
            position_name = self.text_position_combo.currentText()
            margin = 10  # 10 pixel margin from edge
            
            if position_name == "Top Left":
                pos = (margin, margin)
            elif position_name == "Top Center":
                pos = ((img_width - text_width) // 2, margin)
            elif position_name == "Top Right":
                pos = (img_width - text_width - margin, margin)
            elif position_name == "Center":
                pos = ((img_width - text_width) // 2, (img_height - text_height) // 2)
            elif position_name == "Bottom Left":
                pos = (margin, img_height - text_height - margin)
            elif position_name == "Bottom Center":
                pos = ((img_width - text_width) // 2, img_height - text_height - margin)
            elif position_name == "Bottom Right":
                pos = (img_width - text_width - margin, img_height - text_height - margin)

            # --- 4. Draw the Text ---
            draw.text(pos, text, font=font, fill=self.current_text_color)
            
            self.update_preview()
            self.show_success_message("Text watermark added.")

        except Exception as e:
            self.show_error_message(f"Could not add text: {e}")

    def apply_logo(self):
        if not self._check_image_loaded(): return
        if not self.logo_path:
            self.show_error_message("Please load a logo image first.")
            return

        try:
            # --- 1. Load and Resize Logo ---
            logo = Image.open(self.logo_path).convert("RGBA")
            scale_percent = self.logo_scale_input.value()
            
            # Calculate logo size based on main image width
            base_width = int(self.current_image.width * (scale_percent / 100))
            w_percent = (base_width / float(logo.width))
            h_size = int((float(logo.height) * float(w_percent)))
            
            logo = logo.resize((base_width, h_size), Image.LANCZOS)
            
            logo_width, logo_height = logo.size
            img_width, img_height = self.current_image.size
            
            # --- 2. Calculate Position ---
            position_name = self.logo_position_combo.currentText()
            margin = 10
            
            if position_name == "Top Left":
                pos = (margin, margin)
            elif position_name == "Top Right":
                pos = (img_width - logo_width - margin, margin)
            elif position_name == "Center":
                pos = ((img_width - logo_width) // 2, (img_height - logo_height) // 2)
            elif position_name == "Bottom Left":
                pos = (margin, img_height - logo_height - margin)
            elif position_name == "Bottom Right":
                pos = (img_width - logo_width - margin, img_height - logo_height - margin)
            
            # --- 3. Paste the Logo ---
            # We paste the logo onto the current image.
            # The 'logo' itself is used as the 'mask' - this
            # respects the logo's transparency.
            self.current_image.paste(logo, pos, mask=logo)
            
            self.update_preview()
            self.show_success_message("Logo watermark added.")

        except Exception as e:
            self.show_error_message(f"Could not add logo: {e}")

    def apply_border(self):
        if not self._check_image_loaded(): return
        
        try:
            border_size = self.border_size_input.value()
            # ImageOps.expand is the easiest way to add a border
            self.current_image = ImageOps.expand(
                self.current_image, 
                border=border_size, 
                fill=self.current_border_color
            )
            self.update_preview()
            self.show_success_message("Border added.")
            
        except Exception as e:
            self.show_error_message(f"Could not add border: {e}")
            
    def apply_remove_background(self):
        if not self._check_image_loaded(): return
        
        try:
            # Use the 'remove' function from the rembg library
            # This returns a new PIL Image with a transparent background
            self.current_image = remove(self.current_image)
            self.update_preview()
            self.show_success_message("Background removed.")
            
        except Exception as e:
            self.show_error_message(f"Could not remove background: {e}")
    
    def apply_color_background(self):
        if not self._check_image_loaded(): return
        
        try:
            # --- 1. Remove the original background ---
            # We get the image with transparency first
            foreground_image = remove(self.current_image)
            
            # --- 2. Create a new solid color background ---
            # It must be the same size as the original
            bg_width, bg_height = self.current_image.size
            new_background = Image.new("RGBA", (bg_width, bg_height), self.current_bg_color)
            
            # --- 3. Paste the foreground onto the new background ---
            # We use the foreground_image's alpha channel as the mask
            new_background.paste(foreground_image, (0, 0), mask=foreground_image)
            
            self.current_image = new_background
            self.update_preview()
            self.show_success_message("Background replaced with color.")
            
        except Exception as e:
            self.show_error_message(f"Could not replace background: {e}")
            
    def apply_enhancements(self):
        if not self._check_image_loaded(): return
        
        try:
            # We get the slider values and divide by 10.0
            # So a slider value of '10' becomes 1.0 (no change)
            brightness = self.brightness_slider.value() / 10.0
            contrast = self.contrast_slider.value() / 10.0
            sharpness = self.sharpness_slider.value() / 10.0
            
            # We apply the effects one by one
            
            enhancer = ImageEnhance.Brightness(self.current_image)
            self.current_image = enhancer.enhance(brightness)
            
            enhancer = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer.enhance(contrast)
            
            enhancer = ImageEnhance.Sharpness(self.current_image)
            self.current_image = enhancer.enhance(sharpness)
            
            self.update_preview()
            self.show_success_message("Enhancements applied.")
            
        except Exception as e:
            self.show_error_message(f"Could not apply enhancements: {e}")

    # --- 6. HELPER FUNCTIONS (for colors, logos, errors) ---

    def _check_image_loaded(self):
        """A private helper function to check if an image is loaded."""
        if self.current_image is None:
            self.show_error_message("You must load an image first!")
            return False
        return True

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # We store the color as an (R, G, B) tuple
            self.current_text_color = (color.red(), color.green(), color.blue())
            # Update the button to show the new color
            self.text_color_button.setStyleSheet(f"background-color: {color.name()};")

    def choose_border_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_border_color = (color.red(), color.green(), color.blue())
            self.border_color_button.setStyleSheet(f"background-color: {color.name()};")

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # We store as (R, G, B, A) with full opacity (255)
            self.current_bg_color = (color.red(), color.green(), color.blue(), 255)
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()};")
            
    def load_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Logo Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.logo_path = file_path
            # Show the user which file they selected
            self.logo_path_label.setText(os.path.basename(file_path))

    def show_error_message(self, message):
        """Shows a popup error message."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

    def show_success_message(self, message):
        """Shows a popup success message."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Success")
        msg_box.setText(message)
        msg_box.exec()

    def get_dark_theme_stylesheet(self):
        """
        Returns a string containing the QSS (like CSS) for a dark theme.
        """
        return """
            QWidget {
                background-color: #2E3440; /* Dark blue/grey */
                color: #ECEFF4; /* Light grey/white text */
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QMainWindow {
                background-color: #2E3440;
            }
            QLabel {
                color: #D8DEE9;
            }
            QLineEdit, QSpinBox {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 4px;
                padding: 5px;
                color: #ECEFF4;
            }
            QPushButton {
                background-color: #5E81AC; /* A nice blue */
                color: #ECEFF4;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #81A1C1; /* Lighter blue on hover */
            }
            QPushButton:pressed {
                background-color: #4C566A; /* Darker blue when pressed */
            }
            QTabWidget::pane {
                border: 1px solid #4C566A;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #3B4252;
                color: #D8DEE9;
                padding: 8px 15px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #5E81AC;
                color: #ECEFF4;
            }
            QTabBar::tab:!selected {
                background: #2E3440;
                color: #A3BE8C;
            }
            QComboBox {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QSlider::groove:horizontal {
                border: 1px solid #4C566A;
                height: 8px;
                background: #3B4252;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #81A1C1;
                border: 1px solid #5E81AC;
                width: 16px;
                margin: -4px 0; 
                border-radius: 8px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #4C566A;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2E3440;
                color: #88C0D0; /* Light cyan title */
            }
        """

    def resizeEvent(self, event):
        """
        This function automatically runs whenever the window is resized.
        We use it to update the image preview to fit the new window size.
        """
        self.update_preview()
        # Pass the event to the parent class
        super().resizeEvent(event)


# --- 7. RUN THE APPLICATION ---
# This is the standard "main" block for a Python script.
# It only runs if you execute this file directly.

if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Create our main window
    window = PhotoHelperPro()
    
    # Show the window
    window.show()
    
    # Start the application's event loop
    sys.exit(app.exec())