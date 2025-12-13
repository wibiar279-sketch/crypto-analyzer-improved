"""
Order Book Service
Fetches and caches order book data from Indodax API with lazy loading and batch fetching
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OrderBookService:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}  # pair -> order book data
        self.cache_timestamps: Dict[str, datetime] = {}  # pair -> timestamp
        self.cache_duration = timedelta(seconds=30)  # Cache for 30 seconds per pair
        self.cache_timestamp: Optional[datetime] = None  # Global cache timestamp for compatibility
        self.fetching_pairs = set()  # Track which pairs are currently being fetched
        
    def fetch_order_books(self, pairs: List[str]) -> Dict[str, Dict]:
        """
        Fetch order books for specific pairs with per-pair caching
        Uses cache if available and fresh (< 30 seconds old)
        """
        result = {}
        pairs_to_fetch = []
        
        # Check cache for each pair
        for pair in pairs:
            pair_lower = pair.lower()
            if self._is_pair_cache_valid(pair_lower):
                # Use cached data
                result[pair_lower] = self.cache.get(pair_lower, self._empty_order_book())
            else:
                # Need to fetch
                pairs_to_fetch.append(pair_lower)
        
        # Fetch missing/stale pairs
        if pairs_to_fetch:
            logger.info(f"Fetching {len(pairs_to_fetch)} pairs, {len(result)} from cache")
            fetched = self._fetch_order_books_sync(pairs_to_fetch)
            result.update(fetched)
        else:
            logger.info(f"All {len(pairs)} pairs served from cache")
        
        return result
    
    def _is_pair_cache_valid(self, pair: str) -> bool:
        """Check if cache for specific pair is still valid"""
        if pair not in self.cache_timestamps:
            return False
        return datetime.now() - self.cache_timestamps[pair] < self.cache_duration
    
    def _fetch_order_books_sync(self, pairs: List[str]) -> Dict[str, Dict]:
        """Synchronous wrapper for async fetch (for Flask routes)"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._fetch_order_books_async(pairs))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in _fetch_order_books_sync: {e}")
            return {pair: self._empty_order_book() for pair in pairs}
    
    async def _fetch_order_books_async(self, pairs: List[str]) -> Dict[str, Dict]:
        """Fetch order books from Indodax API in parallel"""
        logger.info(f"Fetching order books for {len(pairs)} pairs")
        
        # Fetch all pairs in parallel (batch of 50 at a time to avoid overwhelming API)
        batch_size = 50
        all_results = {}
        
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(pairs), batch_size):
                batch = pairs[i:i + batch_size]
                tasks = [self._fetch_single_order_book(session, pair) for pair in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for pair, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching order book for {pair}: {result}")
                        all_results[pair] = self._empty_order_book()
                    else:
                        all_results[pair] = result
                        # Update per-pair cache timestamp
                        self.cache[pair] = result
                        self.cache_timestamps[pair] = datetime.now()
                
                # Small delay between batches
                if i + batch_size < len(pairs):
                    await asyncio.sleep(0.1)
        
        # Update global timestamp for compatibility
        self.cache_timestamp = datetime.now()
        logger.info(f"Fetched and cached {len(all_results)} order books")
        return all_results
    
    async def _fetch_single_order_book(self, session: aiohttp.ClientSession, pair: str) -> Dict:
        """Fetch single order book from Indodax"""
        try:
            url = f"https://indodax.com/api/depth/{pair}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_order_book(data)
                else:
                    logger.warning(f"Failed to fetch order book for {pair}: {response.status}")
                    return self._empty_order_book()
        except Exception as e:
            logger.error(f"Exception fetching order book for {pair}: {e}")
            return self._empty_order_book()
    
    def _process_order_book(self, data: Dict) -> Dict:
        """Process order book data and calculate metrics"""
        try:
            buy_orders = data.get('buy', [])
            sell_orders = data.get('sell', [])
            
            # Calculate totals
            total_buy_amount = sum(float(order[1]) for order in buy_orders)
            total_sell_amount = sum(float(order[1]) for order in sell_orders)
            
            total_buy_value = sum(float(order[0]) * float(order[1]) for order in buy_orders)
            total_sell_value = sum(float(order[0]) * float(order[1]) for order in sell_orders)
            
            # Get best bid and ask
            highest_bid = float(buy_orders[0][0]) if buy_orders else 0
            lowest_ask = float(sell_orders[0][0]) if sell_orders else 0
            
            # Calculate spread
            spread = lowest_ask - highest_bid if (highest_bid and lowest_ask) else 0
            spread_percent = (spread / highest_bid * 100) if highest_bid else 0
            
            return {
                'total_buy_orders': len(buy_orders),
                'total_sell_orders': len(sell_orders),
                'total_buy_amount': total_buy_amount,
                'total_sell_amount': total_sell_amount,
                'total_buy_value': total_buy_value,
                'total_sell_value': total_sell_value,
                'highest_bid': highest_bid,
                'lowest_ask': lowest_ask,
                'spread': spread,
                'spread_percent': spread_percent,
                'buy_sell_ratio': total_buy_value / total_sell_value if total_sell_value else 0
            }
        except Exception as e:
            logger.error(f"Error processing order book: {e}")
            return self._empty_order_book()
    
    def _empty_order_book(self) -> Dict:
        """Return empty order book structure"""
        return {
            'total_buy_orders': 0,
            'total_sell_orders': 0,
            'total_buy_amount': 0,
            'total_sell_amount': 0,
            'total_buy_value': 0,
            'total_sell_value': 0,
            'highest_bid': 0,
            'lowest_ask': 0,
            'spread': 0,
            'spread_percent': 0,
            'buy_sell_ratio': 0
        }

    def fetch_and_cache_all(self):
        """
        Fetch and cache order books for all pairs (for background job)
        This is optional and runs periodically to warm up cache
        """
        try:
            # Get all pairs from Indodax
            import requests
            response = requests.get('https://indodax.com/api/pairs', timeout=10)
            if response.status_code == 200:
                pairs_data = response.json()
                pairs = [pair['ticker_id'].replace('_', '').lower() for pair in pairs_data]
                
                logger.info(f"Background job: fetching {len(pairs)} pairs")
                # Use the sync fetch method
                self._fetch_order_books_sync(pairs)
                logger.info(f"✓ Background job: cached order books for {len(pairs)} pairs")
            else:
                logger.error(f"Failed to fetch pairs list: {response.status_code}")
        except Exception as e:
            logger.error(f"Error in fetch_and_cache_all: {e}")

# Global instance
orderbook_service = OrderBookService()
