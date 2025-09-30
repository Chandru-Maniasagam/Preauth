"""
Main application entry point for RCM SaaS Application
"""

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from datetime import datetime

from app.config import AppConfig, FirebaseConfig, StorageConfig
from app.database.firebase_client import FirebaseClient
from app.storage.firebase_storage import FirebaseStorageClient
from app.api.v1.routes import v1_bp
from Preauthform import preauth_form_bp
from Preauthregistered_Notification import preauth_notification_bp
from preauthprocess import preauth_process_bp


def create_app(config_name: str = None) -> Flask:
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    
    # Set secret keys for sessions and JWT
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Flask-Session-Secret-Key-2025-RCM-SaaS-Application-Development-Environment-Change-In-Production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'JWT-Token-Secret-Key-2025-RCM-SaaS-Application-Development-Environment-Change-In-Production')
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    try:
        app.config.from_object(f'app.config.settings.{config_name.title()}Config')
    except ImportError:
        # Fallback to development config if specific config not found
        app.config.from_object('app.config.settings.DevelopmentConfig')
    
    # Initialize extensions
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '1000 per hour')]
    )
    limiter.init_app(app)
    
    # Initialize Firebase
    firebase_client = FirebaseClient()
    app.firebase_client = firebase_client
    
    # Initialize Firebase Storage (lazy initialization)
    app.storage_client = None
    
    # Register blueprints
    app.register_blueprint(v1_bp, url_prefix=AppConfig.API_PREFIX)
    app.register_blueprint(preauth_form_bp)
    app.register_blueprint(preauth_notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(preauth_process_bp, url_prefix='/preauth-process')
    
    # Configure logging
    configure_logging(app)
    
    # Root endpoint - API only, no frontend
    @app.route('/')
    def index():
        """API root endpoint - redirect to API documentation"""
        from flask import redirect
        return redirect('/api/v1/', code=302)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check if Firebase client is initialized
            firebase_status = 'healthy' if hasattr(app, 'firebase_client') else 'unhealthy'
            
            return {
                'status': 'healthy',
                'version': '1.0.0',
                'environment': os.environ.get('FLASK_ENV', 'development'),
                'firebase': firebase_status,
                'timestamp': str(datetime.now())
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': str(datetime.now())
            }, 500
    
    return app


def configure_logging(app: Flask) -> None:
    """Configure application logging"""
    
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('RCM SaaS Application startup')


# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
