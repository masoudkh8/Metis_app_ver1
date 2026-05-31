from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user
from models.user import Role, UserProfile
from services.permissions import Permission, DEFAULT_ROLE_PERMISSIONS

def role_required(*roles):
    """
    Decorator to restrict access based on user role.
    
    Usage:
        @users_bp.route('/admin/panel')
        @login_required
        @role_required(Role.ADMIN)
        def admin_panel():
            ...
            
        @users_bp.route('/logistics/assign')
        @login_required
        @role_required(Role.LOGISTICS, Role.ADMIN)
        def assign_driver():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to your account first.", "error")
                return redirect(url_for('auth.login', next=request.url))
            
            if not hasattr(current_user, 'role') or current_user.role is None:
                flash("User role is not defined.", "error")
                return redirect(url_for('users.profile'))
            
            if current_user.role not in roles:
                allowed_roles = [r.value for r in roles]
                flash(f"Unauthorized access. This page is only accessible to roles: {', '.join(allowed_roles)}.", "error")
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(*permissions):
    """
    Decorator to restrict access based on granular permissions.
    This decorator provides more flexibility than role_required and allows
    customizing permissions in each user's profile.
    
    Usage:
        @users_bp.route('/order/create')
        @login_required
        @permission_required(Permission.ORDER_CREATE)
        def create_order():
            ...
            
        @users_bp.route('/logistics/update')
        @login_required
        @permission_required(Permission.LOGISTICS_UPDATE_STATUS)
        def update_logistics():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to your account first.", "error")
                return redirect(url_for('auth.login', next=request.url))
            
            user_permissions = get_user_permissions(current_user)
            
            # Check if user has at least one of the required permissions
            has_permission = any(perm in user_permissions for perm in permissions)
            
            if not has_permission:
                perm_names = [p.value for p in permissions]
                flash(f"Unauthorized access. You do not have the required permission ({', '.join(perm_names)}).", "error")
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_permissions(user):
    """
    Get list of user permissions.
    Priority:
    1. If user has custom permissions in their profile, those are used as final permissions.
    2. If no custom permissions exist, default role permissions (DEFAULT_ROLE_PERMISSIONS) are used.
    3. If user is guest, guest permissions are returned.
    
    Returns:
        List of Permission objects
    """
    import json
    
    if not user.is_authenticated:
        return DEFAULT_ROLE_PERMISSIONS.get('guest', [])
    
    # Try to get custom permissions from user profile first
    # Use the relationship if available, otherwise query
    profile = None
    if hasattr(user, 'profile') and user.profile:
        profile = user.profile
    else:
        try:
            profile = UserProfile.query.filter_by(user_id=user.id).first()
        except Exception:
            # If database is not available, skip custom permissions
            pass
    
    if profile and profile.custom_permissions:
        # If user has manually set permissions
        from services.permissions import Permission as PermEnum
        custom_perms = []
        
        # Parse JSON string to list
        try:
            if isinstance(profile.custom_permissions, str):
                perm_strings = json.loads(profile.custom_permissions)
            else:
                perm_strings = profile.custom_permissions
            
            if perm_strings:  # If list is not empty
                for perm_str in perm_strings:
                    try:
                        # Support both formats: string and Permission object
                        if isinstance(perm_str, PermEnum):
                            custom_perms.append(perm_str)
                        else:
                            perm = PermEnum(str(perm_str))
                            custom_perms.append(perm)
                    except ValueError:
                        continue  # Ignore invalid permissions
                
                # If valid custom permissions exist, return them
                if custom_perms:
                    return custom_perms
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass  # If JSON is invalid, use default
    
    # Use default role permissions
    role_name = user.role.value if user.role else 'guest'
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])


def has_permission(user, permission):
    """
    Simple check if a user has a specific permission.
    Suitable for use in templates.
    
    Usage in template:
        {% if has_permission(current_user, Permission.ORDER_CREATE) %}
            <a href="/order/create">Create New Order</a>
        {% endif %}
    """
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


def get_role_permissions(role):
    """
    Get default permissions for a specific role.
    
    Args:
        role: Role object or role name string
        
    Returns:
        List of Permission objects for that role
    """
    from models.user import Role
    
    # Convert to string if Role object
    if isinstance(role, Role):
        role_name = role.value
    else:
        role_name = str(role)
    
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])


def service_module_enabled(service_name, user=None):
    """
    Check if a service module is enabled for the user.
    This function is used to show/hide different sections in UI based on role and profile settings.
    
    Args:
        service_name: Service name (e.g., 'logistics', 'legal', 'investment')
        user: User object (if None, uses current_user)
    
    Returns:
        Boolean: True if service is enabled for user
    """
    from flask_login import current_user as cu
    if user is None:
        user = cu
    
    if not user.is_authenticated:
        return False
    
    # Map service name to corresponding permission
    service_permission_map = {
        'order': Permission.ORDER_VIEW,
        'logistics': Permission.LOGISTICS_VIEW_ASSIGNED,
        'legal': Permission.LEGAL_VIEW_CONTRACTS,
        'finance': Permission.FINANCE_VIEW_WALLET,
        'investment': Permission.INVESTMENT_VIEW_PORTFOLIO,
        'technical': Permission.TECH_VIEW_INSPECTIONS,
        'dashboard': Permission.DASHBOARD_VIEW_STATS,
    }
    
    required_permission = service_permission_map.get(service_name)
    if not required_permission:
        return False
    
    return has_permission(user, required_permission)
