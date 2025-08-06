from app import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    store = db.Column(db.String(120))
    total_amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(255))
    category = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.utcnow)
    image_path = db.Column(db.String(255))  # optional: local file path or URL

    def to_dict(self):
        return {
            "id": self.id,
            "store": self.store,
            "total_amount": self.total_amount,
            "purpose": self.purpose,
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d"),
            "image_path": self.image_path
        }
