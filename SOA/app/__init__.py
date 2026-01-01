# Flask Application Factory
from flask import Flask, render_template
from flask_cors import CORS

from app.config import config
from app.extensions import init_extensions, db


def create_app(config_name='default'):
    """Create and configure the Flask application"""
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints (routes)
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize default roles
        from app.services.role_service import RoleService
        RoleService.initialize_default_roles()
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'API đang hoạt động'}
    
    # Frontend route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
