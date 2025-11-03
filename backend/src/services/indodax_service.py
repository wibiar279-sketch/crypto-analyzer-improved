"""
Indodax API integration service with rate limiting and error handling.
"""
import time
import requests
from typing import Dict, List, Optional
from flask import current_app
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class IndodaxAPIError(Exception):
    """Custom exception for Indodax API errors"""
    pass


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0])
            if sleep_time > 0:
                current_app.logger.debug(f"Rate limit reached, waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
                self.calls = []
        
        # Record this call
        self.calls.append(time.time())


class IndodaxService:
    """Service for interacting with Indodax API"""
    
    def __init__(self, base_url: str = None, rate_limit: int = 10):
        """
        Initialize Indodax service.
        
        Args:
            base_url: Base URL for Indodax API
            rate_limit: Maximum API calls per minute
        """
        self.base_url = base_url or current_app.config.get(
            'INDODAX_API_URL',
            'https://indodax.com/api'
        )
        self.rate_limiter = RateLimiter(max_calls=rate_limit, time_window=60)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry logic.
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set timeout
        session.timeout = 10
        
        return session
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with error handling and rate limiting.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            IndodaxAPIError: If request fails
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            current_app.logger.debug(f"Requesting: {url}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.Timeout:
            current_app.logger.error(f"Timeout requesting {url}")
            raise IndodaxAPIError("Request timeout")
        
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error: {e}")
            raise IndodaxAPIError(f"API request failed: {str(e)}")
        
        except ValueError as e:
            current_app.logger.error(f"JSON decode error: {e}")
            raise IndodaxAPIError("Invalid JSON response")
    
    def get_pairs(self) -> List[Dict]:
        """
        Get all trading pairs.
        
        Returns:
            List of trading pairs
        """
        try:
            data = self._make_request('pairs')
            return data if isinstance(data, list) else []
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching pairs: {e}")
            return []
    
    def get_summaries(self) -> Dict:
        """
        Get market summaries for all pairs.
        
        Returns:
            Dictionary of market summaries
        """
        try:
            data = self._make_request('summaries')
            return data.get('tickers', {}) if isinstance(data, dict) else {}
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching summaries: {e}")
            return {}
    
    def get_ticker_all(self) -> Dict:
        """
        Get all tickers.
        
        Returns:
            Dictionary of all tickers
        """
        try:
            data = self._make_request('tickers')
            return data.get('tickers', {}) if isinstance(data, dict) else {}
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching tickers: {e}")
            return {}
    
    def get_ticker(self, pair_id: str) -> Optional[Dict]:
        """
        Get ticker for specific pair.
        
        Args:
            pair_id: Trading pair ID
            
        Returns:
            Ticker data or None if not found
        """
        try:
            data = self._make_request(f'ticker/{pair_id}')
            return data.get('ticker') if isinstance(data, dict) else None
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching ticker for {pair_id}: {e}")
            return None
    
    def get_depth(self, pair_id: str) -> Optional[Dict]:
        """
        Get order book depth for specific pair.
        
        Args:
            pair_id: Trading pair ID
            
        Returns:
            Order book data or None if not found
        """
        try:
            data = self._make_request(f'depth/{pair_id}')
            return data if isinstance(data, dict) else None
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching depth for {pair_id}: {e}")
            return None
    
    def get_trades(self, pair_id: str) -> List[Dict]:
        """
        Get recent trades for specific pair.
        
        Args:
            pair_id: Trading pair ID
            
        Returns:
            List of recent trades
        """
        try:
            data = self._make_request(f'trades/{pair_id}')
            return data if isinstance(data, list) else []
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching trades for {pair_id}: {e}")
            return []
    
    def get_ohlc(self, pair_id: str, timeframe: str = '1d') -> List[Dict]:
        """
        Get OHLC (candlestick) data.
        
        Args:
            pair_id: Trading pair ID
            timeframe: Timeframe (e.g., '1h', '1d')
            
        Returns:
            List of OHLC data
        """
        try:
            # Note: Adjust endpoint based on actual Indodax API
            data = self._make_request(f'chart/{pair_id}/{timeframe}')
            return data if isinstance(data, list) else []
        except IndodaxAPIError as e:
            current_app.logger.error(f"Error fetching OHLC for {pair_id}: {e}")
            return []


# Global service instance
_indodax_service = None


def get_indodax_service() -> IndodaxService:
    """
    Get or create Indodax service instance.
    
    Returns:
        IndodaxService instance
    """
    global _indodax_service
    
    if _indodax_service is None:
        rate_limit = current_app.config.get('INDODAX_RATE_LIMIT', 10)
        _indodax_service = IndodaxService(rate_limit=rate_limit)
    
    return _indodax_service
