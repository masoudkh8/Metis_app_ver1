# models/data_intelligence.py
# بخش ۸: دیتا و هوش تجاری (Data & Intelligence Layer)

from . import db
from datetime import datetime
import json

class JSONB(db.TypeDecorator):
    """Platform-independent JSON type that uses JSONB for PostgreSQL and JSON for others."""
    impl = db.JSON
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return json.dumps(value) if value else None
        return value
    
    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            return json.loads(value) if value else None
        return value

class MarketTrend(db.Model):
    """روندهای بازار و تحلیل‌های کلان"""
    __tablename__ = 'market_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    trend_type = db.Column(db.String(100), nullable=False, index=True)
    
    product_category = db.Column(db.String(200))
    hs_codes = db.Column(db.JSON)
    countries = db.Column(db.JSON)
    
    title = db.Column(db.String(300), nullable=False)
    title_fa = db.Column(db.String(300))
    title_en = db.Column(db.String(300))
    title_ar = db.Column(db.String(300))
    
    description = db.Column(db.Text)
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    
    metrics = db.Column(JSONB)
    direction = db.Column(db.String(20))
    confidence_level = db.Column(db.Float)
    
    time_period = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    data_sources = db.Column(db.JSON)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<MarketTrend {self.trend_type}>'


class CompetitorAnalysis(db.Model):
    """تحلیل رقبا"""
    __tablename__ = 'competitor_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(300), nullable=False)
    company_name_fa = db.Column(db.String(300))
    company_name_en = db.Column(db.String(300))
    company_name_ar = db.Column(db.String(300))
    
    country_code = db.Column(db.String(3), index=True)
    industry = db.Column(db.String(200))
    products = db.Column(db.JSON)
    
    performance_metrics = db.Column(JSONB)
    strengths = db.Column(db.JSON)
    weaknesses = db.Column(db.JSON)
    
    threat_level = db.Column(db.String(20))
    
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompetitorAnalysis {self.company_name}>'


class DemandForecast(db.Model):
    """پیش‌بینی تقاضا با AI"""
    __tablename__ = 'demand_forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    product_name = db.Column(db.String(300), nullable=False)
    product_name_fa = db.Column(db.String(300))
    product_name_en = db.Column(db.String(300))
    product_name_ar = db.Column(db.String(300))
    
    hs_code = db.Column(db.String(20), index=True)
    country_code = db.Column(db.String(3), nullable=False, index=True)
    
    forecast_period = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    predicted_demand = db.Column(db.Float)
    predicted_demand_unit = db.Column(db.String(50))
    
    confidence_interval_lower = db.Column(db.Float)
    confidence_interval_upper = db.Column(db.Float)
    confidence_level = db.Column(db.Float)
    
    influencing_factors = db.Column(JSONB)
    scenarios = db.Column(JSONB)
    
    model_name = db.Column(db.String(100))
    historical_accuracy = db.Column(db.Float)
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_latest = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<DemandForecast {self.product_name} - {self.country_code}>'


class TradeStatistic(db.Model):
    """آمار و ارقام تجاری کلان"""
    __tablename__ = 'trade_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    stat_type = db.Column(db.String(100), nullable=False, index=True)
    product_category = db.Column(db.String(200))
    hs_code = db.Column(db.String(20), index=True)
    country_code = db.Column(db.String(3), index=True)
    
    period_type = db.Column(db.String(50))
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    
    value = db.Column(db.Float)
    unit = db.Column(db.String(50))
    change_percent = db.Column(db.Float)
    change_absolute = db.Column(db.Float)
    
    breakdown = db.Column(JSONB)
    data_source = db.Column(db.String(200))
    
    reliability_score = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TradeStatistic {self.stat_type} - {self.period_start}>'


class CustomReport(db.Model):
    """گزارش‌های سفارشی کاربران"""
    __tablename__ = 'custom_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    title = db.Column(db.String(300), nullable=False)
    title_fa = db.Column(db.String(300))
    title_en = db.Column(db.String(300))
    title_ar = db.Column(db.String(300))
    
    description = db.Column(db.Text)
    report_config = db.Column(JSONB, nullable=False)
    selected_fields = db.Column(db.JSON)
    
    generated_outputs = db.Column(db.JSON)
    
    auto_generate = db.Column(db.Boolean, default=False)
    schedule = db.Column(db.String(100))
    last_generated_at = db.Column(db.DateTime)
    
    is_public = db.Column(db.Boolean, default=False)
    shared_with = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='custom_reports')
    
    def __repr__(self):
        return f'<CustomReport {self.id} - User {self.user_id}>'


class DataAlert(db.Model):
    """هشدارهای خودکار بر اساس تغییرات داده"""
    __tablename__ = 'data_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    name = db.Column(db.String(200), nullable=False)
    name_fa = db.Column(db.String(200))
    name_en = db.Column(db.String(200))
    name_ar = db.Column(db.String(200))
    
    alert_type = db.Column(db.String(100), nullable=False)
    conditions = db.Column(JSONB, nullable=False)
    notification_channels = db.Column(db.JSON)
    
    is_active = db.Column(db.Boolean, default=True)
    last_triggered_at = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='data_alerts')
    
    def __repr__(self):
        return f'<DataAlert {self.name} - User {self.user_id}>'
