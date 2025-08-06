from app.models import Expense
from collections import defaultdict
from datetime import datetime

def get_chart_data(mode='monthly'):
    data = defaultdict(float)

    expenses = Expense.query.all()

    for expense in expenses:
        if mode == 'monthly':
            # Group by year-month (e.g. "2025-08")
            key = expense.date.strftime("%Y-%m")
        elif mode == 'category':
            key = expense.category or "Uncategorized"
        else:
            continue

        data[key] += expense.total_amount

    # Sort and format result
    chart_data = [{"label": k, "total": round(v, 2)} for k, v in sorted(data.items())]
    return chart_data
