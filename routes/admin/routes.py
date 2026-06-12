# routes/admin/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from models import db, Notification, Message
from models.user import User, Role
from models.premium_request import PremiumRequest

from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

from functools import wraps
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_user
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import admin_bp



@admin_bp.before_request
def make_session_permanent():
    """Make sessions permanent so they expire after PERMANENT_SESSION_LIFETIME"""
    session.permanent = True


# ---------------------------------------
# Decorator: فقط ادمین دسترسی داشته باشه
# ---------------------------------------


@admin_bp.route('/admin')
def admin_index():
    return redirect(url_for('admin.login'))

def admin_required(f):
    @wraps(f)  # ✅ این خط مشکل رو حل می‌کنه
    def decorated_function(*args, **kwargs):
        # ✅ اول چک کن کاربر وارد شده باشد
        if not current_user.is_authenticated:
            flash(_("❌ Please log in first."))
            return redirect(url_for('users.login'))

        if  current_user.role != Role.ADMIN:
            flash(_("❌ Access denied: Only admin can access this page."), "error")
            return redirect(url_for('users.profile'))
        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------
# داشبورد ادمین
# ---------------------------------------
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics and new notifications"""
    from models.auth import ActivityLog
    
    total_users = User.query.count()
    premium_requests = PremiumRequest.query.count()
    pending_requests = PremiumRequest.query.filter_by(status='pending').count()
    
    # Count uploaded documents for review (users who have documents but are not yet verified)
    users_with_pending_docs = User.query.filter(
        User.verification_documents != None,
        User.verification_documents != '[]',
        User.is_verified == False
    ).count()
    
    # Get unread admin notifications
    from models.notification import Notification
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    # ✅ Fetch recent activity logs for admin dashboard
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           premium_requests=premium_requests,
                           pending_requests=pending_requests,
                           users_with_pending_docs=users_with_pending_docs,
                           unread_notifications=unread_notifications,
                           unread_count=unread_count,
                           recent_activities=recent_activities)


# ---------------------------------------
# مدیریت کاربران
# ---------------------------------------

@admin_bp.route('/users')
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status_filter = request.args.get('status', 'active')

    query = User.query

    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    users = query.order_by(User.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # ✅ محاسبه تعداد در بک‌اند
    total_active = User.query.filter_by(is_active=True).count()
    total_inactive = User.query.filter_by(is_active=False).count()

    return render_template(
        'admin/manage_users.html',
        users=users,
        status_filter=status_filter,
        total_active=total_active,
        total_inactive=total_inactive
    )
# ---------------------------------------
# تغییر نقش کاربر
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if not Role.has_value(new_role):
        flash(_("❌ The role is invalid."), "error")
    else:
        user.role = Role(new_role)
        # print(new_role)
        if new_role=="admin":
            user.is_premium=True
            from models.user import MembershipTier
            user.membership_tier = MembershipTier.VERIFIED
            user.is_kyc_verified = True
            user.premium_since = datetime.now(tehran_tz)
        db.session.commit()
        flash(_("✅ User role %(username)s changed to '%(role)s'.") % {
            "username": user.username,
            "role": new_role
        }, "success")
    return redirect(url_for('admin.manage_users'))


# ---------------------------------------
# درخواست‌های ارتقاء به کاربر ویژه
# ---------------------------------------
@admin_bp.route('/premium_requests')
@admin_required
def premium_requests():
    status_filter = request.args.get('status', 'all')
    query = PremiumRequest.query.order_by(PremiumRequest.submitted_at.desc())

    if status_filter == 'pending':
        query = query.filter_by(status='pending')
    elif status_filter == 'approved':
        query = query.filter_by(status='approved')
    elif status_filter == 'rejected':
        query = query.filter_by(status='rejected')

    requests = query.all()
    return render_template('admin/premium_requests.html', requests=requests, status_filter=status_filter)


# ---------------------------------------
# تأیید یا رد درخواست ارتقاء (یکپارچه‌سازی approve و reject)
# ---------------------------------------
@admin_bp.route('/premium_request/<int:req_id>/review', methods=['POST'])
@admin_required
def review_premium_request(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    action = request.form.get('action')
    
    if action == 'approve':
        req.status = 'approved'
        req.user.is_premium = True
        # ارتقای لایه عضویت به VERIFIED (لایه ۲)
        from models.user import MembershipTier
        req.user.membership_tier = MembershipTier.VERIFIED
        # تأیید KYC
        req.user.is_kyc_verified = True
        # افزایش امتیاز اعتماد (Trust Score)
        req.user.trust_score_value = min(100, req.user.trust_score_value + 20)
        # ثبت زمان پریمیوم شدن
        req.user.premium_since = datetime.now(tehran_tz)
        
        # ذخیره مدارک در فیلد verification_documents
        import json
        docs = {
            'passport': req.passport_file,
            'license': req.license_file,
            'payment_receipt': req.payment_receipt,
            'verified_at': datetime.now(tehran_tz).isoformat()
        }
        req.user.verification_documents = json.dumps(docs)
        
        db.session.commit()
        flash(
            _("[SUCCESS] User '%(username)s' successfully promoted to Premium Level 1 (Verified). Trust Score increased by 20 points!") % {
                "username": req.user.username
            },
            "success"
        )
    elif action == 'reject':
        req.status = 'rejected'
        db.session.commit()
        flash(
            _("[warning] Upgrade Request for '%(username)s' rejected.") % {
                "username": req.user.username
            }, "warning")
    else:
        flash(_("⚠️ Invalid action."), "error")
        return redirect(url_for('admin.view_premium_request', req_id=req_id))
    
    db.session.commit()
    return redirect(url_for('admin.premium_requests'))


# ---------------------------------------
# تأیید درخواست ارتقاء (قدیمی - برای سازگاری)
# ---------------------------------------
@admin_bp.route('/approve_premium/<int:req_id>', methods=['POST'])
@admin_required
def approve_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'approved'
    req.user.is_premium = True
    # ارتقای لایه عضویت به VERIFIED (لایه ۲)
    from models.user import MembershipTier
    req.user.membership_tier = MembershipTier.VERIFIED
    # تأیید KYC
    req.user.is_kyc_verified = True
    # ثبت زمان پریمیوم شدن
    req.user.premium_since = datetime.now(tehran_tz)
    db.session.commit()

    flash(
        _("[success] ✅ User '%(username)s' Successfully promoted to special user.") % {
            "username": req.user.username
        }, "success")
    return redirect(url_for('admin.premium_requests'))


# ---------------------------------------
# رد درخواست ارتقاء (قدیمی - برای سازگاری)
# ---------------------------------------
@admin_bp.route('/reject_premium/<int:req_id>', methods=['POST'])
@admin_required
def reject_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    db.session.commit()

    flash(_("❌ Upgrade Request for '%(username)s' rejected.")%{"username": req.user.username}, "error")

    return redirect(url_for('admin.premium_requests'))


# ---------------------------------------
# مشاهده جزئیات درخواست
# ---------------------------------------
@admin_bp.route('/premium_request/<int:req_id>')
@admin_required
def view_premium_request(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    return render_template('admin/view_premium_request.html', req=req)


# ---------------------------------------
# مشاهده مدارک کاربر
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/documents')
@admin_required
def view_user_documents(user_id):
    user = User.query.get_or_404(user_id)
    
    # دریافت مدارک از فیلد verification_documents (JSON format)
    import json
    documents = json.loads(user.verification_documents) if user.verification_documents else []
    
    return render_template('admin/view_user_documents.html', user=user, documents=documents)


# ---------------------------------------
# View all user documents for review
# ---------------------------------------
@admin_bp.route('/documents')
@admin_required
def view_all_documents():
    """Display list of all users who have uploaded documents"""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    status_filter = request.args.get('status', 'pending')  # pending, approved, rejected, all
    
    query = User.query.filter(
        User.verification_documents != None,
        User.verification_documents != '[]'
    )
    
    if status_filter == 'pending':
        query = query.filter_by(is_verified=False)
    elif status_filter == 'approved':
        query = query.filter_by(is_verified=True)
    
    users_with_docs = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Statistics
    total_pending = User.query.filter(
        User.verification_documents != None,
        User.verification_documents != '[]',
        User.is_verified == False
    ).count()
    
    total_approved = User.query.filter(
        User.verification_documents != None,
        User.verification_documents != '[]',
        User.is_verified == True
    ).count()
    
    return render_template('admin/view_all_documents.html', 
                          users=users_with_docs,
                          total_pending=total_pending,
                          total_approved=total_approved,
                          current_status=status_filter)


# ---------------------------------------
# Verify user documents
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/verify_documents', methods=['POST'])
@admin_required
def verify_user_documents(user_id):
    user = User.query.get_or_404(user_id)
    user.is_verified = True
    user.is_kyc_verified = True
    
    # If user has complete documents, upgrade membership tier
    from models.user import MembershipTier
    if user.verification_documents and user.verification_documents != '[]':
        user.membership_tier = MembershipTier.VERIFIED
    
    # Create notification for user
    from models.notification import Notification
    notification = Notification(
        user_id=user.id,
        notification_type='system',
        actor_id=current_user.id,
        related_id=user.id,
        related_type='document_verified',
        title='✅ Your documents have been verified',
        message=_('Your identity verification documents have been successfully verified. Your trust score has been increased.')
    )
    db.session.add(notification)
    
    # Increase TrustScore
    if user.trust_score:
        user.trust_score_value = min(100, user.trust_score_value + 20)
    
    db.session.commit()
    flash(_("✅ Documents of user '%(username)s' have been successfully verified.") % {"username": user.username},
          "success")
    return redirect(url_for('admin.view_user_documents', user_id=user_id))


# ---------------------------------------
# Reject user documents
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/reject_documents', methods=['POST'])
@admin_required
def reject_user_documents(user_id):
    user = User.query.get_or_404(user_id)
    # We can delete documents or just change status
    # Here we just change status to False
    user.is_verified = False
    
    # Create notification for user
    from models.notification import Notification
    notification = Notification(
        user_id=user.id,
        notification_type='system',
        actor_id=current_user.id,
        related_id=user.id,
        related_type='document_rejected',
        title=_('⚠️ Your documents have been rejected'),
        message=_('Your identity verification documents were not approved. Please upload correct documents.')
    )
    db.session.add(notification)
    
    db.session.commit()
    flash(_("Documents of user '%(username)s' have been rejected.") % {'username': user.username}, "warning")
    return redirect(url_for('admin.view_user_documents', user_id=user_id))


# ---------------------------------------
# حذف کاربر (با احتیاط)
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    Notification.query.filter_by(user_id=user_id).delete()
    if current_user.id == user_id:
        flash(_('❌ You cannot delete yourself.'), "error")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    username = user.username

    # حذف درخواست ارتقاء اگر وجود داشت
    req = PremiumRequest.query.filter_by(user_id=user.id).first()
    if req:
        db.session.delete(req)

    user.is_active = False
    # db.session.delete(user)
    db.session.commit()

    flash(_("User✅ '%(username)s' deleted successfully.") % {'username': user.username},"success")

    return redirect(url_for('admin.manage_users'))



# ---------------------------------------
# غیرفعال‌سازی کاربر
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    if current_user.id == user_id:
        flash(_("❌ You cannot deactivate yourself."))
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    if user.role == Role.ADMIN:
        flash(_("❌ You cannot deactivate another admin."))
        return redirect(url_for('admin.manage_users'))

    user.is_active = False
    db.session.commit()
    flash(_("✅ User'%(username)s' has been disabled.")%{'username': user.username})
    return redirect(url_for('admin.manage_users', status=request.args.get('status', 'active')))


# ---------------------------------------
# فعال‌سازی کاربر
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(_("✅ User'%(username)s' activated.")%{'username': user.username})
    return redirect(url_for('admin.manage_users', status=request.args.get('status', 'active')))


# ---------------------------------------
# تغییر وضعیت ویژه (Premium) کاربر
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/toggle_premium', methods=['POST'])
@admin_required
def toggle_premium(user_id):
    if current_user.id == user_id:
        flash(_("❌ You cannot change your own special status."), "error")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    user.is_premium = not user.is_premium
    
    # اگر کاربر پریمیوم شد، لایه عضویت را ارتقا بده
    if user.is_premium:
        from models.user import MembershipTier
        user.membership_tier = MembershipTier.VERIFIED
        user.is_kyc_verified = True
        user.premium_since = datetime.now(tehran_tz)
    
    db.session.commit()
    
    if user.is_premium:
        flash(_("✅ User '%(username)s' is now a special user.")%{'username': user.username}, "success")
    else:
        flash(_("⚠️ Special status removed from user '%(username)s'.")%{'username': user.username}, "warning")
    
    return redirect(url_for('admin.manage_users'))


# ---------------------------------------
# Admin chat with users
# ---------------------------------------
@admin_bp.route('/chat')
@admin_required
def admin_chat_list():
    """User list for chat - display all active users (premium and non-premium)"""
    users = User.query.filter(
        User.id != current_user.id,
        User.is_active == True
    ).order_by(User.username.asc()).all()
    return render_template('admin/chat.html', users=users)


@admin_bp.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_chat_with_user(user_id):
    """Admin chat with a specific user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash(_('❌ You cannot chat with yourself.'), "error")
        return redirect(url_for('admin.admin_chat_list'))
    
    # دریافت پیام‌های بین ادمین و این کاربر
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user.id)) |
        ((Message.sender_id == user.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # علامت‌گذاری پیام‌های دریافتی به عنوان خوانده شده
    for m in messages:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()
    
    # ارسال پیام
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            msg = Message(
                sender_id=current_user.id,
                receiver_id=user.id,
                content=content
            )
            db.session.add(msg)
            
            # ایجاد اعلان برای کاربر
            notification = Notification(
                user_id=user.id,
                message=_('📩 You received a new message from Admin.')
            )
            db.session.add(notification)
            db.session.commit()
            
            flash(_("✅ Message sent to user."), 'success')
            return redirect(url_for('admin.admin_chat_with_user', user_id=user.id))
    
    return render_template('admin/chat_with_user.html', user=user, messages=messages)


# صفحه ورود
@admin_bp.route('/login')
def login():
    # اگر اولین ادمین وجود ندارد، به صفحه ساخت ادمین هدایت کن
    admin_exists = User.query.filter_by(role=Role.ADMIN).first()
    if not admin_exists:
        return redirect(url_for('admin.create_first_admin'))
    return render_template('admin/login.html', current_year=datetime.now().year)

# پردازش ورود
@admin_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email, is_active=True).first()

    if user and check_password_hash(user.password_hash, password):
        if user.role ==  Role.ADMIN:
            login_user(user)
            flash(_("✅ Welcome, admin.!"), "success")
            return redirect(url_for('admin.dashboard'))
        else:
            print(user.role)
            print(user)
            flash(_("❌ Access denied: Only admin can log in."), "error")
    else:
        flash(_("❌ The email or password is incorrect."), "error")

    return redirect(url_for('admin.login'))


# ---------------------------------------
# ساخت اولین ادمین (فقط زمانی که هیچ ادمینی وجود ندارد)
# ---------------------------------------
@admin_bp.route('/create-first-admin', methods=['GET', 'POST'])
def create_first_admin():
    # بررسی اینکه آیا ادمینی وجود دارد یا خیر
    admin_exists = User.query.filter_by(role=Role.ADMIN).first()
    
    if admin_exists:
        flash(_("⚠️ Admin already exists. Please log in."), "warning")
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # اعتبارسنجی
        errors = []
        
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        
        if not email or '@' not in email:
            errors.append("Please enter a valid email address.")
        
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        
        if password != confirm_password:
            errors.append("Passwords do not match.")
        
        # بررسی تکراری بودن ایمیل
        if User.query.filter_by(email=email).first():
            errors.append("This email is already registered.")
        
        # بررسی تکراری بودن نام کاربری
        if User.query.filter_by(username=username).first():
            errors.append("This username is already taken.")
        
        if errors:
            for error in errors:
                flash(_("[ERROR] %(error)s") % {"error": error}, "error")
            return render_template('admin/create_first_admin.html', 
                                 username=username, 
                                 email=email,
                                 current_year=datetime.now().year)
        
        # ساخت کاربر ادمین
        from werkzeug.security import generate_password_hash
        from models.user import MembershipTier
        
        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=Role.ADMIN,
            is_active=True,
            is_verified=True,
            is_kyc_verified=True,
            is_premium=True,
            membership_tier=MembershipTier.ELITE,
            trust_score_value=100,
            premium_since=datetime.now(tehran_tz)
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        # لاگ فعالیت
        from models.auth import ActivityLog
        activity = ActivityLog(
            activity_type='first_admin_created',
            description='First admin account created automatically',
            request=request
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(_("✅ First admin account created successfully! Please log in."), "success")
        return redirect(url_for('admin.login'))
    
    return render_template('admin/create_first_admin.html', 
                         username='', 
                         email='',
                         current_year=datetime.now().year)



@admin_bp.route('/toggle_active/<int:user_id>', methods=['POST'])
@login_required
def toggle_active(user_id):
    # ۱. بررسی دسترسی: فقط ادمین‌ها مجازند
    if not current_user.is_authenticated or current_user.role != Role.ADMIN:
        flash(_('Access denied.'), 'error')
        return redirect(url_for('admin.dashboard'))  # یا آدرس لیست کاربران

    user = User.query.get_or_404(user_id)

    # ۲. جلوگیری از غیرفعال کردن اکانت خود ادمین
    if user.id == current_user.id:
        flash(_('You c…deactivate your own account.'), 'warning')
        return redirect(request.referrer or url_for('admin.dashboard'))

    # ۳. تغییر وضعیت و ذخیره در دیتابیس
    user.is_active = not user.is_active
    db.session.commit()

    # ۴. پیام موفقیت
    status_msg = _('activated') if user.is_active else _('deactivated')
    flash(_('User account has been {} successfully.').format(status_msg), 'success')

    # ۵. بازگشت به صفحه قبلی
    return redirect(request.referrer or url_for('admin.dashboard'))