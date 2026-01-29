# Photo Helper Pro – v1.0

Photo Helper Pro is a beginner-friendly, all-in-one desktop photo utility application built with Python.  
The application provides a clean graphical interface for performing common image editing tasks such as resizing, cropping, filtering, background removal, and exporting images in multiple formats.

---

## Overview

Photo Helper Pro is designed for students, beginners, and anyone who wants a simple yet powerful desktop photo editor without relying on heavy professional software.  
The project focuses on clarity, usability, and clean Python architecture.

---

## Features

- Load and preview images
- Resize images using custom dimensions
- Crop images using manual coordinates
- Flip images horizontally or vertically
- Rotate images clockwise or counter-clockwise
- Apply filters:
  - Grayscale
  - Blur
  - Sharpen
  - Contour
  - Emboss
- Add text watermarks with:
  - Custom font
  - Size
  - Color
  - Position
- Add logo watermarks with scaling and positioning
- Add borders with configurable thickness and color
- Remove image background using AI (rembg)
- Replace background with a solid color
- Enhance image quality:
  - Brightness
  - Contrast
  - Sharpness
- Export images as:
  - PNG
  - JPEG
  - PDF

---

## Technologies Used

- Python 3
- PySide6 (GUI framework)
- Pillow (Image processing)
- rembg (AI background removal)

---

## Project Structure

```text
photo-helper-pro-v1/
├── src/
│   └── photo_helper_pro.py
├── assets/
│   └── screenshots/
├── requirements.txt
├── README.md
└── LICENSE
```

#Installation
## 1. Clone the repository
```bash
git clone https://github.com/abdessamad-erramy/photo-helper-pro-v1.git
cd photo-helper-pro-v1
```

2. Create a virtual environment (recommended)
```bash
python -m venv venv
```



## Activate the virtual environment:

## Windows
```bash
venv\Scripts\activate
```

## Linux / macOS
```bash
source venv/bin/activate
```
## 3. Install dependencies
  ```bash 
pip install -r requirements.txt
```

## Running the Application
```bash
python src/photo_helper_pro.py
```

The graphical interface will open, allowing you to load and edit images.

