"""
Employee Service - Main Application
SOA Mini Supermarket Management System
Port: 5002
"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import config
from models import db

def create_app(config_name='development'):
    """Application Factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from routes import employee_bp
    app.register_blueprint(employee_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'service': 'Employee Service',
            'status': 'healthy',
            'port': 5002
        }), 200
    
    # Root endpoint - Serve HTML UI
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')
    
    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        return jsonify({
            'service': 'Employee Service',
            'version': '1.0.0',
            'description': 'Quản lý nhân viên siêu thị mini'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    
    with app.app_context():
        db.create_all()
    
    print("=" * 50)
    print("Employee Service is running on http://localhost:5002")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
