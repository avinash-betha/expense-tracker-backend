import pandas as pd
from app.models import Expense
from app import db
import os
from datetime import datetime

def export_to_csv():
    # Query all expenses
    expenses = Expense.query.order_by(Expense.date.desc()).all()

    # Convert to list of dicts
    data = [e.to_dict() for e in expenses]

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Export path
    export_folder = os.path.join(os.getcwd(), "exports")
    os.makedirs(export_folder, exist_ok=True)

    file_name = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(export_folder, file_name)

    # Export to CSV
    df.to_csv(file_path, index=False)

    return file_path
