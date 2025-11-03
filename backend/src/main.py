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
    
    # Initialize Redis
    try:
        redis_client = redis.from_url(
            app.config['REDIS_URL'],
            decode_responses=True
        )
        redis_client.ping()
        app.logger.info("Redis connected successfully")
        
        # Initialize cache manager
        cache_manager = CacheManager(redis_client)
        app.extensions['cache_manager'] = cache_manager
        
    except Exception as e:
        app.logger.error(f"Redis connection failed: {e}")
        app.logger.warning("Running without cache")
        app.extensions['cache_manager'] = None
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    app.logger.info(f"CORS enabled for: {app.config['CORS_ORIGINS']}")
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=app.config.get('RATELIMIT_DEFAULT', '200 per day;50 per hour').split(';'),
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL')
    )
    app.logger.info("Rate limiting enabled")
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.logger.info("API blueprint registered")
    
    # Request/response logging
    app.before_request(log_request)
    app.after_request(log_response)
    
    # Error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        log_error(e)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Crypto Analyzer API',
            'version': '2.0.0',
            'status': 'running',
            'documentation': '/api/v1/docs'
        })
    
    # API documentation endpoint
    @app.route('/api/v1/docs')
    def api_docs():
        return jsonify({
            'endpoints': {
                'health': {
                    'path': '/api/v1/health',
                    'method': 'GET',
                    'description': 'Health check'
                },
                'pairs': {
                    'path': '/api/v1/pairs',
                    'method': 'GET',
                    'description': 'Get all trading pairs'
                },
                'tickers': {
                    'path': '/api/v1/tickers',
                    'method': 'GET',
                    'description': 'Get all tickers'
                },
                'ticker': {
                    'path': '/api/v1/ticker/<pair_id>',
                    'method': 'GET',
                    'description': 'Get ticker for specific pair'
                },
                'depth': {
                    'path': '/api/v1/depth/<pair_id>',
                    'method': 'GET',
                    'description': 'Get order book depth'
                },
                'analysis': {
                    'path': '/api/v1/analysis/<pair_id>',
                    'method': 'GET',
                    'description': 'Get complete analysis with recommendation'
                },
                'technical': {
                    'path': '/api/v1/technical/<pair_id>',
                    'method': 'GET',
                    'description': 'Get technical analysis only'
                },
                'bandarmology': {
                    'path': '/api/v1/bandarmology/<pair_id>',
                    'method': 'GET',
                    'description': 'Get bandarmology analysis only'
                },
                'history': {
                    'path': '/api/v1/history/<pair_id>',
                    'method': 'GET',
                    'description': 'Get historical analysis data',
                    'params': {'limit': 'Number of records (default 50, max 1000)'}
                }
            }
        })
    
    # Optional: Sentry integration
    if app.config.get('SENTRY_DSN'):
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                integrations=[FlaskIntegration()],
                environment=app.config['FLASK_ENV']
            )
            app.logger.info("Sentry integration enabled")
        except ImportError:
            app.logger.warning("Sentry SDK not installed")
    
    app.logger.info("Application initialization complete")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
