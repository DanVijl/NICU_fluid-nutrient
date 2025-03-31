import logging
import os
import time
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g

def setup_logging(app):
    """
    Set up logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Ensure log directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up file handler for application logs
    file_handler = RotatingFileHandler(
        'logs/nicu_app.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    app.logger.info('NICU Fluid Management App startup')

def log_request_info():
    """Log information about each request."""
    app = Flask(__name__)
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        app.logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def after_request(response):
        diff = time.time() - g.start_time
        app.logger.debug(f"Response: {response.status_code} in {diff:.6f}s")
        return response

class HealthCheck:
    """Health check endpoints for monitoring."""
    
    @staticmethod
    def register(app):
        """Register health check endpoints with the Flask app."""
        
        @app.route('/health')
        def health_check():
            """Basic health check endpoint."""
            return {'status': 'ok'}
        
        @app.route('/health/db')
        def db_health_check():
            """Database health check endpoint."""
            from flask_sqlalchemy import SQLAlchemy
            db = SQLAlchemy(app)
            
            try:
                # Execute a simple query
                db.session.execute('SELECT 1')
                return {'status': 'ok', 'database': 'connected'}
            except Exception as e:
                app.logger.error(f"Database health check failed: {str(e)}")
                return {'status': 'error', 'database': 'disconnected', 'error': str(e)}, 500

class ErrorMonitoring:
    """Error monitoring and reporting."""
    
    @staticmethod
    def register(app):
        """Register error monitoring with the Flask app."""
        
        @app.errorhandler(404)
        def not_found_error(error):
            app.logger.info(f"404 error: {request.path}")
            return app.send_static_file('404.html'), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            app.logger.error(f"500 error: {str(error)}")
            return app.send_static_file('500.html'), 500
        
        # Optional: integrate with external error monitoring service
        if os.environ.get('SENTRY_DSN'):
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=os.environ.get('SENTRY_DSN'),
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0
            )
            app.logger.info("Sentry error monitoring enabled")

class PerformanceMonitoring:
    """Performance monitoring for the application."""
    
    @staticmethod
    def register(app):
        """Register performance monitoring with the Flask app."""
        
        @app.before_request
        def start_timer():
            g.start_time = time.time()
        
        @app.after_request
        def log_request_time(response):
            if hasattr(g, 'start_time'):
                elapsed = time.time() - g.start_time
                app.logger.info(f"Request {request.method} {request.path} took {elapsed:.6f}s")
                
                # Add timing header to response
                response.headers['X-Response-Time'] = f"{elapsed:.6f}s"
                
                # Log slow requests
                if elapsed > 1.0:  # Log requests taking more than 1 second
                    app.logger.warning(f"Slow request: {request.method} {request.path} took {elapsed:.6f}s")
            
            return response
        
        # Optional: integrate with external performance monitoring service
        if os.environ.get('NEW_RELIC_LICENSE_KEY'):
            try:
                import newrelic.agent
                newrelic.agent.initialize('newrelic.ini')
                app.logger.info("New Relic performance monitoring enabled")
            except ImportError:
                app.logger.warning("New Relic package not installed")

def setup_monitoring(app):
    """
    Set up all monitoring components for the application.
    
    Args:
        app: Flask application instance
    """
    # Set up logging
    setup_logging(app)
    
    # Register health checks
    HealthCheck.register(app)
    
    # Register error monitoring
    ErrorMonitoring.register(app)
    
    # Register performance monitoring
    PerformanceMonitoring.register(app)
    
    app.logger.info("Monitoring setup complete")
