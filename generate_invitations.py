import fitz  # PyMuPDF
import os
import sys
import json
from PyQt5.QtGui import QGuiApplication, QImage, QPainter, QFont, QColor, QFontDatabase
from PyQt5.QtCore import Qt

# Initialize a background application for the native text engine
app = QGuiApplication(sys.argv)

def create_perfect_gujarati_image(text, font_family, output_image_path, font_size=40):
    """Generates a transparent PNG with perfectly shaped Gujarati text."""
    img = QImage(1200, 150, QImage.Format_ARGB32)
    img.fill(Qt.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    # Set text color to Red (R=255, G=0, B=0)
    painter.setPen(QColor(255, 0, 0))
    
    font = QFont(font_family, font_size) 
    painter.setFont(font)
    
    painter.drawText(img.rect(), Qt.AlignLeft | Qt.AlignVCenter, text)
    painter.end()

    img.save(output_image_path)

def generate_invitations():
    # ---------------------------------------------------------
    # LOAD CONFIGURATION FROM JSON FILE
    # ---------------------------------------------------------
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found!")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    guest_lists = config.get("guest_lists", {})
    pdf_settings = config.get("pdf_settings", {})

    # ---------------------------------------------------------
    # LOAD THE FONT
    # ---------------------------------------------------------
    font_path = "NotoSansGujarati-Regular.ttf"
    if not os.path.exists(font_path):
        print(f"Error: Please ensure '{font_path}' is in this folder!")
        return

    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print(f"Error: Failed to load font from {font_path}")
        return
        
    custom_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

    temp_img_path = "temp_name.png"

    # ---------------------------------------------------------
    # PROCESS BATCHES BY TEMPLATE
    # ---------------------------------------------------------
    for pdf_file, names_list in guest_lists.items():
        print(f"\n--- Starting Batch for Template: {pdf_file} ---")
        
        if pdf_file not in pdf_settings:
            print(f"Error: Settings for '{pdf_file}' not found in pdf_settings. Skipping this list.")
            continue

        if not os.path.exists(pdf_file):
            print(f"Error: Template file '{pdf_file}' not found on disk. Skipping this list.")
            continue

        settings = pdf_settings[pdf_file]

        for name in names_list:
            create_perfect_gujarati_image(name, custom_font_family, temp_img_path)
            
            doc = fitz.open(pdf_file)
            page = doc[0] 
            
            # --- 1. Insert the Name Image ---
            x0 = settings["x"]
            y0 = settings["y"]
            x1 = x0 + settings["box_width"]
            y1 = y0 + settings["box_height"]
            
            rect = fitz.Rect(x0, y0, x1, y1)
            page.insert_image(rect, filename=temp_img_path)
            
            # --- 2. Draw TWO INDEPENDENT Strikethrough Lines ---
            
            # Line 1
            p1_line1 = fitz.Point(settings["line1_x"], settings["line1_y"])
            p2_line1 = fitz.Point(settings["line1_x"] + settings.get("line1_length", 30), settings["line1_y"])
            page.draw_line(p1_line1, p2_line1, color=(1, 0, 0), width=1.5)

            # Line 2
            p1_line2 = fitz.Point(settings["line2_x"], settings["line2_y"])
            p2_line2 = fitz.Point(settings["line2_x"] + settings.get("line2_length", 30), settings["line2_y"])
            page.draw_line(p1_line2, p2_line2, color=(1, 0, 0), width=1.5)
            
            # Save the final PDF safely
            safe_name = name.replace(" ", "_")
            output_filename = f"{pdf_file.replace('.pdf', '')}_{safe_name}.pdf"
            
            doc.save(output_filename)
            print(f"Created: {output_filename}")
            
            doc.close()

    # Clean up the temporary PNG file
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)

if __name__ == "__main__":
    generate_invitations()
