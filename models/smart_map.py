# models/smart_map.py
# بخش ۲: نقشه تعاملی و هوش لجستیک (Smart Map & Logistics)

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

class Country(db.Model):
    """اطلاعات کشورهای جهان برای نقشه تجاری"""
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), nullable=False, unique=True)
    code_alpha2 = db.Column(db.String(2), unique=True)
    
    name_fa = db.Column(db.String(100))
    name_en = db.Column(db.String(100))
    name_ar = db.Column(db.String(100))
    
    region = db.Column(db.String(100))
    subregion = db.Column(db.String(100))
    continent = db.Column(db.String(50))
    
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    bounding_box = db.Column(JSONB)
    
    currency_code = db.Column(db.String(10))
    gdp_per_capita = db.Column(db.Float)
    population = db.Column(db.BigInteger)
    
    is_sanctioned = db.Column(db.Boolean, default=False)
    sanction_details = db.Column(db.Text)
    risk_level = db.Column(db.String(20), default='medium')
    
    trade_relation_score = db.Column(db.Integer)
    has_trade_agreement = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Country {self.code} - {self.name_en}>'


class CustomsData(db.Model):
    """داده‌های گمرکی و تعرفه‌ای هر کشور"""
    __tablename__ = 'customs_data'
    
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, index=True)
    
    hs_code = db.Column(db.String(20), nullable=False, index=True)
    product_name_fa = db.Column(db.String(300))
    product_name_en = db.Column(db.String(300))
    product_name_ar = db.Column(db.String(300))
    
    import_tariff = db.Column(db.Float)
    export_tariff = db.Column(db.Float)
    vat_rate = db.Column(db.Float)
    additional_taxes = db.Column(JSONB)
    
    is_prohibited = db.Column(db.Boolean, default=False)
    requires_license = db.Column(db.Boolean, default=False)
    license_types = db.Column(db.JSON)
    
    required_documents = db.Column(JSONB)
    special_regulations = db.Column(db.Text)
    special_regulations_fa = db.Column(db.Text)
    special_regulations_en = db.Column(db.Text)
    special_regulations_ar = db.Column(db.Text)
    
    data_source = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    country = db.relationship('Country', backref='customs_data')
    
    def __repr__(self):
        return f'<CustomsData {self.hs_code} - Country {self.country_id}>'


class RiskEvent(db.Model):
    """رویدادهای ریسک ژئوپلیتیک و اقتصادی"""
    __tablename__ = 'risk_events'
    
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, index=True)
    
    event_type = db.Column(db.String(100), nullable=False)
    
    title = db.Column(db.String(300), nullable=False)
    title_fa = db.Column(db.String(300))
    title_en = db.Column(db.String(300))
    title_ar = db.Column(db.String(300))
    
    description = db.Column(db.Text)
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    
    severity = db.Column(db.String(20), nullable=False)
    impact_score = db.Column(db.Integer)
    
    location = db.Column(db.String(300))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    occurred_at = db.Column(db.DateTime)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    affected_sectors = db.Column(db.JSON)
    trade_impact = db.Column(db.String(100))
    
    recommendations = db.Column(db.Text)
    recommendations_fa = db.Column(db.Text)
    recommendations_en = db.Column(db.Text)
    recommendations_ar = db.Column(db.Text)
    
    sources = db.Column(db.JSON)
    
    country = db.relationship('Country', backref='risk_events')
    
    def __repr__(self):
        return f'<RiskEvent {self.id} - {self.event_type}>'


class TradeRoute(db.Model):
    """مسیرهای تجاری و حمل‌ونقل بین کشورها"""
    __tablename__ = 'trade_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    origin_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, index=True)
    destination_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, index=True)
    
    route_type = db.Column(db.String(50), nullable=False)
    
    origin_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'))
    destination_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'))
    
    distance_km = db.Column(db.Float)
    estimated_days = db.Column(db.Integer)
    
    base_cost_usd = db.Column(db.Float)
    fuel_surcharge = db.Column(db.Float)
    insurance_cost = db.Column(db.Float)
    
    max_weight_kg = db.Column(db.Float)
    max_volume_m3 = db.Column(db.Float)
    frequency_per_week = db.Column(db.Integer)
    
    is_active = db.Column(db.Boolean, default=True)
    reliability_score = db.Column(db.Integer)
    current_congestion = db.Column(db.String(20))
    
    requires_transit = db.Column(db.Boolean, default=False)
    transit_countries = db.Column(db.JSON)
    special_requirements = db.Column(db.Text)
    
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    origin_country = db.relationship('Country', foreign_keys=[origin_country_id], backref='origin_routes')
    destination_country = db.relationship('Country', foreign_keys=[destination_country_id], backref='destination_routes')
    
    __table_args__ = (
        db.UniqueConstraint('origin_country_id', 'destination_country_id', 'route_type', name='unique_route'),
    )
    
    def __repr__(self):
        return f'<TradeRoute {self.origin_country_id} -> {self.destination_country_id} ({self.route_type})>'


class ShipmentTracking(db.Model):
    """رهگیری محموله‌ها"""
    __tablename__ = 'shipment_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    
    tracking_number = db.Column(db.String(100), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    origin_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    destination_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    
    shipment_type = db.Column(db.String(50))
    current_status = db.Column(db.String(100), default='pending')
    
    current_location = db.Column(db.String(300))
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    
    shipped_at = db.Column(db.DateTime)
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    
    tracking_history = db.Column(JSONB, default=list)
    
    notify_on_update = db.Column(db.Boolean, default=True)
    last_notification_sent = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='shipments')
    
    def __repr__(self):
        return f'<ShipmentTracking {self.tracking_number}>'
