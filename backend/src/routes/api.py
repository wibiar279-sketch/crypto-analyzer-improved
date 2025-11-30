"""
API routes for crypto analyzer.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..services import (
    get_indodax_service,
    get_technical_service,
    get_bandarmology_service,
    get_recommendation_service,
    IndodaxAPIError
)
from ..utils import (
    cached,
    validate_pair_id,
    ValidationError,
    RequestLogger
)
# Models will be imported when needed to avoid initialization errors
# from ..models import db, AnalysisResult, TradingPair

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Rate limiter will be initialized in main.py
limiter = None


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'crypto-analyzer-api',
        'version': '2.0.0'
    })


@api_bp.route('/pairs', methods=['GET'])
@cached(ttl=300, key_prefix='pairs')
def get_pairs():
    """Get all trading pairs"""
    try:
        with RequestLogger("Fetching trading pairs"):
            indodax = get_indodax_service()
            pairs = indodax.get_pairs()
            
            return jsonify({
                'success': True,
                'data': pairs,
                'count': len(pairs)
            })
    
    except IndodaxAPIError as e:
        current_app.logger.error(f"Indodax API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch trading pairs'
        }), 503
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@api_bp.route('/tickers', methods=['GET'])
def get_tickers():
    """Get all tickers with caching"""
    try:
        cache_ttl = current_app.config.get('CACHE_TTL_TICKER', 30)
        
        @cached(ttl=cache_ttl, key_prefix='tickers')
        def fetch_tickers():
            indodax = get_indodax_service()
            return indodax.get_ticker_all()
        
        with RequestLogger("Fetching all tickers"):
            tickers = fetch_tickers()
            
            return jsonify({
                'success': True,
                'data': tickers,
                'count': len(tickers) if tickers else 0
            })
    
    except IndodaxAPIError as e:
        return jsonify({'success': False, 'error': str(e)}), 503
    
    except Exception as e:
        current_app.logger.error(f"Error fetching tickers: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@api_bp.route('/ticker/<pair_id>', methods=['GET'])
def get_ticker(pair_id):
    """Get ticker for specific pair"""
    try:
        pair_id = validate_pair_id(pair_id)
        cache_ttl = current_app.config.get('CACHE_TTL_TICKER', 30)
        
        @cached(ttl=cache_ttl, key_prefix=f'ticker:{pair_id}')
        def fetch_ticker():
            indodax = get_indodax_service()
            return indodax.get_ticker(pair_id)
        
        with RequestLogger(f"Fetching ticker for {pair_id}"):
            ticker = fetch_ticker()
            
            if not ticker:
                return jsonify({
                    'success': False,
                    'error': f'Ticker not found for {pair_id}'
                }), 404
            
            return jsonify({
                'success': True,
                'data': ticker
            })
    
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except IndodaxAPIError as e:
        return jsonify({'success': False, 'error': str(e)}), 503
    
    except Exception as e:
        current_app.logger.error(f"Error fetching ticker: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@api_bp.route('/depth/<pair_id>', methods=['GET'])
def get_depth(pair_id):
    """Get order book depth for specific pair"""
    try:
        pair_id = validate_pair_id(pair_id)
        cache_ttl = current_app.config.get('CACHE_TTL_DEPTH', 10)
        
        @cached(ttl=cache_ttl, key_prefix=f'depth:{pair_id}')
        def fetch_depth():
            indodax = get_indodax_service()
            return indodax.get_depth(pair_id)
        
        with RequestLogger(f"Fetching depth for {pair_id}"):
            depth = fetch_depth()
            
            if not depth:
                return jsonify({
                    'success': False,
                    'error': f'Depth data not found for {pair_id}'
                }), 404
            
            return jsonify({
                'success': True,
                'data': depth
            })
    
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except IndodaxAPIError as e:
        return jsonify({'success': False, 'error': str(e)}), 503
    
    except Exception as e:
        current_app.logger.error(f"Error fetching depth: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@api_bp.route('/analysis/<pair_id>', methods=['GET'])
def get_analysis(pair_id):
    """
    Get complete analysis for a trading pair.
    This is the main analysis endpoint that combines all services.
    """
    try:
        pair_id = validate_pair_id(pair_id)
        
        with RequestLogger(f"Complete analysis for {pair_id}"):
            # Get services
            indodax = get_indodax_service()
            technical = get_technical_service()
            bandarmology = get_bandarmology_service()
            recommendation = get_recommendation_service()
            
            # Fetch market data
            ticker = indodax.get_ticker(pair_id)
            if not ticker:
                return jsonify({
                    'success': False,
                    'error': f'Ticker not found for {pair_id}'
                }), 404
            
            depth = indodax.get_depth(pair_id)
            if not depth:
                return jsonify({
                    'success': False,
                    'error': f'Order book not found for {pair_id}'
                }), 404
            
            # Get historical data (simulated for now - in production, fetch from DB)
            ohlcv_data = []  # TODO: Fetch from database
            current_price = float(ticker.get('last', 0))
            
            # Perform analyses
            technical_analysis = technical.analyze(ohlcv_data, current_price)
            bandarmology_analysis = bandarmology.analyze_order_book(depth)
            
            # Generate recommendation
            market_data = {
                'price_change_24h': float(ticker.get('price_change_24h', 0)),
                'volume_24h': float(ticker.get('vol_idr', 0)),
                'avg_volume': float(ticker.get('vol_idr', 0))  # TODO: Calculate from history
            }
            
            rec = recommendation.generate_recommendation(
                technical_analysis,
                bandarmology_analysis,
                market_data
            )
            
            # Save to database (optional - will skip if models not available)
            try:
                from ..models import db, AnalysisResult, TradingPair
                
                analysis_record = AnalysisResult(
                    pair_id=pair_id,
                    total_score=rec['total_score'],
                    technical_score=rec['breakdown']['technical_score'],
                    bandarmology_score=rec['breakdown']['bandarmology_score'],
                    momentum_score=rec['breakdown']['momentum_score'],
                    action=rec['action'],
                    confidence=rec['confidence'],
                    technical_data=technical_analysis,
                    bandarmology_data=bandarmology_analysis,
                    price=current_price,
                    volume_24h=market_data['volume_24h']
                )
                db.session.add(analysis_record)
                
                # Update trading pair stats
                trading_pair = TradingPair.query.filter_by(pair_id=pair_id).first()
                if trading_pair:
                    trading_pair.total_analyses += 1
                    trading_pair.last_analysis_at = analysis_record.timestamp
                
                db.session.commit()
                current_app.logger.debug("Analysis saved to database")
            
            except Exception as e:
                current_app.logger.warning(f"Database save skipped: {e}")
                try:
                    from ..models import db
                    db.session.rollback()
                except:
                    pass
            
            # Prepare response
            result = {
                'success': True,
                'pair_id': pair_id,
                'recommendation': rec,
                'technical_analysis': technical_analysis,
                'bandarmology_analysis': bandarmology_analysis,
                'market_data': {
                    'ticker': ticker,
                    'current_price': current_price,
                    **market_data
                }
            }
            
            return jsonify(result)
    
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except IndodaxAPIError as e:
        return jsonify({'success': False, 'error': str(e)}), 503
    
    except Exception as e:
        current_app.logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@api_bp.route('/technical/<pair_id>', methods=['GET'])
def get_technical_analysis(pair_id):
    """Get technical analysis only"""
    try:
        pair_id = validate_pair_id(pair_id)
        
        with RequestLogger(f"Technical analysis for {pair_id}"):
            indodax = get_indodax_service()
            technical = get_technical_service()
            
            ticker = indodax.get_ticker(pair_id)
            if not ticker:
                return jsonify({'success': False, 'error': 'Ticker not found'}), 404
            
            current_price = float(ticker.get('last', 0))
            ohlcv_data = []  # TODO: Fetch from database
            
            analysis = technical.analyze(ohlcv_data, current_price)
            
            return jsonify({
                'success': True,
                'pair_id': pair_id,
                'data': analysis
            })
    
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        current_app.logger.error(f"Technical analysis error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@api_bp.route('/bandarmology/<pair_id>', methods=['GET'])
def get_bandarmology_analysis(pair_id):
    """Get bandarmology analysis only"""
    try:
        pair_id = validate_pair_id(pair_id)
        
        with RequestLogger(f"Bandarmology analysis for {pair_id}"):
            indodax = get_indodax_service()
            bandarmology = get_bandarmology_service()
            
            depth = indodax.get_depth(pair_id)
            if not depth:
                return jsonify({'success': False, 'error': 'Order book not found'}), 404
            
            analysis = bandarmology.analyze_order_book(depth)
            
            return jsonify({
                'success': True,
                'pair_id': pair_id,
                'data': analysis
            })
    
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        current_app.logger.error(f"Bandarmology analysis error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@api_bp.route('/history/<pair_id>', methods=['GET'])
def get_history(pair_id):
    """Get historical analysis data from database"""
    try:
        pair_id = validate_pair_id(pair_id)
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 1000)  # Max 1000 records
        
        with RequestLogger(f"Fetching history for {pair_id}"):
            try:
                from ..models import AnalysisResult
                
                results = AnalysisResult.query.filter_by(pair_id=pair_id)\
                    .order_by(AnalysisResult.timestamp.desc())\
                    .limit(limit)\
                    .all()
                
                return jsonify({
                    'success': True,
                    'pair_id': pair_id,
                    'data': [r.to_dict() for r in results],
                    'count': len(results)
                })
            
            except Exception as db_error:
                current_app.logger.warning(f"Database not available: {db_error}")
                return jsonify({
                    'success': False,
                    'error': 'Historical data not available',
                    'message': 'Database is not configured'
                }), 503
    
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        current_app.logger.error(f"History fetch error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405


@api_bp.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.'
    }), 429


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
