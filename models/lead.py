# models/lead.py
# بخش ۱۲: Admin & CRM - مدیریت مشتریان و لیدها

from . import db
from datetime import datetime, timedelta
from enum import Enum
import uuid

class LeadStatus(Enum):
    NEW = 'new'  # جدید
    CONTACTED = 'contacted'  # تماس گرفته‌شده
    QUALIFIED = 'qualified'  # واجد شرایط
    PROPOSAL_SENT = 'proposal_sent'  # ارسال پیشنهاد
    NEGOTIATION = 'negotiation'  # در مذاکره
    WON = 'won'  # برنده‌شده
    LOST = 'lost'  # باخته‌شده
    COLD = 'cold'  # سرد

class LeadSource(Enum):
    WEBSITE = 'website'  # وب‌سایت
    REFERRAL = 'referral'  # معرفی
    LINKEDIN = 'linkedin'  # لینکدین
    INSTAGRAM = 'instagram'  # اینستاگرام
    TELEGRAM = 'telegram'  # تلگرام
    WHATSAPP = 'whatsapp'  # واتس‌اپ
    EMAIL_CAMPAIGN = 'email_campaign'  # کمپین ایمیل
    WEBINAR = 'webinar'  # وبینار
    TRADE_SHOW = 'trade_show'  # نمایشگاه تجاری
    MARKETPLACE = 'marketplace'  # مارکت‌پلیس
    OTHER = 'other'  # سایر

class LeadPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'

class PipelineStage(Enum):
    AWARENESS = 'awareness'  # آگاهی
    INTEREST = 'interest'  # علاقه
    EVALUATION = 'evaluation'  # ارزیابی
    DECISION = 'decision'  # تصمیم‌گیری
    PURCHASE = 'purchase'  # خرید
    RETENTION = 'retention'  # حفظ مشتری

class CommunicationChannel(Enum):
    EMAIL = 'email'
    PHONE = 'phone'
    WHATSAPP = 'whatsapp'
    TELEGRAM = 'telegram'
    LINKEDIN = 'linkedin'
    IN_APP_MESSAGE = 'in_app_message'
    VIDEO_CALL = 'video_call'
    MEETING = 'meeting'

