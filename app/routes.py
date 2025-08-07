from flask import Blueprint, request, jsonify, send_file
from flask import send_from_directory
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
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = request.files['image']
        if image.filename == '':
            return jsonify({"error": "Invalid image filename"}), 400

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        filename = secure_filename(image.filename)
        save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        image.save(save_path)

        text = extract_text_from_image(save_path)
        parsed = parse_receipt_data(text)

        purpose = request.form.get('purpose', 'General')
        category = request.form.get('category', 'Misc')

        expense = Expense(
            store=parsed.get('store'),
            total_amount=parsed.get('total'),
            purpose=purpose,
            category=category,
            date=parsed.get('date', datetime.utcnow().date()),
            image_path=save_path
        )

        db.session.add(expense)
        db.session.commit()

        return jsonify({"message": "Expense saved", "data": expense.to_dict()}), 201

    except Exception as e:
        print("🔥 Error in /upload:", str(e))
        return jsonify({"error": str(e)}), 500

# ============================
# 2. Get All Expenses
# ============================
@api.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        sort_by = request.args.get('sort', 'date')
        order = request.args.get('order', 'desc')

        query = Expense.query

        if sort_by == 'amount':
            query = query.order_by(Expense.total_amount.desc() if order == 'desc' else Expense.total_amount.asc())
        else:
            query = query.order_by(Expense.date.desc() if order == 'desc' else Expense.date.asc())

        expenses = query.all()
        return jsonify([e.to_dict() for e in expenses])

    except Exception as e:
        print("🔥 Error in /expenses:", str(e))
        return jsonify({"error": str(e)}), 500

# ============================
# 3. Export to CSV
# ============================
@api.route('/export', methods=['GET'])
def export_csv():
    try:
        file_path = export_to_csv()
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print("🔥 Error in /export:", str(e))
        return jsonify({"error": str(e)}), 500

# ============================
# 4. Get Chart Data (Monthly / Category)
# ============================
@api.route('/chart', methods=['GET'])
def chart_data():
    try:
        mode = request.args.get('mode', 'monthly').lower()

        if mode not in ['monthly', 'category']:
            return jsonify({"error": "Invalid mode. Use 'monthly' or 'category'."}), 400

        data = get_chart_data(mode)
        return jsonify(data)

    except Exception as e:
        print("🔥 Error in /chart:", str(e))
        return jsonify({"error": str(e)}), 500


# ============================
# 5. Download Receipt by Filename
# ============================
@api.route('/download/<filename>', methods=['GET'])
def download_receipt(filename):
    try:
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_from_directory(Config.UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print("🔥 Error in /download:", str(e))
        return jsonify({"error": str(e)}), 500