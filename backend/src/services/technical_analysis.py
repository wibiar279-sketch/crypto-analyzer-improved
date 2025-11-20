"""
Technical analysis service using TA-Lib indicators.
"""
import numpy as np
from typing import Dict, List, Optional
from flask import current_app

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    # Note: TA-Lib not available. Technical analysis will be limited.


class TechnicalAnalysisService:
    """Service for calculating technical indicators"""
    
    def __init__(self):
        self.talib_available = TALIB_AVAILABLE
    
    def _prepare_data(self, ohlcv_data: List[Dict]) -> Dict[str, np.ndarray]:
        """
        Prepare OHLCV data for analysis.
        
        Args:
            ohlcv_data: List of OHLCV dictionaries
            
        Returns:
            Dictionary with numpy arrays for each field
        """
        if not ohlcv_data:
            return {
                'open': np.array([]),
                'high': np.array([]),
                'low': np.array([]),
                'close': np.array([]),
                'volume': np.array([])
            }
        
        return {
            'open': np.array([float(d.get('open', 0)) for d in ohlcv_data]),
            'high': np.array([float(d.get('high', 0)) for d in ohlcv_data]),
            'low': np.array([float(d.get('low', 0)) for d in ohlcv_data]),
            'close': np.array([float(d.get('close', 0)) for d in ohlcv_data]),
            'volume': np.array([float(d.get('volume', 0)) for d in ohlcv_data])
        }
    
    def calculate_rsi(self, close: np.ndarray, period: int = 14) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index).
        
        Args:
            close: Close prices
            period: RSI period
            
        Returns:
            Current RSI value or None
        """
        if not self.talib_available or len(close) < period:
            return None
        
        try:
            rsi = talib.RSI(close, timeperiod=period)
            return float(rsi[-1]) if not np.isnan(rsi[-1]) else None
        except Exception as e:
            current_app.logger.error(f"RSI calculation error: {e}")
            return None
    
    def calculate_macd(self, close: np.ndarray) -> Optional[Dict]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            close: Close prices
            
        Returns:
            Dictionary with MACD, signal, and histogram values
        """
        if not self.talib_available or len(close) < 26:
            return None
        
        try:
            macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            return {
                'macd': float(macd[-1]) if not np.isnan(macd[-1]) else None,
                'signal': float(signal[-1]) if not np.isnan(signal[-1]) else None,
                'histogram': float(hist[-1]) if not np.isnan(hist[-1]) else None
            }
        except Exception as e:
            current_app.logger.error(f"MACD calculation error: {e}")
            return None
    
    def calculate_moving_averages(self, close: np.ndarray) -> Dict:
        """
        Calculate various moving averages.
        
        Args:
            close: Close prices
            
        Returns:
            Dictionary with moving average values
        """
        result = {}
        
        if not self.talib_available:
            return result
        
        try:
            # SMA
            for period in [7, 25, 99]:
                if len(close) >= period:
                    sma = talib.SMA(close, timeperiod=period)
                    result[f'sma_{period}'] = float(sma[-1]) if not np.isnan(sma[-1]) else None
            
            # EMA
            for period in [12, 26]:
                if len(close) >= period:
                    ema = talib.EMA(close, timeperiod=period)
                    result[f'ema_{period}'] = float(ema[-1]) if not np.isnan(ema[-1]) else None
            
        except Exception as e:
            current_app.logger.error(f"Moving averages calculation error: {e}")
        
        return result
    
    def calculate_bollinger_bands(self, close: np.ndarray, period: int = 20) -> Optional[Dict]:
        """
        Calculate Bollinger Bands.
        
        Args:
            close: Close prices
            period: BB period
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        if not self.talib_available or len(close) < period:
            return None
        
        try:
            upper, middle, lower = talib.BBANDS(close, timeperiod=period)
            return {
                'upper': float(upper[-1]) if not np.isnan(upper[-1]) else None,
                'middle': float(middle[-1]) if not np.isnan(middle[-1]) else None,
                'lower': float(lower[-1]) if not np.isnan(lower[-1]) else None
            }
        except Exception as e:
            current_app.logger.error(f"Bollinger Bands calculation error: {e}")
            return None
    
    def calculate_volume_analysis(self, volume: np.ndarray) -> Dict:
        """
        Calculate volume-based indicators.
        
        Args:
            volume: Volume data
            
        Returns:
            Dictionary with volume analysis
        """
        if len(volume) < 2:
            return {}
        
        try:
            current_volume = volume[-1]
            avg_volume_20 = np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume)
            
            return {
                'current_volume': float(current_volume),
                'avg_volume_20': float(avg_volume_20),
                'volume_ratio': float(current_volume / avg_volume_20) if avg_volume_20 > 0 else 0,
                'volume_trend': 'increasing' if current_volume > avg_volume_20 else 'decreasing'
            }
        except Exception as e:
            current_app.logger.error(f"Volume analysis error: {e}")
            return {}
    
    def analyze(self, ohlcv_data: List[Dict], current_price: float) -> Dict:
        """
        Perform complete technical analysis.
        
        Args:
            ohlcv_data: Historical OHLCV data
            current_price: Current price
            
        Returns:
            Dictionary with all technical indicators and analysis
        """
        if not ohlcv_data:
            return {'error': 'No data available for analysis'}
        
        # Prepare data
        data = self._prepare_data(ohlcv_data)
        close = data['close']
        volume = data['volume']
        
        # Calculate indicators
        analysis = {
            'current_price': current_price,
            'rsi': self.calculate_rsi(close),
            'macd': self.calculate_macd(close),
            'moving_averages': self.calculate_moving_averages(close),
            'bollinger_bands': self.calculate_bollinger_bands(close),
            'volume_analysis': self.calculate_volume_analysis(volume)
        }
        
        # Generate signals
        analysis['signals'] = self._generate_signals(analysis)
        
        # Calculate technical score
        analysis['technical_score'] = self._calculate_technical_score(analysis)
        
        return analysis
    
    def _generate_signals(self, analysis: Dict) -> Dict:
        """
        Generate buy/sell signals from indicators.
        
        Args:
            analysis: Technical analysis data
            
        Returns:
            Dictionary with signals
        """
        signals = {
            'rsi_signal': 'neutral',
            'macd_signal': 'neutral',
            'ma_signal': 'neutral',
            'bb_signal': 'neutral'
        }
        
        # RSI signals
        rsi = analysis.get('rsi')
        if rsi:
            if rsi < 30:
                signals['rsi_signal'] = 'oversold'
            elif rsi > 70:
                signals['rsi_signal'] = 'overbought'
        
        # MACD signals
        macd_data = analysis.get('macd')
        if macd_data and macd_data.get('macd') and macd_data.get('signal'):
            if macd_data['macd'] > macd_data['signal']:
                signals['macd_signal'] = 'bullish'
            else:
                signals['macd_signal'] = 'bearish'
        
        # Moving average signals
        ma_data = analysis.get('moving_averages', {})
        current_price = analysis.get('current_price')
        if current_price and ma_data.get('sma_25'):
            if current_price > ma_data['sma_25']:
                signals['ma_signal'] = 'bullish'
            else:
                signals['ma_signal'] = 'bearish'
        
        # Bollinger Bands signals
        bb_data = analysis.get('bollinger_bands')
        if current_price and bb_data:
            if bb_data.get('lower') and current_price < bb_data['lower']:
                signals['bb_signal'] = 'oversold'
            elif bb_data.get('upper') and current_price > bb_data['upper']:
                signals['bb_signal'] = 'overbought'
        
        return signals
    
    def _calculate_technical_score(self, analysis: Dict) -> float:
        """
        Calculate overall technical score (0-40).
        
        Args:
            analysis: Technical analysis data
            
        Returns:
            Technical score
        """
        score = 20.0  # Start at neutral
        signals = analysis.get('signals', {})
        
        # RSI scoring (±5 points)
        rsi_signal = signals.get('rsi_signal')
        if rsi_signal == 'oversold':
            score += 5
        elif rsi_signal == 'overbought':
            score -= 5
        
        # MACD scoring (±5 points)
        macd_signal = signals.get('macd_signal')
        if macd_signal == 'bullish':
            score += 5
        elif macd_signal == 'bearish':
            score -= 5
        
        # MA scoring (±5 points)
        ma_signal = signals.get('ma_signal')
        if ma_signal == 'bullish':
            score += 5
        elif ma_signal == 'bearish':
            score -= 5
        
        # BB scoring (±5 points)
        bb_signal = signals.get('bb_signal')
        if bb_signal == 'oversold':
            score += 5
        elif bb_signal == 'overbought':
            score -= 5
        
        # Clamp to 0-40 range
        return max(0, min(40, score))


# Global service instance
_technical_service = None


def get_technical_service() -> TechnicalAnalysisService:
    """
    Get or create technical analysis service instance.
    
    Returns:
        TechnicalAnalysisService instance
    """
    global _technical_service
    
    if _technical_service is None:
        _technical_service = TechnicalAnalysisService()
    
    return _technical_service
