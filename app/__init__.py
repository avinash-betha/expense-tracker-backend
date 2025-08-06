from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    # Load config
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)

    # Register routes
    from app.routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app
