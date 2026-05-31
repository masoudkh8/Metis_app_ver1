from enum import Enum

class ServiceCategory(Enum):
    ORDER = 'order'
    LOGISTICS = 'logistics'
    LEGAL = 'legal'
    FINANCE = 'finance'
    TECHNICAL = 'technical'
    DASHBOARD = 'dashboard'
    ADMIN = 'admin'

class Permission(Enum):
    # --- Order Services ---
    ORDER_VIEW = 'order.view'
    ORDER_CREATE = 'order.create'
    ORDER_CANCEL = 'order.cancel'
    ORDER_EDIT = 'order.edit'
    
    # --- Logistics Services ---
    LOGISTICS_VIEW_ASSIGNED = 'logistics.view_assigned'
    LOGISTICS_UPDATE_STATUS = 'logistics.update_status'
    LOGISTICS_ASSIGN_DRIVER = 'logistics.assign_driver'
    
    # --- Legal Services ---
    LEGAL_VIEW_CONTRACTS = 'legal.view_contracts'
    LEGAL_APPROVE_DOCS = 'legal.approve_docs'
    LEGAL_REJECT_DOCS = 'legal.reject_docs'
    
    # --- Finance & Investment ---
    FINANCE_VIEW_WALLET = 'finance.view_wallet'
    FINANCE_WITHDRAW = 'finance.withdraw'
    INVESTMENT_VIEW_PORTFOLIO = 'investment.view_portfolio'
    INVESTMENT_COMMIT = 'investment.commit'
    
    # --- Technical ---
    TECH_VIEW_INSPECTIONS = 'tech.view_inspections'
    TECH_SUBMIT_REPORT = 'tech.submit_report'
    
    # --- Dashboard & Profile ---
    DASHBOARD_VIEW_STATS = 'dashboard.view_stats'
    PROFILE_EDIT = 'profile.edit'
    PROFILE_VERIFY_IDENTITY = 'profile.verify_identity'
    
    # --- Public / Unauthenticated ---
    PUBLIC_VIEW_PRODUCTS = 'public.view_products'
    PUBLIC_VIEW_ABOUT = 'public.view_about'

# تعریف دسترسی‌های پیش‌فرض برای هر نقش (Default Role Policies)
DEFAULT_ROLE_PERMISSIONS = {
    'guest': [  # کاربران غیر احراز هویت
        Permission.PUBLIC_VIEW_PRODUCTS,
        Permission.PUBLIC_VIEW_ABOUT,
    ],
    'buyer': [
        Permission.ORDER_VIEW,
        Permission.ORDER_CREATE,
        Permission.ORDER_CANCEL,
        Permission.FINANCE_VIEW_WALLET,
        Permission.DASHBOARD_VIEW_STATS,
        Permission.PROFILE_EDIT,
    ],
    'producer': [
        Permission.ORDER_VIEW,
        Permission.ORDER_EDIT,
        Permission.LOGISTICS_VIEW_ASSIGNED, # تولیدکننده هم می‌تواند وضعیت لجستیک سفارش خودش را ببیند
        Permission.DASHBOARD_VIEW_STATS,
        Permission.PROFILE_EDIT,
    ],
    'logistics': [
        Permission.LOGISTICS_VIEW_ASSIGNED,
        Permission.LOGISTICS_UPDATE_STATUS,
        Permission.LOGISTICS_ASSIGN_DRIVER,
        Permission.ORDER_VIEW, # برای دیدن جزئیات سفارش جهت حمل
        Permission.DASHBOARD_VIEW_STATS,
    ],
    'legal': [
        Permission.LEGAL_VIEW_CONTRACTS,
        Permission.LEGAL_APPROVE_DOCS,
        Permission.LEGAL_REJECT_DOCS,
        Permission.ORDER_VIEW, # مشاهده سفارش مرتبط با قرارداد
    ],
    'tech_partner': [
        Permission.TECH_VIEW_INSPECTIONS,
        Permission.TECH_SUBMIT_REPORT,
        Permission.ORDER_VIEW,
    ],
    'investor': [
        Permission.INVESTMENT_VIEW_PORTFOLIO,
        Permission.INVESTMENT_COMMIT,
        Permission.FINANCE_VIEW_WALLET,
        Permission.DASHBOARD_VIEW_STATS,
    ],
    'corporate_agent': [
        Permission.ORDER_VIEW,
        Permission.LEGAL_VIEW_CONTRACTS,
        Permission.DASHBOARD_VIEW_STATS,
    ],
    'broker': [
        Permission.ORDER_VIEW,
        Permission.DASHBOARD_VIEW_STATS,
        Permission.FINANCE_VIEW_WALLET,
    ],
    'admin': [
        perm for perm in Permission # دسترسی به همه چیز
    ]
}

def get_role_permissions(role):
    """
    دریافت لیست مجوزهای پیش‌فرض برای یک نقش خاص.
    
    Args:
        role: شیء Role از enum
        
    Returns:
        لیستی از اشیاء Permission
    """
    if role is None:
        return DEFAULT_ROLE_PERMISSIONS.get('guest', [])
    
    role_name = role.name.lower() if hasattr(role, 'name') else str(role).lower()
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])
