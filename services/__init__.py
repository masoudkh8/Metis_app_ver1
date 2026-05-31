# Services package initialization
# Note: Import permissions first (no Flask dependencies)
from services.permissions import Permission, ServiceCategory, DEFAULT_ROLE_PERMISSIONS

# Lazy load access_control to avoid import errors when Flask is not initialized
__all__ = [
    'Permission',
    'ServiceCategory', 
    'DEFAULT_ROLE_PERMISSIONS',
    # Access control functions are available when Flask app is running
    # 'role_required',
    # 'permission_required', 
    # 'get_user_permissions',
    # 'has_permission',
    # 'service_module_enabled'
]

def get_access_control_functions():
    """Lazy loader for access control functions (requires Flask context)"""
    from services.access_control import (
        role_required,
        permission_required,
        get_user_permissions,
        has_permission,
        service_module_enabled
    )
    return {
        'role_required': role_required,
        'permission_required': permission_required,
        'get_user_permissions': get_user_permissions,
        'has_permission': has_permission,
        'service_module_enabled': service_module_enabled
    }
