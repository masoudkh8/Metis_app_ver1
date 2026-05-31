"""
Trading Engine Service - Core Matching Logic
Handles order matching, trade execution, and market data updates.
"""
import time
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import heapq

from models import db, TradeOrder, Trade, TradingPair, MarketData, TradingWallet, WalletTransaction
from models.exhibition_trading_models import OrderType, OrderSide, OrderStatus


class OrderBook:
    """Manages buy and sell orders for a specific trading pair."""
    
    def __init__(self, pair_id: str):
        self.pair_id = pair_id
        # Max heap for bids (buy orders) - negate price for max heap behavior
        self.bids: List[Tuple[Decimal, str, dict]] = []  # (price, order_id, order_data)
        # Min heap for asks (sell orders)
        self.asks: List[Tuple[Decimal, str, dict]] = []
        self.order_map: Dict[str, dict] = {}  # order_id -> order_data
        
    def add_order(self, order: TradeOrder) -> bool:
        """Add an order to the book."""
        order_data = {
            'id': str(order.id),
            'price': order.price,
            'quantity': order.quantity,
            'filled_quantity': Decimal('0'),
            'side': order.side,
            'type': order.type,
            'user_id': str(order.user_id),
            'created_at': order.created_at
        }
        
        self.order_map[str(order.id)] = order_data
        
        if order.side == OrderSide.BUY:
            # Use negative price for max heap (highest bid first)
            heapq.heappush(self.bids, (-order.price, str(order.id), order_data))
        else:
            heapq.heappush(self.asks, (order.price, str(order.id), order_data))
            
        return True
    
    def remove_order(self, order_id: str):
        """Remove/cancel an order from the book."""
        if order_id in self.order_map:
            del self.order_map[order_id]
        # Note: Lazy removal - orders are filtered out during matching
    
    def get_best_bid(self) -> Optional[Decimal]:
        """Get the highest bid price."""
        while self.bids:
            price, order_id, _ = self.bids[0]
            if order_id in self.order_map:
                return -price  # Return positive price
            else:
                heapq.heappop(self.bids)  # Remove stale order
        return None
    
    def get_best_ask(self) -> Optional[Decimal]:
        """Get the lowest ask price."""
        while self.asks:
            price, order_id, _ = self.asks[0]
            if order_id in self.order_map:
                return price
            else:
                heapq.heappop(self.asks)  # Remove stale order
        return None
    
    def get_spread(self) -> Optional[Decimal]:
        """Calculate bid-ask spread."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask - best_bid
        return None
    
    def get_depth(self, levels: int = 10) -> Dict:
        """Get order book depth for visualization."""
        bids_depth = []
        asks_depth = []
        
        # Aggregate bids by price
        bid_prices = defaultdict(int)
        for price, order_id, data in self.bids:
            if order_id in self.order_map:
                available_qty = data['quantity'] - data['filled_quantity']
                if available_qty > 0:
                    bid_prices[-price] += float(available_qty)
        
        # Aggregate asks by price
        ask_prices = defaultdict(int)
        for price, order_id, data in self.asks:
            if order_id in self.order_map:
                available_qty = data['quantity'] - data['filled_quantity']
                if available_qty > 0:
                    ask_prices[price] += float(available_qty)
        
        # Get top N levels
        sorted_bids = sorted(bid_prices.items(), key=lambda x: x[0], reverse=True)[:levels]
        sorted_asks = sorted(ask_prices.items())[:levels]
        
        return {
            'bids': [{'price': p, 'quantity': q} for p, q in sorted_bids],
            'asks': [{'price': p, 'quantity': q} for p, q in sorted_asks]
        }


class MatchingEngine:
    """Core matching engine for executing trades."""
    
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.trade_history: List[dict] = []
        
    def get_or_create_book(self, pair_id: str) -> OrderBook:
        """Get or create an order book for a trading pair."""
        if pair_id not in self.order_books:
            self.order_books[pair_id] = OrderBook(pair_id)
        return self.order_books[pair_id]
    
    def match_order(self, order: TradeOrder) -> List[Trade]:
        """Attempt to match an incoming order against the order book."""
        book = self.get_or_create_book(str(order.pair_id))
        executed_trades = []
        
        # Determine opposite side and appropriate book side
        if order.side == OrderSide.BUY:
            opposite_book = book.asks
            is_maker_buy = False
        else:
            opposite_book = book.bids
            is_maker_buy = True
        
        remaining_quantity = order.quantity
        
        while remaining_quantity > 0 and opposite_book:
            # Get best opposing order
            if order.side == OrderSide.BUY:
                best_price = book.get_best_ask()
                if best_price is None or (order.type == OrderType.LIMIT and order.price < best_price):
                    break
                    
                # Find the actual order with best price
                while book.asks:
                    price, order_id, maker_order = book.asks[0]
                    if order_id not in book.order_map:
                        heapq.heappop(book.asks)
                        continue
                    
                    available_qty = maker_order['quantity'] - maker_order['filled_quantity']
                    if available_qty <= 0:
                        heapq.heappop(book.asks)
                        continue
                    
                    # Check price compatibility
                    if order.type == OrderType.LIMIT and order.price < price:
                        break
                    
                    # Execute trade
                    trade_qty = min(remaining_quantity, available_qty)
                    trade_price = price  # Maker's price
                    
                    trade = self._execute_trade(
                        taker_order=order,
                        maker_order_data=maker_order,
                        quantity=trade_qty,
                        price=trade_price,
                        is_maker_buy=is_maker_buy
                    )
                    
                    if trade:
                        executed_trades.append(trade)
                        remaining_quantity -= trade_qty
                        maker_order['filled_quantity'] += trade_qty
                        
                        # Update order status
                        if maker_order['filled_quantity'] >= maker_order['quantity']:
                            self._update_order_status(maker_order['id'], OrderStatus.FILLED)
                            heapq.heappop(book.asks)
                        else:
                            self._update_order_status(maker_order['id'], OrderStatus.PARTIALLY_FILLED)
                            
                        # Update taker order
                        order.filled_quantity = order.quantity - remaining_quantity
                        if remaining_quantity <= 0:
                            order.status = OrderStatus.FILLED
                        else:
                            order.status = OrderStatus.PARTIALLY_FILLED
                    break
                    
            else:  # SELL order
                best_price = book.get_best_bid()
                if best_price is None or (order.type == OrderType.LIMIT and order.price > best_price):
                    break
                
                while book.bids:
                    neg_price, order_id, maker_order = book.bids[0]
                    if order_id not in book.order_map:
                        heapq.heappop(book.bids)
                        continue
                    
                    available_qty = maker_order['quantity'] - maker_order['filled_quantity']
                    if available_qty <= 0:
                        heapq.heappop(book.bids)
                        continue
                    
                    price = -neg_price
                    if order.type == OrderType.LIMIT and order.price > price:
                        break
                    
                    trade_qty = min(remaining_quantity, available_qty)
                    trade_price = price
                    
                    trade = self._execute_trade(
                        taker_order=order,
                        maker_order_data=maker_order,
                        quantity=trade_qty,
                        price=trade_price,
                        is_maker_buy=True
                    )
                    
                    if trade:
                        executed_trades.append(trade)
                        remaining_quantity -= trade_qty
                        maker_order['filled_quantity'] += trade_qty
                        
                        if maker_order['filled_quantity'] >= maker_order['quantity']:
                            self._update_order_status(maker_order['id'], OrderStatus.FILLED)
                            heapq.heappop(book.bids)
                        else:
                            self._update_order_status(maker_order['id'], OrderStatus.PARTIALLY_FILLED)
                        
                        order.filled_quantity = order.quantity - remaining_quantity
                        if remaining_quantity <= 0:
                            order.status = OrderStatus.FILLED
                        else:
                            order.status = OrderStatus.PARTIALLY_FILLED
                    break
        
        # If order still has remaining quantity and it's a limit order, add to book
        if remaining_quantity > 0 and order.type == OrderType.LIMIT:
            order.quantity = remaining_quantity
            order.filled_quantity = order.quantity - remaining_quantity
            if order.status != OrderStatus.PARTIALLY_FILLED:
                order.status = OrderStatus.PENDING
            book.add_order(order)
        elif remaining_quantity > 0 and order.type == OrderType.MARKET:
            # Market order couldn't be fully filled
            order.status = OrderStatus.CANCELLED
            
        return executed_trades
    
    def _execute_trade(self, taker_order: TradeOrder, maker_order_data: dict, 
                      quantity: Decimal, price: Decimal, is_maker_buy: bool) -> Optional[Trade]:
        """Execute a trade between taker and maker."""
        try:
            trade_id = uuid.uuid4()
            timestamp = datetime.utcnow()
            
            # Calculate fees (simplified - 0.1% for both sides)
            fee_rate = Decimal('0.001')
            trade_value = quantity * price
            
            maker_fee = trade_value * fee_rate
            taker_fee = trade_value * fee_rate
            
            trade = Trade(
                id=trade_id,
                pair_id=taker_order.pair_id,
                buyer_id=maker_order_data['user_id'] if is_maker_buy else taker_order.user_id,
                seller_id=taker_order.user_id if is_maker_buy else maker_order_data['user_id'],
                price=price,
                quantity=quantity,
                total_value=trade_value,
                maker_fee=maker_fee,
                taker_fee=taker_fee,
                maker_order_id=maker_order_data['id'],
                taker_order_id=str(taker_order.id),
                executed_at=timestamp
            )
            
            # Update wallets
            self._update_wallets(trade, is_maker_buy)
            
            # Record trade
            db.session.add(trade)
            
            # Update market data
            self._update_market_data(taker_order.pair_id, price, quantity, timestamp)
            
            return trade
            
        except Exception as e:
            print(f"Error executing trade: {e}")
            db.session.rollback()
            return None
    
    def _update_wallets(self, trade: Trade, is_maker_buy: bool):
        """Update user wallets after trade execution."""
        # Implementation would handle actual wallet balance updates
        # For now, just create transaction records
        pass
    
    def _update_order_status(self, order_id: str, status: OrderStatus):
        """Update order status in database."""
        order = db.session.get(TradeOrder, order_id)
        if order:
            order.status = status
            db.session.commit()
    
    def _update_market_data(self, pair_id: str, price: Decimal, quantity: Decimal, timestamp: datetime):
        """Update market data for charts and tickers."""
        try:
            # Get or create today's market data
            today = timestamp.date()
            market_data = MarketData.query.filter_by(
                pair_id=pair_id,
                timestamp=datetime.combine(today, datetime.min.time())
            ).first()
            
            if not market_data:
                # Create new daily record
                pair = db.session.get(TradingPair, pair_id)
                if not pair:
                    return
                    
                market_data = MarketData(
                    pair_id=pair_id,
                    open_price=price,
                    high_price=price,
                    low_price=price,
                    close_price=price,
                    volume=quantity,
                    quote_volume=price * quantity,
                    trade_count=1,
                    timestamp=datetime.combine(today, datetime.min.time())
                )
                db.session.add(market_data)
            else:
                # Update existing record
                market_data.high_price = max(market_data.high_price, price)
                market_data.low_price = min(market_data.low_price, price)
                market_data.close_price = price
                market_data.volume += quantity
                market_data.quote_volume += price * quantity
                market_data.trade_count += 1
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error updating market data: {e}")
            db.session.rollback()


# Global matching engine instance
matching_engine = MatchingEngine()


def process_order(order_id: str):
    """Process a single order through the matching engine."""
    order = db.session.get(TradeOrder, order_id)
    if not order or order.status != OrderStatus.PENDING:
        return []
    
    trades = matching_engine.match_order(order)
    
    # Commit all changes
    if trades:
        db.session.commit()
    
    return trades


def cancel_order(order_id: str) -> bool:
    """Cancel an order."""
    order = db.session.get(TradeOrder, order_id)
    if not order or order.status not in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
        return False
    
    order.status = OrderStatus.CANCELLED
    book = matching_engine.get_or_create_book(str(order.pair_id))
    book.remove_order(order_id)
    
    db.session.commit()
    return True


def get_order_book_depth(pair_id: str, levels: int = 10) -> dict:
    """Get order book depth for a trading pair."""
    book = matching_engine.get_or_create_book(pair_id)
    return book.get_depth(levels)


def get_market_ticker(pair_id: str) -> Optional[dict]:
    """Get current market ticker for a trading pair."""
    today = datetime.utcnow().date()
    market_data = MarketData.query.filter_by(
        pair_id=pair_id,
        timestamp=datetime.combine(today, datetime.min.time())
    ).first()
    
    if not market_data:
        return None
    
    book = matching_engine.get_or_create_book(pair_id)
    
    return {
        'pair_id': pair_id,
        'last_price': float(market_data.close_price),
        'high_24h': float(market_data.high_price),
        'low_24h': float(market_data.low_price),
        'volume': float(market_data.volume),
        'quote_volume': float(market_data.quote_volume),
        'bid': float(book.get_best_bid()) if book.get_best_bid() else None,
        'ask': float(book.get_best_ask()) if book.get_best_ask() else None,
        'spread': float(book.get_spread()) if book.get_spread() else None,
        'timestamp': market_data.timestamp.isoformat()
    }
