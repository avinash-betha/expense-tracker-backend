from app import create_app, db
import os

app = create_app()

with app.app_context():
    print("Using DB:", os.getenv("DATABASE_URI"))  # ✅ add this line
    db.create_all()
    print("✅ Database tables created.")
