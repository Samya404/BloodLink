import os
from flask import Flask, jsonify, send_from_directory
from config import Config, config_by_name
from extensions import db, jwt, cors, socketio, migrate
from utils.helpers import error_response

def create_app(config_class=None):
    frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
    
    if config_class is None:
        config_class = Config
    elif isinstance(config_class, str):
        config_class = config_by_name.get(config_class, Config)
        
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)

    # Configure JWT error handlers for consistent API error responses
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return error_response("UNAUTHORIZED", "Missing or invalid authorization header", 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return error_response("INVALID_TOKEN", "Signature verification failed", 401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response("TOKEN_EXPIRED", "The token has expired", 401)

    # Import models to ensure they are registered with SQLAlchemy
    from models import (
        User, DonorProfile, Hospital, BloodInventory, 
        BloodRequest, DonorMatch, Donation, Notification, 
        APISource, ExternalBloodRecord, AuditLog
    )

    # Register blueprints
    from routes.auth_routes import bp as auth_bp
    from routes.blood_routes import bp as blood_bp
    from routes.request_routes import bp as request_bp
    from routes.donor_routes import bp as donor_bp
    from routes.hospital_routes import bp as hospital_bp
    from routes.inventory_routes import bp as inventory_bp
    from routes.donation_routes import bp as donation_bp
    from routes.notification_routes import bp as notification_bp
    from routes.admin_routes import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(blood_bp, url_prefix='/api/v1/blood')
    app.register_blueprint(request_bp, url_prefix='/api/v1/requests')
    app.register_blueprint(donor_bp, url_prefix='/api/v1/donors')
    app.register_blueprint(hospital_bp, url_prefix='/api/v1/hospitals')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(donation_bp, url_prefix='/api/v1/donations')
    app.register_blueprint(notification_bp, url_prefix='/api/v1/notifications')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')

    # Ensure tables exist
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database auto-creation skipped or failed: {e}")

    # A simple health check
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}

    # Frontend serving routes
    @app.route('/')
    def serve_index():
        if os.path.exists(os.path.join(frontend_folder, 'index.html')):
            return send_from_directory(frontend_folder, 'index.html')
        return jsonify({"message": "BloodLink API is running. Frontend static directory not found."})

    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(frontend_folder, path)):
            return send_from_directory(frontend_folder, path)
        return error_response("NOT_FOUND", f"Resource {path} not found", 404)

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
