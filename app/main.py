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
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    if isinstance(cors_origins, str):
        cors_origins = [origin.strip() for origin in cors_origins.split(',')]
    
    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Hospital-ID",
            "X-User-ID",
            "X-User-Name"
        ],
        expose_headers=["Content-Type", "Authorization"]
    )
    
    # Initialize rate limiter with proper storage
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '1000 per hour')],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    )
    limiter.init_app(app)
    
    # Initialize Firebase
    firebase_client = FirebaseClient()
    app.firebase_client = firebase_client
    
    # Initialize Firebase Storage (lazy initialization)
    app.storage_client = None
    
    # Register blueprints
    app.register_blueprint(v1_bp, url_prefix=AppConfig.API_PREFIX)
    
    # Configure logging
    configure_logging(app)
    
    # Add CORS error handler for 404s
    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 errors with proper CORS headers"""
        from flask import jsonify
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404
        }), 404
    
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
            
            # Test Firebase connection if available
            firebase_health = 'unknown'
            if hasattr(app, 'firebase_client') and app.firebase_client:
                try:
                    firebase_health = app.firebase_client.health_check()
                except Exception as e:
                    firebase_health = {'status': 'unhealthy', 'error': str(e)}
            
            return {
                'status': 'healthy',
                'version': '1.0.0',
                'environment': os.environ.get('FLASK_ENV', 'development'),
                'firebase': firebase_status,
                'firebase_health': firebase_health,
                'environment_variables': {
                    'FIREBASE_PROJECT_ID': bool(os.environ.get('FIREBASE_PROJECT_ID')),
                    'FIREBASE_STORAGE_BUCKET': bool(os.environ.get('FIREBASE_STORAGE_BUCKET')),
                    'FIREBASE_SERVICE_ACCOUNT_KEY': bool(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
                },
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
    # Only run in debug mode if explicitly set
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
