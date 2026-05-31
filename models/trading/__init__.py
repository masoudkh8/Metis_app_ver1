"""
Metisma Trading Hall Models
=================================
Online Trading Data Models for Metisma

Includes:
- Trading pairs
- Digital wallets
- Order placement and trades
- Market data

Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
try:
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    POSTGRES_AVAILABLE = True
except ImportError:
    from sqlalchemy import JSON as JSONB
    from sqlalchemy import String as UUID_str
    import uuid as uuid_module
    POSTGRES_AVAILABLE = False
import uuid

# Use the main db instance from models
from models import db

# Helper for UUID type compatibility
UUID_TYPE = UUID(as_uuid=True) if POSTGRES_AVAILABLE else db.String(36)


# =============================================================================
# ENUM Tables
# =============================================================================

class OrderType(db.Model):
    """Order types"""
    __tablename__ = 'order_type_enum'
    
    id = db.Column(db.Integer, primary_key=True)
    order_type = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<OrderType {self.order_type}>"


class OrderSide(db.Model):
    """Order side (buy/sell)"""
    __tablename__ = 'order_side_enum'
    
    id = db.Column(db.Integer, primary_key=True)
    side = db.Column(db.String(10), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<OrderSide {self.side}>"


class OrderStatus(db.Model):
    """Order statuses"""
    __tablename__ = 'order_status_enum'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<OrderStatus {self.status}>"


# =============================================================================
# TRADING MODELS
# =============================================================================

class TradingPair(db.Model):
    """
    Tradable asset pairs
    Example: BTC/USDT, GOLD/USD
    """
    __tablename__ = 'trading_pairs'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    
    base_asset = db.Column(db.String(50), nullable=False)  # Base Currency
    quote_asset = db.Column(db.String(50), nullable=False)  # Quote Currency
    symbol = db.Column(db.String(20), unique=True, nullable=False)  # Display Symbol
    
    # Trade Specifications
    min_order_size = db.Column(db.Numeric(20, 8), nullable=False)
    max_order_size = db.Column(db.Numeric(20, 8), nullable=False)
    price_precision = db.Column(db.Integer, default=2)  # Price Precision
    quantity_precision = db.Column(db.Integer, default=8)  # Quantity Precision
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Limits/Restrictions
    trading_hours = db.Column(db.JSON, default={})  # Allowed Trading Hours
    allowed_user_levels = db.Column(db.JSON, default=[])  # Allowed User Levels
    
    # Market Statistics (24 hours)
    last_price = db.Column(db.Numeric(20, 8))
    price_change_24h = db.Column(db.Numeric(10, 4))  # Percentage Change
    volume_24h = db.Column(db.Numeric(20, 8), default=0)
    high_24h = db.Column(db.Numeric(20, 8))
    low_24h = db.Column(db.Numeric(20, 8))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_trading_pairs_symbol', 'symbol', unique=True),
        db.Index('idx_trading_pairs_assets', 'base_asset', 'quote_asset'),
        db.Index('idx_trading_pairs_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<TradingPair {self.symbol}>"


class TradingWallet(db.Model):
    """
    Internal user wallet for trading
    Each user has a multi-currency wallet
    """
    __tablename__ = 'trading_wallets'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID_TYPE, nullable=False, unique=True)
    
    # Balances as JSONB: {"USDT": 1000.50, "BTC": 0.05}
    balances = db.Column(db.JSON, default={})
    locked_balances = db.Column(db.JSON, default={})  # Locked Balances in Orders
    
    # Credit
    credit_limit = db.Column(db.Numeric(20, 8), default=0)
    used_credit = db.Column(db.Numeric(20, 8), default=0)
    
    # Trading Statistics
    total_trades = db.Column(db.Integer, default=0)
    total_volume = db.Column(db.Numeric(30, 8), default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Risk Management
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high
    daily_loss_limit = db.Column(db.Numeric(20, 8))  # Daily Loss Limit
    daily_loss_current = db.Column(db.Numeric(20, 8), default=0)  # Current Loss Today
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_trading_wallets_user', 'user_id', unique=True),
        db.Index('idx_trading_wallets_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<TradingWallet User: {self.user_id}>"


class TradingWalletTransaction(db.Model):
    """
    Trading wallet transactions
    Records all balance changes in trading hall
    """
    __tablename__ = 'trading_wallet_transactions'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    wallet_id = db.Column(UUID_TYPE, db.ForeignKey('trading_wallets.id'), nullable=False)
    
    transaction_type = db.Column(db.String(50), nullable=False)
    # deposit, withdrawal, trade_profit, trade_loss, fee, transfer, refund
    
    asset = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    balance_before = db.Column(db.Numeric(20, 8), nullable=False)
    balance_after = db.Column(db.Numeric(20, 8), nullable=False)
    
    # Reference to Related Order or Trade
    related_order_id = db.Column(UUID_TYPE)
    related_trade_id = db.Column(UUID_TYPE)
    
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(100))  # External Reference ID
    
    status = db.Column(db.String(50), default='completed')
    extra_data = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    wallet = db.relationship('TradingWallet', backref='transactions')
    
    __table_args__ = (
        db.Index('idx_trading_wallet_transactions_wallet', 'wallet_id'),
        db.Index('idx_trading_wallet_transactions_type', 'transaction_type'),
        db.Index('idx_trading_wallet_transactions_time', 'created_at'),
        db.Index('idx_trading_wallet_transactions_status', 'status'),
    )
    
    def __repr__(self):
        return f"<WalletTransaction {self.transaction_type} - {self.amount} {self.asset}>"


class TradeOrder(db.Model):
    """
    Trade order
    Supports order types: Market, Limit, Stop-Limit
    """
    __tablename__ = 'trade_orders'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    
    user_id = db.Column(UUID_TYPE, nullable=False)
    trading_pair_id = db.Column(UUID_TYPE, db.ForeignKey('trading_pairs.id'), nullable=False)
    
    # Order Type
    type_id = db.Column(db.Integer, db.ForeignKey('order_type_enum.id'), nullable=False)
    order_type = db.relationship('OrderType', backref='orders')
    
    # Order Side
    side_id = db.Column(db.Integer, db.ForeignKey('order_side_enum.id'), nullable=False)
    side = db.relationship('OrderSide', backref='orders')
    
    # Price and Quantity
    price = db.Column(db.Numeric(20, 8))  # for Limit orders
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    filled_quantity = db.Column(db.Numeric(20, 8), default=0)
    remaining_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    
    # Conditional Prices
    stop_price = db.Column(db.Numeric(20, 8))  # for Stop orders
    trigger_price = db.Column(db.Numeric(20, 8))  # Price at which order is activated
    
    # Status
    status_id = db.Column(db.Integer, db.ForeignKey('order_status_enum.id'), default=1)
    status = db.relationship('OrderStatus', backref='orders')
    
    # Timing/Scheduling
    time_in_force = db.Column(db.String(20), default='GTC')  # GTC, IOC, FOK
    expires_at = db.Column(db.DateTime)
    
    # Financial
    fee_rate = db.Column(db.Numeric(10, 6), default=0.001)  # Fee
    total_fee = db.Column(db.Numeric(20, 8), default=0)
    average_fill_price = db.Column(db.Numeric(20, 8))
    
    # Metadata
    client_order_id = db.Column(db.String(100), unique=True)  # Client Order ID
    notes = db.Column(db.Text)
    extra_data = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Relationships
    trading_pair = db.relationship('TradingPair', backref='orders')
    
    __table_args__ = (
        db.Index('idx_trade_orders_user', 'user_id'),
        db.Index('idx_trade_orders_pair', 'trading_pair_id'),
        db.Index('idx_trade_orders_status', 'status_id'),
        db.Index('idx_trade_orders_side', 'side_id'),
        db.Index('idx_trade_orders_created', 'created_at'),
        db.Index('idx_trade_orders_client', 'client_order_id', unique=True),
    )
    
    def __repr__(self):
        return f"<TradeOrder {self.side.side} {self.quantity} {self.trading_pair_id}>"


class Trade(db.Model):
    """
    Executed trade
    Result of matching buy and sell orders
    """
    __tablename__ = 'trades'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    
    trading_pair_id = db.Column(UUID_TYPE, db.ForeignKey('trading_pairs.id'), nullable=False)
    
    # Orders of Both Parties
    maker_order_id = db.Column(UUID_TYPE, db.ForeignKey('trade_orders.id'), nullable=False)
    taker_order_id = db.Column(UUID_TYPE, db.ForeignKey('trade_orders.id'), nullable=False)
    
    # Trade Information
    price = db.Column(db.Numeric(20, 8), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    quote_amount = db.Column(db.Numeric(20, 8), nullable=False)  # price * quantity
    
    # Fees
    maker_fee = db.Column(db.Numeric(20, 8), default=0)
    taker_fee = db.Column(db.Numeric(20, 8), default=0)
    
    # Roles
    maker_user_id = db.Column(UUID_TYPE, nullable=False)
    taker_user_id = db.Column(UUID_TYPE, nullable=False)
    
    executed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    trading_pair = db.relationship('TradingPair', backref='trades')
    maker_order = db.relationship('TradeOrder', foreign_keys=[maker_order_id], backref='maker_trades')
    taker_order = db.relationship('TradeOrder', foreign_keys=[taker_order_id], backref='taker_trades')
    
    __table_args__ = (
        db.Index('idx_trades_pair', 'trading_pair_id'),
        db.Index('idx_trades_maker', 'maker_order_id'),
        db.Index('idx_trades_taker', 'taker_order_id'),
        db.Index('idx_trades_time', 'executed_at'),
        db.Index('idx_trades_maker_user', 'maker_user_id'),
        db.Index('idx_trades_taker_user', 'taker_user_id'),
    )
    
    def __repr__(self):
        return f"<Trade {self.quantity} @ {self.price}>"


class MarketData(db.Model):
    """
    Historical Market Data for Charts
    Price Candles (OHLCV)
    """
    __tablename__ = 'market_data'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    trading_pair_id = db.Column(UUID_TYPE, db.ForeignKey('trading_pairs.id'), nullable=False)
    
    # Timeframe
    timeframe = db.Column(db.String(10), nullable=False)  # 1m, 5m, 1h, 1d, etc.
    
    # Candle Start Time
    timestamp = db.Column(db.DateTime, nullable=False)
    
    # OHLCV Data
    open_price = db.Column(db.Numeric(20, 8), nullable=False)
    high_price = db.Column(db.Numeric(20, 8), nullable=False)
    low_price = db.Column(db.Numeric(20, 8), nullable=False)
    close_price = db.Column(db.Numeric(20, 8), nullable=False)
    volume = db.Column(db.Numeric(20, 8), default=0)
    quote_volume = db.Column(db.Numeric(30, 8), default=0)
    
    # Number of Trades
    trade_count = db.Column(db.Integer, default=0)
    
    # Additional Data
    vwap = db.Column(db.Numeric(20, 8))  # Volume Weighted Average Price
    extra_data = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    trading_pair = db.relationship('TradingPair', backref='market_data')
    
    __table_args__ = (
        db.Index('idx_market_data_pair_time', 'trading_pair_id', 'timestamp'),
        db.Index('idx_market_data_timeframe', 'timeframe'),
        db.UniqueConstraint('trading_pair_id', 'timeframe', 'timestamp', name='uq_pair_timeframe_time'),
    )
    
    def __repr__(self):
        return f"<MarketData {self.trading_pair_id} {self.timeframe} {self.timestamp}>"


class TradingSetting(db.Model):
    """
    General trading hall settings
    """
    __tablename__ = 'trading_settings'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.JSON, nullable=False)
    
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    is_public = db.Column(db.Boolean, default=False)  # Can Users View
    category = db.Column(db.String(50), default='general')
    
    updated_by = db.Column(UUID_TYPE)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_trading_settings_key', 'setting_key', unique=True),
        db.Index('idx_trading_settings_category', 'category'),
    )
    
    def __repr__(self):
        return f"<TradingSetting {self.setting_key}>"


# =============================================================================
# Helper Functions
# =============================================================================

def init_trading_db(app=None):
    """
    Initialize trading database
    Create default ENUM values and settings
    """
    if app:
        db.init_app(app)
    
    # Create Order Types
    order_types = ['market', 'limit', 'stop_limit', 'stop_market']
    for otype in order_types:
        existing = OrderType.query.filter_by(order_type=otype).first()
        if not existing:
            db.session.add(OrderType(order_type=otype))
    
    # Create Order Sides
    sides = ['buy', 'sell']
    for side in sides:
        existing = OrderSide.query.filter_by(side=side).first()
        if not existing:
            db.session.add(OrderSide(side=side))
    
    # Create Order Statuses
    statuses = ['pending', 'partially_filled', 'filled', 'cancelled', 'rejected', 'expired']
    for status in statuses:
        existing = OrderStatus.query.filter_by(status=status).first()
        if not existing:
            db.session.add(OrderStatus(status=status))
    
    # Create Default Settings
    default_settings = [
        {
            'key': 'trading_enabled',
            'value': True,
            'desc_fa': 'Trading Hall Enabled',
            'desc_en': 'Trading hall enabled',
            'category': 'general'
        },
        {
            'key': 'default_fee_rate',
            'value': 0.001,
            'desc_fa': 'Default Trading Fee',
            'desc_en': 'Default trading fee rate',
            'category': 'fees'
        },
        {
            'key': 'max_orders_per_user',
            'value': 100,
            'desc_fa': 'Maximum Open Orders Per User',
            'desc_en': 'Maximum open orders per user',
            'category': 'limits'
        }
    ]
    
    for setting in default_settings:
        existing = TradingSetting.query.filter_by(setting_key=setting['key']).first()
        if not existing:
            db.session.add(TradingSetting(
                setting_key=setting['key'],
                setting_value=setting['value'],
                description_fa=setting['desc_fa'],
                description_en=setting['desc_en'],
                category=setting['category'],
                is_public=True
            ))
    
    db.session.commit()
