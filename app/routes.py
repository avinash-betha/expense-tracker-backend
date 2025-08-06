from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app.models import Expense
from app.ocr_utils import extract_text_from_image, parse_receipt_data
from app.export_utils import export_to_csv
from app.chart_utils import get_chart_data
from app import db
from datetime import datetime
from app.config import Config
import os

api = Blueprint('api', __name__)

# ============================
# 1. Upload Receipt + Save
# ============================
@api.route('/upload', methods=['POST'])
def upload_receipt():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files['image']
    filename = secure_filename(image.filename)
    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    image.save(save_path)

    # OCR and parse
    text = extract_text_from_image(save_path)
    parsed = parse_receipt_data(text)

    # Extra fields from form
    purpose = request.form.get('purpose', 'General')
    category = request.form.get('category', 'Misc')

    expense = Expense(
        store=parsed.get('store'),
        total_amount=parsed.get('total'),
        purpose=purpose,
        category=category,
        date=parsed.get('date'),
        image_path=save_path
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({"message": "Expense saved", "data": expense.to_dict()})


# ============================
# 2. Get All Expenses
# ============================
@api.route('/expenses', methods=['GET'])
def get_expenses():
    sort_by = request.args.get('sort', 'date')  # optional ?sort=amount
    order = request.args.get('order', 'desc')   # optional ?order=asc

    query = Expense.query

    if sort_by == 'amount':
        query = query.order_by(Expense.total_amount.desc() if order == 'desc' else Expense.total_amount.asc())
    else:
        query = query.order_by(Expense.date.desc() if order == 'desc' else Expense.date.asc())

    expenses = query.all()
    return jsonify([e.to_dict() for e in expenses])


# ============================
# 3. Export to CSV
# ============================
@api.route('/export', methods=['GET'])
def export_csv():
    file_path = export_to_csv()
    return send_file(file_path, as_attachment=True)


# ============================
# 4. Get Chart Data
# ============================
@api.route('/chart', methods=['GET'])
def chart_data():
    mode = request.args.get('mode', 'monthly')  # or category
    data = get_chart_data(mode)
    return jsonify(data)
