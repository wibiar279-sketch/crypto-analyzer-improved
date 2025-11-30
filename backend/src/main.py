"""
Main Flask application with all configurations.
"""
import os
import redis
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from .config import get_config
from .models import db
from .routes.api import api_bp
from .utils import CacheManager, setup_logging, log_request, log_response, log_error


def create_app(config_name=None):
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    config.init_app(app)
    
    # Initialize logging
    setup_logging(app)
    app.logger.info("Starting Crypto Analyzer API")
    
    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created/verified successfully ✓")
        except Exception as e:
            app.logger.warning(f"Database table creation skipped: {e}")
    
    # Initialize Redis
    try:
        redis_client = redis.from_url(
            app.config['REDIS_URL'],
            decode_responses=True
        )
        redis_client.ping()
        app.logger.info("Redis connected successfully ✓")
        
        # Initialize cache manager
        cache = CacheManager(redis_client)
        app.cache = cache
        
    except Exception as e:
        app.logger.error(f"Redis connection failed: {e}")
        app.cache = None
    
    # Configure CORS
    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:5173'])
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    app.logger.info(f"CORS enabled for: {cors_origins} ✓")
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL')
    )
    app.logger.info("Rate limiting enabled ✓")
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Crypto Analyzer API',
            'version': '2.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/v1/health',
                'pairs': '/api/v1/pairs',
                'tickers': '/api/v1/tickers',
                'analyze': '/api/v1/analyze/<pair_id>'
            }
        })
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.logger.info("API blueprint registered ✓")
    
    # Request/response logging
    app.before_request(log_request)
    app.after_request(log_response)
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        app.logger.warning(f"404 Not Found: {e}")
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': str(e)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"500 Internal Server Error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        log_error(e)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred'
        }), 500
    
    app.logger.info("Application initialization complete ✓")
    
    return app


# Create app instance for Gunicorn
app = create_app()


if __name__ == '__main__':
    # Development server
    app = create_app('development')
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
