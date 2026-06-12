from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user
from models.user import Role, UserProfile
from services.permissions import Permission, DEFAULT_ROLE_PERMISSIONS


def _get_safe_value(item):
    """
    تابع کمکی برای دریافت مقدار متنی به صورت ایمن.
    چه آیتم یک Enum باشد و چه یک String، مقدار متنی آن را برمی‌گرداند.
    """
    if item is None:
        return None
    return item.value if hasattr(item, 'value') else str(item)


def role_required(*roles):
    """
    Decorator to restrict access based on user role.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to your account first.", "error")
                # ✅ اصلاح شده: auth.login به users.login تغییر یافت
                return redirect(url_for('users.login', next=request.url))

            user_role_val = _get_safe_value(current_user.role)
            if user_role_val is None:
                flash("User role is not defined.", "error")
                return redirect(url_for('users.profile'))

            # ✅ مقایسه ایمن: تبدیل همه نقش‌های مجاز به مقدار متنی برای مقایسه
            allowed_role_vals = [_get_safe_value(r) for r in roles]

            if user_role_val not in allowed_role_vals:
                flash(f"Unauthorized access. This page is only accessible to roles: {', '.join(allowed_role_vals)}.",
                      "error")
                abort(403)  # Forbidden

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def permission_required(*permissions):
    """
    Decorator to restrict access based on granular permissions.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to your account first.", "error")
                # ✅ اصلاح شده: auth.login به users.login تغییر یافت
                return redirect(url_for('users.login', next=request.url))

            user_permissions = get_user_permissions(current_user)

            # ✅ بررسی ایمن مجوزها (پشتیبانی از ترکیب Enum و String)
            has_permission = False
            for req_perm in permissions:
                req_val = _get_safe_value(req_perm)
                for user_perm in user_permissions:
                    if _get_safe_value(user_perm) == req_val:
                        has_permission = True
                        break
                if has_permission:
                    break

            if not has_permission:
                perm_names = [_get_safe_value(p) for p in permissions]
                flash(f"Unauthorized access. You do not have the required permission ({', '.join(perm_names)}).",
                      "error")
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_user_permissions(user):
    """
    Get list of user permissions.
    """
    import json

    if not user.is_authenticated:
        return DEFAULT_ROLE_PERMISSIONS.get('guest', [])

    # Try to get custom permissions from user profile first
    profile = None
    if hasattr(user, 'profile') and user.profile:
        profile = user.profile
    else:
        try:
            profile = UserProfile.query.filter_by(user_id=user.id).first()
        except Exception:
            pass

    if profile and profile.custom_permissions:
        from services.permissions import Permission as PermEnum
        custom_perms = []

        try:
            if isinstance(profile.custom_permissions, str):
                perm_strings = json.loads(profile.custom_permissions)
            else:
                perm_strings = profile.custom_permissions

            if perm_strings:
                for perm_str in perm_strings:
                    try:
                        if isinstance(perm_str, PermEnum):
                            custom_perms.append(perm_str)
                        else:
                            perm = PermEnum(str(perm_str))
                            custom_perms.append(perm)
                    except ValueError:
                        continue

                if custom_perms:
                    return custom_perms
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

    # ✅ دریافت ایمن نام نقش برای جستجو در دیکشنری
    role_name = _get_safe_value(user.role) if user.role else 'guest'
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])


def has_permission(user, permission):
    """
    Simple check if a user has a specific permission.
    Suitable for use in templates.
    """
    user_permissions = get_user_permissions(user)

    perm_val = _get_safe_value(permission)
    for user_perm in user_permissions:
        if _get_safe_value(user_perm) == perm_val:
            return True
    return False


def get_role_permissions(role):
    """
    Get default permissions for a specific role.
    """
    from models.user import Role

    # ✅ دریافت ایمن نام نقش
    role_name = _get_safe_value(role)
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])


def service_module_enabled(service_name, user=None):
    """
    Check if a service module is enabled for the user.
    """
    from flask_login import current_user as cu
    from services.permissions import Permission

    if user is None:
        user = cu

    if not user.is_authenticated:
        return False

    service_permission_map = {
        'order': Permission.ORDER_VIEW,
        'logistics': Permission.LOGISTICS_VIEW_ASSIGNED,
        'legal': Permission.LEGAL_VIEW_CONTRACTS,
        'finance': Permission.FINANCE_VIEW_WALLET,
        'investment': Permission.INVESTMENT_VIEW_PORTFOLIO,
        'technical': Permission.TECH_VIEW_INSPECTIONS,
        'dashboard': Permission.DASHBOARD_VIEW_STATS,
        'social': Permission.SOCIAL_ACCESS,
    }

    required_permission = service_permission_map.get(service_name)

    if not required_permission:
        return False

    return has_permission(user, required_permission)