class Lead(db.Model):
    """
    سرنخ فروش (Lead) - بخش ۱۲
    """
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # شناسه یکتا
    lead_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    # اطلاعات تماس
    company_name = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))  # شخص تماس
    position = db.Column(db.String(100))  # سمت
    
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    telegram = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(300))
    website = db.Column(db.String(300))
    
    # آدرس
    country = db.Column(db.String(50))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    
    # منبع و وضعیت
    source = db.Column(db.Enum(LeadSource), default=LeadSource.WEBSITE)
    status = db.Column(db.Enum(LeadStatus), default=LeadStatus.NEW)
    priority = db.Column(db.Enum(LeadPriority), default=LeadPriority.MEDIUM)
    
    # اختصاص به کارشناس فروش
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    
    # اطلاعات کسب‌وکار
    industry = db.Column(db.String(100))  # صنعت
    company_size = db.Column(db.String(50))  # اندازه شرکت
    annual_revenue = db.Column(db.String(50))  # درآمد سالانه
    
    # نیازها
    interested_products = db.Column(db.JSON)  # محصولات مورد علاقه
    target_markets = db.Column(db.JSON)  # بازارهای هدف
    requirements = db.Column(db.Text)  # نیازمندی‌ها
    budget_range = db.Column(db.String(50))  # محدوده بودجه
    timeline = db.Column(db.String(50))  # زمان‌بندی مورد نظر
    
    # پایپ‌لاین
    pipeline_stage = db.Column(db.Enum(PipelineStage), default=PipelineStage.AWARENESS)
    deal_value = db.Column(db.Numeric(15, 2))  # ارزش معامله احتمالی
    currency = db.Column(db.String(3), default='USD')
    probability = db.Column(db.Integer, default=10)  # احتمال موفقیت (درصد)
    
    # امتیازدهی
    lead_score = db.Column(db.Integer, default=0)  # امتیاز لید
    
    # آخرین تعامل
    last_contact_date = db.Column(db.DateTime)
    next_follow_up = db.Column(db.DateTime)
    
    # توضیحات
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)  # یادداشت‌های داخلی
    
    # تبدیل به مشتری
    converted_to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    converted_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref=db.backref('assigned_leads', lazy='dynamic'))
    converter = db.relationship('User', foreign_keys=[converted_to_user_id], backref=db.backref('converted_leads', lazy='dynamic'))
    
    interactions = db.relationship('LeadInteraction', backref='lead', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('LeadTask', backref='lead', lazy='dynamic', cascade='all, delete-orphan')
    campaigns = db.relationship('CampaignLead', backref='lead', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'country': self.country,
            'status': self.status.value,
            'priority': self.priority.value,
            'pipeline_stage': self.pipeline_stage.value,
            'deal_value': float(self.deal_value) if self.deal_value else None,
            'lead_score': self.lead_score,
            'assigned_to_name': self.assignee.company_name if self.assignee else None,
            'next_follow_up': self.next_follow_up.isoformat() if self.next_follow_up else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LeadInteraction(db.Model):
    """
    تعاملات با لید - بخش ۱۲
    """
    __tablename__ = 'lead_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # نوع تعامل
    interaction_type = db.Column(db.String(50), nullable=False)  # call, email, meeting, message
    channel = db.Column(db.Enum(CommunicationChannel))
    
    # موضوع و محتوا
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # نتیجه
    outcome = db.Column(db.Text)  # نتیجه تعامل
    sentiment = db.Column(db.String(20))  # positive, neutral, negative
    
    # فایل‌های ضمیمه
    attachments = db.Column(db.JSON)  # لیست فایل‌ها
    
    # زمان
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer)  # مدت (برای تماس/جلسه)
    
    # بعدی
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('lead_interactions', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'channel': self.channel.value if self.channel else None,
            'subject': self.subject,
            'outcome': self.outcome,
            'occurred_at': self.occurred_at.isoformat() if self.occurred_at else None,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
        }


class LeadTask(db.Model):
    """
    وظایف مرتبط با لید - بخش ۱۲
    """
    __tablename__ = 'lead_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    task_type = db.Column(db.String(50))  # call, email, proposal, meeting, research
    
    # زمان‌بندی
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # وضعیت
    is_completed = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    
    # یادآوری
    reminder_enabled = db.Column(db.Boolean, default=False)
    reminder_time = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_tasks', lazy='dynamic'))
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref=db.backref('assigned_tasks', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'task_type': self.task_type,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_completed': self.is_completed,
            'assignee_name': self.assignee.company_name if self.assignee else None,
        }


class Campaign(db.Model):
    """
    کمپین بازاریابی - بخش ۱۲
    """
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name_fa = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    
    description = db.Column(db.Text)
    
    # نوع کمپین
    campaign_type = db.Column(db.String(50))  # email, social_media, content, webinar, ads
    channel = db.Column(db.Enum(CommunicationChannel))
    
    # هدف
    objective = db.Column(db.Text)  # هدف کمپین
    target_audience = db.Column(db.JSON)  # مخاطبان هدف
    
    # زمان‌بندی
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    
    # وضعیت
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, completed
    
    # بودجه
    budget = db.Column(db.Numeric(15, 2))
    currency = db.Column(db.String(3), default='USD')
    actual_cost = db.Column(db.Numeric(15, 2), default=0)
    
    # آمار
    total_recipients = db.Column(db.Integer, default=0)
    opens = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    leads_generated = db.Column(db.Integer, default=0)
    
    # محتوا
    email_template = db.Column(db.Text)  # قالب ایمیل
    landing_page_url = db.Column(db.String(500))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', backref=db.backref('campaigns', lazy='dynamic'))
    leads = db.relationship('CampaignLead', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    analytics = db.relationship('CampaignAnalytics', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_fa': self.name_fa,
            'campaign_type': self.campaign_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': float(self.budget) if self.budget else None,
            'leads_generated': self.leads_generated,
            'conversion_rate': (self.conversions / self.total_recipients * 100) if self.total_recipients > 0 else 0,
        }


class CampaignLead(db.Model):
    """
    ارتباط لید با کمپین - بخش ۱۲
    """
    __tablename__ = 'campaign_leads'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False, index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    
    # وضعیت در کمپین
    status = db.Column(db.String(20), default='sent')  # sent, opened, clicked, converted
    
    # تعامل
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    converted_at = db.Column(db.DateTime)
    
    # امتیاز
    engagement_score = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('campaign_id', 'lead_id', name='unique_campaign_lead'),)


class CampaignAnalytics(db.Model):
    """
    تحلیل کمپین - بخش ۱۲
    """
    __tablename__ = 'campaign_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False, index=True)
    
    # تاریخ
    date = db.Column(db.Date, nullable=False)
    
    # آمار روزانه
    sent = db.Column(db.Integer, default=0)
    delivered = db.Column(db.Integer, default=0)
    opened = db.Column(db.Integer, default=0)
    clicked = db.Column(db.Integer, default=0)
    bounced = db.Column(db.Integer, default=0)
    unsubscribed = db.Column(db.Integer, default=0)
    converted = db.Column(db.Integer, default=0)
    
    # هزینه
    daily_cost = db.Column(db.Numeric(10, 2), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('campaign_id', 'date', name='unique_campaign_daily'),)


class EmailTemplate(db.Model):
    """
    قالب‌های ایمیل - بخش ۱۲
    """
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(200), nullable=False)
    subject_fa = db.Column(db.String(200))
    subject_en = db.Column(db.String(200))
    
    content_fa = db.Column(db.Text)
    content_en = db.Column(db.Text)
    
    template_type = db.Column(db.String(50))  # welcome, follow_up, proposal, newsletter
    category = db.Column(db.String(50))
    
    variables = db.Column(db.JSON)  # متغیرهای قابل استفاده
    
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'subject_fa': self.subject_fa,
            'usage_count': self.usage_count,
        }


class AutomationRule(db.Model):
    """
    قوانین اتوماسیون بازاریابی - بخش ۱۲
    """
    __tablename__ = 'automation_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # شرط
    trigger_type = db.Column(db.String(50))  # lead_created, status_changed, no_response, date_based
    conditions = db.Column(db.JSON)  # شرایط اجرا
    
    # عملیات
    actions = db.Column(db.JSON)  # اقدامات خودکار
    
    is_active = db.Column(db.Boolean, default=True)
    execution_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'trigger_type': self.trigger_type,
            'is_active': self.is_active,
            'execution_count': self.execution_count,
        }
