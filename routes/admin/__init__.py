from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def init_admin_blueprints():
    """Initialize and register all admin-related blueprints"""
    from routes.admin.permissions import admin_perms_bp
    admin_bp.register_blueprint(admin_perms_bp)
    
    # Add more admin blueprints here as needed
    # from routes.admin.users import users_mgmt_bp
    # admin_bp.register_blueprint(users_mgmt_bp)
    
    return admin_bp