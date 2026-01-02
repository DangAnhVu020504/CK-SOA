"""
Auth Service - Xác thực và phân quyền
Port: 5100
Database: MySQL (auth_db)
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)
sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, '.env'))

from flask import Flask
from flask_cors import CORS

from config import Config, SERVICE_NAME, SERVICE_PORT, SERVICE_TAGS
from models import db
from routes import auth_bp
from utils import init_default_roles, init_default_admin


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_roles()
        init_default_admin()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, SERVICE_NAME, SERVICE_PORT, SERVICE_TAGS)
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  {SERVICE_NAME} running on port {SERVICE_PORT}")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=SERVICE_PORT, host='0.0.0.0')
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Auth Service running on port 5100")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5100, host='0.0.0.0')
