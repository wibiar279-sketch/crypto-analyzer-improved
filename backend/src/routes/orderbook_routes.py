"""
Order Book Routes
API endpoints for order book data
"""
from flask import Blueprint, jsonify, request
from ..services.orderbook_service import orderbook_service
import logging

logger = logging.getLogger(__name__)

orderbook_bp = Blueprint('orderbook', __name__)

@orderbook_bp.route('/order-books', methods=['GET'])
def get_order_books():
    """
    Get cached order books for all pairs
    Returns immediately from cache (updated every 5 minutes in background)
    """
    try:
        # Get cached data (no async needed, just return cache)
        cached_data = orderbook_service.cache
        
        if not cached_data:
            return jsonify({
                'success': False,
                'message': 'Order book data not yet available. Please wait for initial fetch to complete.',
                'data': {}
            }), 503
        
        # Get specific pairs if requested
        pairs_param = request.args.get('pairs')
        if pairs_param:
            requested_pairs = [p.strip().lower() for p in pairs_param.split(',')]
            filtered_data = {pair: cached_data.get(pair, orderbook_service._empty_order_book()) 
                           for pair in requested_pairs}
        else:
            filtered_data = cached_data
        
        return jsonify({
            'success': True,
            'total_pairs': len(filtered_data),
            'cache_timestamp': orderbook_service.cache_timestamp.isoformat() if orderbook_service.cache_timestamp else None,
            'data': filtered_data
        })
    except Exception as e:
        logger.error(f"Error in get_order_books: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@orderbook_bp.route('/order-books/<pair_id>', methods=['GET'])
def get_single_order_book(pair_id: str):
    """Get cached order book for a single pair"""
    try:
        cached_data = orderbook_service.cache
        
        if not cached_data:
            return jsonify({
                'success': False,
                'message': 'Order book data not yet available.'
            }), 503
        
        pair_data = cached_data.get(pair_id.lower())
        if pair_data:
            return jsonify({
                'success': True,
                'data': pair_data,
                'pair_id': pair_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Order book not found for this pair'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_single_order_book: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
