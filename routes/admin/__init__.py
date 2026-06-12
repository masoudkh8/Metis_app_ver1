from flask import Blueprint

# تعریف Blueprint اصلی
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# یک متغیر ساده برای اینکه بدانیم آیا قبلاً این کار را انجام داده‌ایم یا نه
_is_initialized = False


def init_admin_blueprints():
    """
    Initialize and register all admin-related blueprints.
    این تابع طوری نوشته شده که اگر چند بار صدا زده شود، خطا نمی‌دهد.
    """
    global _is_initialized

    # اگر قبلاً انجام شده، فوراً برگرد و کاری نکن
    if _is_initialized:
        return admin_bp

    try:
        # ایمپورت و ثبت زیرمجموعه‌ها
        from routes.admin.permissions import admin_perms_bp
        admin_bp.register_blueprint(admin_perms_bp)

        # اگر بلوپرینت‌های دیگری هم دارید اینجا اضافه کنید
        # from routes.admin.users import users_mgmt_bp
        # admin_bp.register_blueprint(users_mgmt_bp)

        _is_initialized = True

    except AssertionError:
        # اگر ارور داد که "قبلاً ثبت شده"، نادیده بگیر و پرچم را True کن
        _is_initialized = True
    except Exception as e:
        print(f"[WARNING] Admin blueprint setup skipped: {e}")
        _is_initialized = True

    return admin_bp