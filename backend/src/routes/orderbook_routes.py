"""
Order Book Routes
API endpoints for order book data with lazy loading and batch fetching
"""
from flask import Blueprint, jsonify, request, current_app
from ..services.orderbook_service import orderbook_service
import logging

logger = logging.getLogger(__name__)

orderbook_bp = Blueprint('orderbook', __name__)

@orderbook_bp.route('/order-books', methods=['GET'])
def get_order_books():
    """
    Get order books with lazy loading and caching
    - If pairs parameter provided: fetch only those pairs (batch mode)
    - If no pairs parameter: return all cached data
    - Cache each pair for 5 minutes
    """
    try:
        # Get specific pairs if requested
        pairs_param = request.args.get('pairs')
        
        if pairs_param:
            # Batch mode: fetch only requested pairs
            requested_pairs = [p.strip().lower() for p in pairs_param.split(',')]
            logger.info(f"Fetching order books for {len(requested_pairs)} pairs")
            
            # Fetch with caching (will use cache if available and fresh)
            result = orderbook_service.fetch_order_books(requested_pairs)
            
            return jsonify({
                'success': True,
                'total_pairs': len(result),
                'data': result
            })
        else:
            # Return all cached data
            cached_data = orderbook_service.cache
            
            if not cached_data:
                return jsonify({
                    'success': True,
                    'message': 'No cached data available. Please request specific pairs using ?pairs=btcidr,ethidr',
                    'total_pairs': 0,
                    'data': {}
                })
            
            return jsonify({
                'success': True,
                'total_pairs': len(cached_data),
                'cache_timestamp': orderbook_service.cache_timestamp.isoformat() if orderbook_service.cache_timestamp else None,
                'data': cached_data
            })
    except Exception as e:
        logger.error(f"Error in get_order_books: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@orderbook_bp.route('/order-books/<pair_id>', methods=['GET'])
def get_single_order_book(pair_id: str):
    """Get order book for a single pair with lazy loading"""
    try:
        # Fetch single pair (will use cache if available)
        result = orderbook_service.fetch_order_books([pair_id.lower()])
        
        pair_data = result.get(pair_id.lower())
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
        logger.error(f"Error in get_single_order_book: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
