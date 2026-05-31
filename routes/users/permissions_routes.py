
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask.views import MethodView
from flask_login import login_required, current_user
from models import db
from models.user import User, UserProfile, Role
from services.permissions import Permission, DEFAULT_ROLE_PERMISSIONS
from services.access_control import role_required, permission_required, get_user_permissions, has_permission
import json

# users_bp = Blueprint('users', __name__, url_prefix='/users')
# Using shared users_bp from __init__.py
from . import users_bp


def _get_permission_category(permission):
    """Determine category of each permission - helper function shared between CBV and FBV"""
    category_map = {
        'ORDER': 'Orders',
        'LOGISTICS': 'Logistics',
        'LEGAL': 'Legal',
        'FINANCE': 'Finance',
        'INVESTMENT': 'Investment',
        'TECH': 'Technical',
        'DASHBOARD': 'Dashboard',
        'PROFILE': 'Profile',
        'PUBLIC': 'Public',
    }
    
    for prefix, category in category_map.items():
        if permission.name.startswith(prefix):
            return category
    
    return 'Other'


# ============================================
# Implementation using MethodView (CBV)
# ============================================

class ManagePermissionsView(MethodView):
    """Class-based view for permissions management"""
    
    decorators = [login_required, role_required(Role.ADMIN)]
    
    def get(self):
        """نمایش صفحه مدیریت مجوزها"""
        from models.user import UserProfile
        import json
        
        target_user_id = request.args.get('target_user_id')
        
        if target_user_id:
            try:
                target_user_id = int(target_user_id)
            except (ValueError, TypeError):
                target_user_id = current_user.id
        else:
            target_user_id = current_user.id
        
        target_user = User.query.get_or_404(target_user_id)
        
        # Auto-create profile if doesn't exist
        if not target_user.profile:
            target_profile = UserProfile(user_id=target_user.id)
            db.session.add(target_profile)
            db.session.commit()
            flash(f"Profile for user {target_user.username} was automatically created.", "info")
        else:
            target_profile = target_user.profile
        
        default_perms = DEFAULT_ROLE_PERMISSIONS.get(target_user.role.value if target_user.role else 'guest', [])
        custom_perms = target_profile.get_custom_permissions() if target_profile else []
        
        # Convert default permissions to string list for correct comparison
        default_perms_values = [p.value if hasattr(p, 'value') else p for p in default_perms]
        
        all_permissions = [
            {
                'value': perm.value,
                'name': perm.name,
                'category': _get_permission_category(perm),
                'is_enabled': perm.value in custom_perms if custom_perms else perm.value in default_perms_values
            }
            for perm in Permission
        ]
        
        categories = {}
        for perm in all_permissions:
            cat = perm['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(perm)
        
        users_list = User.query.order_by(User.username).all() if current_user.role == Role.ADMIN else []
        
        return render_template('users/manage_permissions.html',
                             categories=categories,
                             default_perms=[p.value for p in default_perms],
                             custom_perms=custom_perms,
                             users_list=users_list,
                             current_user_obj=current_user,
                             target_user=target_user)
    
    def post(self):
        """Save permission changes"""
        from flask_wtf.csrf import validate_csrf
        from wtforms.validators import ValidationError
        from models.user import UserProfile
        
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash("Security error: Invalid CSRF token.", "error")
            return redirect(url_for('users.manage_permissions'))
        
        target_user_id = request.form.get('target_user_id') or current_user.id
        
        try:
            target_user_id = int(target_user_id)
        except (ValueError, TypeError):
            target_user_id = current_user.id
        
        target_user = User.query.get_or_404(target_user_id)
        
        if not target_user.profile:
            target_profile = UserProfile(user_id=target_user.id)
            db.session.add(target_profile)
            db.session.commit()
        else:
            target_profile = target_user.profile
        
        selected_permissions = request.form.getlist('permissions')
        
        valid_permissions = []
        for perm_value in selected_permissions:
            try:
                Permission(perm_value)
                valid_permissions.append(perm_value)
            except ValueError:
                continue
        
        if valid_permissions:
            target_profile.set_custom_permissions(valid_permissions)
            flash(f"Permissions for user {target_user.username} updated successfully. ({len(valid_permissions)} active permissions)", "success")
        else:
            target_profile.set_custom_permissions([])
            flash(f"Permissions for user {target_user.username} reverted to default.", "info")
        
        db.session.commit()
        return redirect(url_for('users.manage_permissions', target_user_id=target_user.id))

# ثبت View به عنوان route
users_bp.add_url_rule(
    '/profile/permissions-cbv',
    view_func=ManagePermissionsView.as_view('manage_permissions_cbv'),
    methods=['GET', 'POST']
)


@users_bp.route('/profile/permissions', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN)
def manage_permissions():
    """
    Manage custom permissions for user - FBV (Function Based View)
    Only admin can enable/disable specific permissions for any user.
    """
    from models.user import UserProfile
    import json
    
    # Get target_user_id from query parameter or form
    target_user_id = request.args.get('target_user_id') or request.form.get('target_user_id')
    
    # If target_user_id not specified, use current user (view only)
    if target_user_id:
        try:
            target_user_id = int(target_user_id)
        except (ValueError, TypeError):
            target_user_id = current_user.id
    else:
        target_user_id = current_user.id
    
    target_user = User.query.get_or_404(target_user_id)
    
    # === Auto-create profile if doesn't exist ===
    if not target_user.profile:
        target_profile = UserProfile(user_id=target_user.id)
        db.session.add(target_profile)
        db.session.commit()
        flash(f"Profile for user {target_user.username} was automatically created.", "info")
    else:
        target_profile = target_user.profile
    
    # Get default permissions for target user's role
    default_perms = DEFAULT_ROLE_PERMISSIONS.get(target_user.role.value if target_user.role else 'guest', [])
    
    # Get custom permissions using new model method
    custom_perms = target_profile.get_custom_permissions() if target_profile else []
    
    # Convert default permissions to string list for correct comparison
    default_perms_values = [p.value if hasattr(p, 'value') else p for p in default_perms]
    
    # Convert to appropriate format for display
    all_permissions = [
        {
            'value': perm.value,
            'name': perm.name,
            'category': _get_permission_category(perm),
            'is_enabled': perm.value in custom_perms if custom_perms else perm.value in default_perms_values
        }
        for perm in Permission
    ]
    
    # Group by category
    categories = {}
    for perm in all_permissions:
        cat = perm['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(perm)
    
    if request.method == 'POST':
        # Check CSRF Token
        from flask_wtf.csrf import validate_csrf
        from wtforms.validators import ValidationError
        
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash("Security error: Invalid CSRF token.", "error")
            return redirect(url_for('users.manage_permissions'))
        
        # Get list of selected permissions from form
        selected_permissions = request.form.getlist('permissions')
        
        # Validate and filter valid permissions
        valid_permissions = []
        for perm_value in selected_permissions:
            try:
                # Ensure permission is valid
                Permission(perm_value)
                valid_permissions.append(perm_value)
            except ValueError:
                continue  # Ignore invalid permissions
        
        # Use new model methods to save permissions
        if valid_permissions:
            target_profile.set_custom_permissions(valid_permissions)
            flash(f"Permissions for user {target_user.username} updated successfully. ({len(valid_permissions)} active permissions)", "success")
        else:
            target_profile.set_custom_permissions([])
            flash(f"Permissions for user {target_user.username} reverted to default.", "info")
        
        db.session.commit()
        return redirect(url_for('users.manage_permissions', target_user_id=target_user.id))
    
    # If user is admin, send list of users for selection
    users_list = []
    if current_user.role == Role.ADMIN:
        users_list = User.query.order_by(User.username).all()
    
    return render_template('users/manage_permissions.html',
                         categories=categories,
                         default_perms=[p.value for p in default_perms],  # Convert to string list
                         custom_perms=custom_perms,
                         users_list=users_list,
                         current_user_obj=current_user,
                         target_user=target_user,
                         get_permission_category=_get_permission_category)


@users_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Smart dashboard that displays relevant services based on user role and permissions.
    """
    from services.access_control import service_module_enabled
    from models.notification import Notification
    
    # Check access to various modules
    modules = {
        'order': service_module_enabled('order'),
        'logistics': service_module_enabled('logistics'),
        'legal': service_module_enabled('legal'),
        'finance': service_module_enabled('finance'),
        'investment': service_module_enabled('investment'),
        'technical': service_module_enabled('technical'),
        'dashboard': service_module_enabled('dashboard'),
    }
    
    # Get stats based on role
    stats = _get_user_stats(current_user)
    
    # Calculate unread notifications count
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Determine document verification status
    import json
    verification_docs = json.loads(current_user.verification_documents) if current_user.verification_documents else []
    document_status = 'not_uploaded'
    if verification_docs:
        document_status = 'pending'
        if current_user.is_verified:
            document_status = 'approved'
    
    # Integrate modular dashboard into main dashboard.html for consistency
    return render_template('users/dashboard.html', 
                         modules=modules, 
                         stats=stats,
                         user=current_user,
                         user_role=current_user.role.value,
                         unread_notifications=unread_notifications,
                         document_status=document_status,
                         pending_orders=stats.get('pending_orders', 0))


def _get_user_stats(user):
    """Get user-related statistics based on role"""
    stats = {}
    
    # Example: Order statistics
    if user.role in [Role.BUYER, Role.PRODUCER, Role.BROKER]:
        from models.order import Order
        user_orders = Order.query.filter(
            db.or_(
                Order.buyer_id == user.id,
                Order.seller_id == user.id,
                Order.broker_id == user.id
            )
        ).all()
        stats['total_orders'] = len(user_orders)
        stats['pending_orders'] = len([o for o in user_orders if o.status.value == 'pending'])
    
    # Example: Logistics statistics
    if user.role == Role.LOGISTICS:
        from models.order import Order
        logistics_orders = Order.query.filter_by(logistics_provider_id=user.id).all()
        stats['assigned_shipments'] = len(logistics_orders)
        stats['in_transit'] = len([o for o in logistics_orders if o.status.value == 'in_transit'])
    
    # Example: Investment statistics
    if user.role == Role.INVESTOR:
        stats['portfolio_value'] = 0  # TODO: Calculate from Investment model
        stats['active_investments'] = 0
    
    return stats


@users_bp.route('/logistics/orders')
@login_required
@role_required(Role.LOGISTICS, Role.ADMIN)
def logistics_orders():
    """Display orders assigned to logistics provider"""
    from models.order import Order
    
    orders = Order.query.filter_by(logistics_provider_id=current_user.id).all()
    return render_template('users/logistics_orders.html', orders=orders)


@users_bp.route('/legal/reviews')
@login_required
@role_required(Role.LEGAL, Role.ADMIN)
def legal_reviews():
    """Display contracts requiring legal review"""
    from models.order import Order
    
    orders = Order.query.filter_by(legal_advisor_id=current_user.id).all()
    return render_template('users/legal_reviews.html', orders=orders)


@users_bp.route('/technical/inspections')
@login_required
@role_required(Role.TECH_PARTNER, Role.ADMIN)
def technical_inspections():
    """Display technical inspection requests"""
    from models.order import Order
    
    orders = Order.query.filter_by(tech_partner_id=current_user.id).all()
    return render_template('users/technical_inspections.html', orders=orders)


@users_bp.route('/investment/portfolio')
@login_required
@role_required(Role.INVESTOR, Role.ADMIN)
def investment_portfolio():
    """Display investment portfolio"""
    # TODO: Implement Investment model and its relationship with user
    investments = []  # Investment.query.filter_by(investor_id=current_user.id).all()
    return render_template('users/investment_portfolio.html', investments=investments)


@users_bp.route('/corporate/approvals')
@login_required
@role_required(Role.CORPORATE_AGENT, Role.ADMIN)
def corporate_approvals():
    """Display required corporate approvals"""
    from models.order import Order
    
    orders = Order.query.filter_by(corporate_agent_id=current_user.id).all()
    return render_template('users/corporate_approvals.html', orders=orders)


@users_bp.route('/broker/commissions')
@login_required
@role_required(Role.BROKER, Role.ADMIN)
def broker_commissions():
    """Display brokerage commissions"""
    from models.order import Order
    
    orders = Order.query.filter_by(broker_id=current_user.id).all()
    total_commission = sum(o.commission_amount or 0 for o in orders)
    
    return render_template('users/broker_commissions.html', 
                         orders=orders, 
                         total_commission=total_commission)
