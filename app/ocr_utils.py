import pytesseract
from PIL import Image
import re
from datetime import datetime

# If Tesseract is not in PATH, specify the full path below
# Update this path only if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 🔹 Extract raw OCR text from image
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print("OCR Error:", e)
        return ""

# 🔹 Parse fields like total, store name, and date from the text
def parse_receipt_data(text):
    total = None
    store = None
    date = None

    lines = text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # Try to find the total amount
    for line in lines:
        if 'total' in line.lower() or 'amount' in line.lower():
            match = re.search(r'(\d+\.\d{2})', line)
            if match:
                total = float(match.group(1))
                break
    if not total:
        # Last resort: any float value in the receipt
        for line in lines:
            match = re.search(r'(\d+\.\d{2})', line)
            if match:
                total = float(match.group(1))
                break

    # Assume store is first line (if no other pattern found)
    store = lines[0] if lines else "Unknown Store"

    # Try to extract date
    for line in lines:
        # Format: MM/DD/YYYY or DD-MM-YYYY
        date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', line)
        if date_match:
            try:
                date = datetime.strptime(date_match.group(1), "%m/%d/%Y").date()
                break
            except:
                try:
                    date = datetime.strptime(date_match.group(1), "%d-%m-%Y").date()
                    break
                except:
                    continue
        # Format: YYYY-MM-DD
        iso_match = re.search(r'(\d{4}[/-]\d{2}[/-]\d{2})', line)
        if iso_match:
            try:
                date = datetime.strptime(iso_match.group(1), "%Y-%m-%d").date()
                break
            except:
                continue

    return {
        "total": total if total else 0.0,
        "store": store,
        "date": date if date else datetime.today().date()
    }
