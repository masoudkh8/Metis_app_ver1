"""
Metisma Trading Routes - MVP Version
Real-time Order Book, Trading Pairs, and Wallet Management
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import desc, func, and_
from decimal import Decimal
import json

from models.trading import (
    TradingPair, TradingWallet, TradingWalletTransaction, 
    TradeOrder, Trade, MarketData, TradingSetting
)
from models.user import User
from extensions import db

trading_bp = Blueprint('trading', __name__, url_prefix='/trading')

# --- Public Market Data ---

@trading_bp.route('/')
def market():
    """Main Trading Hall - Market Overview"""
    # Get active trading pairs
    active_pairs = TradingPair.query.filter_by(status='active').order_by(TradingPair.base_currency).all()
    
    # Get market stats
    total_volume_24h = db.session.query(func.sum(Trade.volume)).filter(
        Trade.created_at > datetime.now() - timedelta(hours=24)
    ).scalar() or 0
    
    total_trades_24h = Trade.query.filter(
        Trade.created_at > datetime.now() - timedelta(hours=24)
    ).count()
    
    # Get top gainers/losers (simplified for MVP)
    trending_pairs = TradingPair.query.filter_by(status='active')\
        .order_by(desc(TradingPair.price_change_24h)).limit(5).all()
    
    return render_template('trading/market.html',
                         pairs=active_pairs,
                         total_volume=total_volume_24h,
                         total_trades=total_trades_24h,
                         trending=trending_pairs)

@trading_bp.route('/pair/<string:symbol>')
def trading_pair_detail(symbol):
    """Individual Trading Pair Page with Order Book & Chart"""
    pair = TradingPair.query.filter_by(symbol=symbol.upper(), status='active').first_or_404()
    
    # Get recent trades for this pair
    recent_trades = Trade.query.filter_by(pair_id=pair.id)\
        .order_by(desc(Trade.created_at)).limit(20).all()
    
    # Get order book (simplified - just show active orders)
    buy_orders = TradeOrder.query.filter_by(
        pair_id=pair.id,
        side='buy',
        status='open'
    ).order_by(desc(TradeOrder.price)).limit(10).all()
    
    sell_orders = TradeOrder.query.filter_by(
        pair_id=pair.id,
        side='sell',
        status='open'
    ).order_by(TradeOrder.price).limit(10).all()
    
    # Get market data for chart (last 100 points)
    market_data = MarketData.query.filter_by(pair_id=pair.id)\
        .order_by(desc(MarketData.timestamp)).limit(100).all()
    
    return render_template('trading/pair_detail.html',
                         pair=pair,
                         recent_trades=recent_trades,
                         buy_orders=buy_orders,
                         sell_orders=sell_orders,
                         market_data=market_data)

@trading_bp.route('/api/orderbook/<string:symbol>')
def get_orderbook(symbol):
    """API: Get real-time order book for a pair"""
    pair = TradingPair.query.filter_by(symbol=symbol.upper(), status='active').first()
    if not pair:
        return jsonify({'error': 'Pair not found'}), 404
    
    buy_orders = TradeOrder.query.filter_by(
        pair_id=pair.id,
        side='buy',
        status='open'
    ).order_by(desc(TradeOrder.price)).limit(20).all()
    
    sell_orders = TradeOrder.query.filter_by(
        pair_id=pair.id,
        side='sell',
        status='open'
    ).order_by(TradeOrder.price).limit(20).all()
    
    orderbook = {
        'symbol': pair.symbol,
        'bids': [{'price': float(o.price), 'amount': float(o.remaining_amount)} for o in buy_orders],
        'asks': [{'price': float(o.price), 'amount': float(o.remaining_amount)} for o in sell_orders],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(orderbook)

# --- User Trading Operations ---
from sqlalchemy import or_, desc
@trading_bp.route('/wallet')
@login_required
def wallet():
    """User's Trading Wallet"""
    wallet = TradingWallet.query.filter_by(user_id=current_user.id).first()
    
    if not wallet:
        # Create wallet if doesn't exist
        wallet = TradingWallet(user_id=current_user.id)
        db.session.add(wallet)
        db.session.commit()
    
    # Get recent transactions
    transactions = TradingWalletTransaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(desc(TradingWalletTransaction.created_at)).limit(20).all()
    
    # Get active orders
    active_orders = TradeOrder.query.filter_by(
        user_id=current_user.id,
        status='open'
    ).order_by(desc(TradeOrder.created_at)).all()
    
    # Get trade history
    trade_history = Trade.query.filter(
        or_(Trade.buyer_id == current_user.id, Trade.seller_id == current_user.id)
    ).order_by(desc(Trade.created_at)).limit(20).all()
    
    return render_template('trading/wallet.html',
                         wallet=wallet,
                         transactions=transactions,
                         active_orders=active_orders,
                         trade_history=trade_history)

