from flask import Blueprint

def register_routes(app):
    from .auth_routes import auth_bp
    from .blood_routes import blood_bp
    from .request_routes import request_bp
    from .donor_routes import donor_bp
    from .hospital_routes import hospital_bp
    from .inventory_routes import inventory_bp
    from .donation_routes import donation_bp
    from .notification_routes import notification_bp
    from .admin_routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(blood_bp, url_prefix='/api/v1/blood')
    app.register_blueprint(request_bp, url_prefix='/api/v1/requests')
    app.register_blueprint(donor_bp, url_prefix='/api/v1/donors')
    app.register_blueprint(hospital_bp, url_prefix='/api/v1/hospitals')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(donation_bp, url_prefix='/api/v1/donations')
    app.register_blueprint(notification_bp, url_prefix='/api/v1/notifications')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
