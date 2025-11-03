"""
Database models for crypto analyzer.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()


class PriceHistory(db.Model):
    """Store historical price data"""
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    pair_id = db.Column(db.String(20), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    
    # OHLCV data
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_pair_timestamp', 'pair_id', 'timestamp'),
    )
    
    def to_dict(self):
        return {
            'pair_id': self.pair_id,
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        }


class AnalysisResult(db.Model):
    """Store analysis results for caching and tracking"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    pair_id = db.Column(db.String(20), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Scores
    total_score = db.Column(db.Float)
    technical_score = db.Column(db.Float)
    bandarmology_score = db.Column(db.Float)
    momentum_score = db.Column(db.Float)
    
    # Recommendation
    action = db.Column(db.String(20))  # BUY, SELL, HOLD, etc.
    confidence = db.Column(db.String(10))  # HIGH, MEDIUM, LOW
    
    # Technical indicators (stored as JSON)
    technical_data = db.Column(db.JSON)
    bandarmology_data = db.Column(db.JSON)
    
    # Market data snapshot
    price = db.Column(db.Float)
    volume_24h = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_pair_timestamp_analysis', 'pair_id', 'timestamp'),
    )
    
    def to_dict(self):
        return {
            'pair_id': self.pair_id,
            'timestamp': self.timestamp.isoformat(),
            'total_score': self.total_score,
            'technical_score': self.technical_score,
            'bandarmology_score': self.bandarmology_score,
            'momentum_score': self.momentum_score,
            'action': self.action,
            'confidence': self.confidence,
            'price': self.price,
            'volume_24h': self.volume_24h,
        }


class TradingPair(db.Model):
    """Store trading pair metadata"""
    __tablename__ = 'trading_pairs'
    
    id = db.Column(db.Integer, primary_key=True)
    pair_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    base_currency = db.Column(db.String(10), nullable=False)
    quoted_currency = db.Column(db.String(10), nullable=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    total_analyses = db.Column(db.Integer, default=0)
    last_analysis_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'pair_id': self.pair_id,
            'base_currency': self.base_currency,
            'quoted_currency': self.quoted_currency,
            'is_active': self.is_active,
            'total_analyses': self.total_analyses,
            'last_analysis_at': self.last_analysis_at.isoformat() if self.last_analysis_at else None,
        }


class APILog(db.Model):
    """Log API requests for monitoring and debugging"""
    __tablename__ = 'api_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Request info
    method = db.Column(db.String(10))
    endpoint = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    # Response info
    status_code = db.Column(db.Integer)
    response_time_ms = db.Column(db.Float)
    
    # Error tracking
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'method': self.method,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
        }