@trading_bp.route('/order/place', methods=['POST'])
@login_required
def place_order():
    """Place a new trade order"""
    data = request.form
    symbol = data.get('symbol', '').upper()
    order_type = data.get('type', 'limit')  # limit or market
    side = data.get('side', 'buy')  # buy or sell
    amount = Decimal(data.get('amount', '0'))
    price = Decimal(data.get('price', '0')) if order_type == 'limit' else None
    
    pair = TradingPair.query.filter_by(symbol=symbol, status='active').first()
    if not pair:
        flash('Trading pair not found.', 'error')
        return redirect(url_for('trading.market'))
    
    # Validate amount
    if amount <= 0:
        flash('Amount must be positive.', 'error')
        return redirect(url_for('trading.trading_pair_detail', symbol=symbol))
    
    # Check wallet balance for buy orders
    wallet = TradingWallet.query.filter_by(user_id=current_user.id).first()
    if not wallet:
        wallet = TradingWallet(user_id=current_user.id)
        db.session.add(wallet)
        db.session.commit()
    
    if side == 'buy' and order_type == 'limit':
        required_balance = amount * price
        # Convert to quote currency if needed (simplified)
        if wallet.balance_quote < required_balance:
            flash('Insufficient balance.', 'error')
            return redirect(url_for('trading.trading_pair_detail', symbol=symbol))
    
    # Create order
    order = TradeOrder(
        user_id=current_user.id,
        pair_id=pair.id,
        type=order_type,
        side=side,
        amount=amount,
        price=price,
        status='open'
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Try to match order immediately (simplified matching)
    matched = try_match_order(order)
    
    if matched:
        flash(f'Your order of {float(amount)} was executed successfully!', 'success')
    else:
        flash('Your order has been placed in the order book.', 'info')
    
    return redirect(url_for('trading.wallet'))

def try_match_order(new_order):
    """Simple order matching engine (MVP version)"""
    # Find opposite orders
    if new_order.side == 'buy':
        opposite_side = 'sell'
        # Find sell orders with price <= buy price
        matching_orders = TradeOrder.query.filter_by(
            pair_id=new_order.pair_id,
            side=opposite_side,
            status='open'
        ).filter(TradeOrder.price <= new_order.price).order_by(TradeOrder.price).all()
    else:
        opposite_side = 'buy'
        # Find buy orders with price >= sell price
        matching_orders = TradeOrder.query.filter_by(
            pair_id=new_order.pair_id,
            side=opposite_side,
            status='open'
        ).filter(TradeOrder.price >= new_order.price).order_by(desc(TradeOrder.price)).all()
    
    remaining_amount = new_order.amount
    
    for match_order in matching_orders:
        if remaining_amount <= 0:
            break
        
        # Calculate trade amount
        trade_amount = min(remaining_amount, match_order.remaining_amount)
        
        # Execute trade at match_order price (price-time priority)
        trade = Trade(
            pair_id=new_order.pair_id,
            buyer_id=new_order.user_id if new_order.side == 'buy' else match_order.user_id,
            seller_id=match_order.user_id if new_order.side == 'buy' else new_order.user_id,
            price=match_order.price,
            volume=trade_amount,
            status='completed'
        )
        db.session.add(trade)
        
        # Update order statuses
        match_order.remaining_amount -= trade_amount
        if match_order.remaining_amount <= 0:
            match_order.status = 'filled'
        
        remaining_amount -= trade_amount
        
        # Update new order
        new_order.remaining_amount = remaining_amount
        if remaining_amount <= 0:
            new_order.status = 'filled'
    
    db.session.commit()
    return new_order.status == 'filled'

@trading_bp.route('/order/cancel/<uuid:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an open order"""
    order = TradeOrder.query.get_or_404(order_id)
    
    # Check ownership
    if order.user_id != current_user.id:
        flash('You are not authorized to cancel this order.', 'error')
        return redirect(url_for('trading.wallet'))
    
    if order.status != 'open':
        flash('This order cannot be cancelled.', 'warning')
        return redirect(url_for('trading.wallet'))
    
    order.status = 'cancelled'
    db.session.commit()
    
    flash('Order cancelled successfully.', 'success')
    return redirect(url_for('trading.wallet'))

# --- Admin Routes (Simplified) ---

@trading_bp.route('/admin/create-pair', methods=['GET', 'POST'])
@login_required
def create_pair():
    """Create a new trading pair (admin only)"""
    # In production, add admin role check
    if request.method == 'POST':
        base_currency = request.form.get('base_currency', '').upper()
        quote_currency = request.form.get('quote_currency', '').upper()
        symbol = f"{base_currency}/{quote_currency}"
        
        pair = TradingPair(
            base_currency=base_currency,
            quote_currency=quote_currency,
            symbol=symbol,
            tick_size=Decimal('0.01'),
            min_order_size=Decimal('0.001'),
            status='active'
        )
        db.session.add(pair)
        db.session.commit()
        
        flash(f'Trading pair {symbol} created successfully.', 'success')
        return redirect(url_for('trading.market'))
    
    return render_template('trading/create_pair.html')
