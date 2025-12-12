"""
Order Book Routes
API endpoints for order book data
"""
from flask import Blueprint, jsonify, request
from ..services.orderbook_service import orderbook_service
import asyncio
import logging

logger = logging.getLogger(__name__)

orderbook_bp = Blueprint('orderbook', __name__)

@orderbook_bp.route('/order-books', methods=['GET'])
async def get_order_books():
    """
    Get order books for all trading pairs
    Query params:
    - pairs: comma-separated list of pair IDs (e.g., btcidr,ethidr)
    """
    try:
        # Get pairs from query param or use default list
        pairs_param = request.args.get('pairs', '')
        
        if pairs_param:
            pairs = [p.strip() for p in pairs_param.split(',') if p.strip()]
        else:
            # Default: fetch for common pairs
            # In production, this should come from the pairs endpoint
            pairs = [
                'btcidr', 'ethidr', 'usdtidr', 'bnbidr', 'xrpidr',
                'adaidr', 'dogidr', 'shibaidr', 'maticid', 'solidr'
            ]
        
        # Fetch order books
        order_books = await orderbook_service.get_order_books(pairs)
        
        return jsonify({
            'success': True,
            'data': order_books,
            'cached_at': orderbook_service.cache_timestamp.isoformat() if orderbook_service.cache_timestamp else None,
            'total_pairs': len(order_books)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_order_books: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orderbook_bp.route('/order-books/<pair_id>', methods=['GET'])
async def get_single_order_book(pair_id: str):
    """Get order book for a single pair"""
    try:
        order_books = await orderbook_service.get_order_books([pair_id])
        
        if pair_id in order_books:
            return jsonify({
                'success': True,
                'data': order_books[pair_id],
                'pair_id': pair_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Order book not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_single_order_book: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
