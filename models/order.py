# models/order.py
from . import db
from datetime import datetime
import pytz
from enum import Enum
from sqlalchemy import Enum as SqlEnum

# تنظیم منطقه زمانی تهران
tehran_tz = pytz.timezone('Asia/Tehran')

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    quantity_tons = db.Column(db.Float, nullable=False)
    price_per_ton = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)  # محاسبه شده

    origin_port = db.Column(db.String(100), nullable=False)
    destination_port = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    status = db.Column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)

    # 🔑 Foreign keys — correct table name: 'user'
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Timestamps — using lambda for runtime evaluation
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz), onupdate=lambda: datetime.now(tehran_tz))
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders')
    broker = db.relationship('User', foreign_keys=[broker_id], backref='brokered_orders')

    def calculate_total(self):
        """Calculate total price: quantity * price"""
        self.total_price = self.quantity_tons * self.price_per_ton

    def __repr__(self):
        return f"<Order {self.id} | {self.product} | {self.quantity_tons}T | {self.status.value}>"