"""
Input validation utilities.
"""
import re
from typing import Any, List, Optional
from functools import wraps
from flask import request, jsonify


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_pair_id(pair_id: str) -> str:
    """
    Validate trading pair ID format.
    
    Args:
        pair_id: Trading pair ID (e.g., 'btcidr')
        
    Returns:
        Validated pair ID in lowercase
        
    Raises:
        ValidationError: If pair ID is invalid
    """
    if not pair_id:
        raise ValidationError("Pair ID is required")
    
    # Convert to lowercase
    pair_id = pair_id.lower().strip()
    
    # Check format (alphanumeric, 5-20 characters)
    if not re.match(r'^[a-z0-9]{5,20}$', pair_id):
        raise ValidationError(
            "Invalid pair ID format. Must be 5-20 alphanumeric characters"
        )
    
    return pair_id


def validate_timeframe(timeframe: str) -> str:
    """
    Validate timeframe parameter.
    
    Args:
        timeframe: Timeframe string (e.g., '1h', '1d', '1w')
        
    Returns:
        Validated timeframe
        
    Raises:
        ValidationError: If timeframe is invalid
    """
    valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    
    if timeframe not in valid_timeframes:
        raise ValidationError(
            f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"
        )
    
    return timeframe


def validate_limit(limit: Any, max_limit: int = 1000) -> int:
    """
    Validate limit parameter.
    
    Args:
        limit: Limit value
        max_limit: Maximum allowed limit
        
    Returns:
        Validated limit as integer
        
    Raises:
        ValidationError: If limit is invalid
    """
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        raise ValidationError("Limit must be an integer")
    
    if limit < 1:
        raise ValidationError("Limit must be at least 1")
    
    if limit > max_limit:
        raise ValidationError(f"Limit cannot exceed {max_limit}")
    
    return limit


def validate_request_args(required: List[str] = None, optional: List[str] = None):
    """
    Decorator to validate request arguments.
    
    Args:
        required: List of required argument names
        optional: List of optional argument names
    
    Example:
        @app.route('/api/ticker/<pair_id>')
        @validate_request_args(required=['pair_id'])
        def get_ticker(pair_id):
            return {'pair_id': pair_id}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate required arguments
            if required:
                for arg in required:
                    if arg not in kwargs and arg not in request.args:
                        return jsonify({
                            'error': f"Missing required parameter: {arg}"
                        }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def sanitize_string(value: str, max_length: int = 100) -> str:
    """
    Sanitize string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes and control characters
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Trim whitespace
    value = value.strip()
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_pagination(page: Any = 1, per_page: Any = 20, max_per_page: int = 100):
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        max_per_page: Maximum items per page
        
    Returns:
        Tuple of (page, per_page)
        
    Raises:
        ValidationError: If parameters are invalid
    """
    try:
        page = int(page)
        per_page = int(per_page)
    except (TypeError, ValueError):
        raise ValidationError("Page and per_page must be integers")
    
    if page < 1:
        raise ValidationError("Page must be at least 1")
    
    if per_page < 1:
        raise ValidationError("Per page must be at least 1")
    
    if per_page > max_per_page:
        raise ValidationError(f"Per page cannot exceed {max_per_page}")
    
    return page, per_page
