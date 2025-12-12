"""
Order Book Service
Fetches and caches order book data from Indodax API
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OrderBookService:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration = timedelta(seconds=30)  # Cache for 30 seconds
        self.is_fetching = False
        
    async def get_order_books(self, pairs: List[str]) -> Dict[str, Dict]:
        """
        Get order books for all pairs with caching
        """
        # Return cache if still valid
        if self._is_cache_valid():
            return self.cache
            
        # Prevent multiple simultaneous fetches
        if self.is_fetching:
            # Wait for ongoing fetch to complete
            while self.is_fetching:
                await asyncio.sleep(0.1)
            return self.cache
            
        # Fetch new data
        self.is_fetching = True
        try:
            await self._fetch_order_books(pairs)
        finally:
            self.is_fetching = False
            
        return self.cache
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_timestamp:
            return False
        return datetime.now() - self.cache_timestamp < self.cache_duration
    
    async def _fetch_order_books(self, pairs: List[str]):
        """Fetch order books from Indodax API in parallel batches"""
        logger.info(f"Fetching order books for {len(pairs)} pairs")
        
        # Fetch in batches of 50 to avoid overwhelming the API
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
                
                # Small delay between batches
                if i + batch_size < len(pairs):
                    await asyncio.sleep(0.1)
        
        self.cache = all_results
        self.cache_timestamp = datetime.now()
        logger.info(f"Order books cached at {self.cache_timestamp}")
    
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

# Global instance
orderbook_service = OrderBookService()
