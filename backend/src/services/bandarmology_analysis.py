"""
Bandarmology analysis service for detecting whale/market maker activity.
"""
import numpy as np
from typing import Dict, List, Optional
from flask import current_app


class BandarmologyService:
    """Service for analyzing order book and detecting whale activity"""
    
    def analyze_order_book(self, depth_data: Dict) -> Dict:
        """
        Analyze order book for whale activity and imbalances.
        
        Args:
            depth_data: Order book depth data with 'buy' and 'sell' orders
            
        Returns:
            Dictionary with bandarmology analysis
        """
        if not depth_data or not depth_data.get('buy') or not depth_data.get('sell'):
            return {'error': 'Insufficient order book data'}
        
        buy_orders = depth_data.get('buy', [])
        sell_orders = depth_data.get('sell', [])
        
        analysis = {
            'order_book_imbalance': self._calculate_imbalance(buy_orders, sell_orders),
            'buy_sell_walls': self._detect_walls(buy_orders, sell_orders),
            'whale_activity': self._detect_whale_activity(buy_orders, sell_orders),
            'spread_analysis': self._analyze_spread(buy_orders, sell_orders),
            'depth_visualization': self._prepare_depth_viz(buy_orders, sell_orders)
        }
        
        # Calculate bandarmology score
        analysis['bandarmology_score'] = self._calculate_bandarmology_score(analysis)
        
        return analysis
    
    def _calculate_imbalance(self, buy_orders: List, sell_orders: List) -> Dict:
        """
        Calculate order book imbalance ratio.
        
        Args:
            buy_orders: List of buy orders [price, volume]
            sell_orders: List of sell orders [price, volume]
            
        Returns:
            Dictionary with imbalance metrics
        """
        try:
            # Calculate total volumes
            buy_volume = sum(float(order[1]) for order in buy_orders[:20])  # Top 20
            sell_volume = sum(float(order[1]) for order in sell_orders[:20])
            
            total_volume = buy_volume + sell_volume
            
            if total_volume == 0:
                return {'ratio': 0.5, 'pressure': 'neutral'}
            
            buy_ratio = buy_volume / total_volume
            
            # Determine pressure
            if buy_ratio > 0.6:
                pressure = 'strong_buy'
            elif buy_ratio > 0.55:
                pressure = 'buy'
            elif buy_ratio < 0.4:
                pressure = 'strong_sell'
            elif buy_ratio < 0.45:
                pressure = 'sell'
            else:
                pressure = 'neutral'
            
            return {
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'ratio': buy_ratio,
                'pressure': pressure
            }
        
        except Exception as e:
            current_app.logger.error(f"Imbalance calculation error: {e}")
            return {'ratio': 0.5, 'pressure': 'neutral'}
    
    def _detect_walls(self, buy_orders: List, sell_orders: List) -> Dict:
        """
        Detect buy and sell walls (large orders).
        
        Args:
            buy_orders: List of buy orders
            sell_orders: List of sell orders
            
        Returns:
            Dictionary with wall detection results
        """
        try:
            # Calculate average volumes
            buy_volumes = [float(order[1]) for order in buy_orders[:50]]
            sell_volumes = [float(order[1]) for order in sell_orders[:50]]
            
            avg_buy_volume = np.mean(buy_volumes) if buy_volumes else 0
            avg_sell_volume = np.mean(sell_volumes) if sell_volumes else 0
            
            # Detect walls (orders > 3x average)
            wall_threshold = 3.0
            
            buy_walls = [
                {'price': float(order[0]), 'volume': float(order[1])}
                for order in buy_orders[:20]
                if float(order[1]) > avg_buy_volume * wall_threshold
            ]
            
            sell_walls = [
                {'price': float(order[0]), 'volume': float(order[1])}
                for order in sell_orders[:20]
                if float(order[1]) > avg_sell_volume * wall_threshold
            ]
            
            return {
                'buy_walls': buy_walls[:5],  # Top 5
                'sell_walls': sell_walls[:5],
                'has_buy_wall': len(buy_walls) > 0,
                'has_sell_wall': len(sell_walls) > 0
            }
        
        except Exception as e:
            current_app.logger.error(f"Wall detection error: {e}")
            return {'buy_walls': [], 'sell_walls': [], 'has_buy_wall': False, 'has_sell_wall': False}
    
    def _detect_whale_activity(self, buy_orders: List, sell_orders: List) -> Dict:
        """
        Detect whale trader activity.
        
        Args:
            buy_orders: List of buy orders
            sell_orders: List of sell orders
            
        Returns:
            Dictionary with whale activity metrics
        """
        try:
            # Combine all orders
            all_volumes = (
                [float(order[1]) for order in buy_orders[:50]] +
                [float(order[1]) for order in sell_orders[:50]]
            )
            
            if not all_volumes:
                return {'whale_detected': False, 'whale_percentage': 0}
            
            # Calculate 95th percentile (top 5%)
            whale_threshold = np.percentile(all_volumes, 95)
            
            # Count whale orders
            whale_orders = [v for v in all_volumes if v >= whale_threshold]
            whale_volume = sum(whale_orders)
            total_volume = sum(all_volumes)
            
            whale_percentage = (whale_volume / total_volume * 100) if total_volume > 0 else 0
            
            return {
                'whale_detected': len(whale_orders) > 0,
                'whale_orders_count': len(whale_orders),
                'whale_percentage': whale_percentage,
                'whale_threshold': whale_threshold
            }
        
        except Exception as e:
            current_app.logger.error(f"Whale detection error: {e}")
            return {'whale_detected': False, 'whale_percentage': 0}
    
    def _analyze_spread(self, buy_orders: List, sell_orders: List) -> Dict:
        """
        Analyze bid-ask spread.
        
        Args:
            buy_orders: List of buy orders
            sell_orders: List of sell orders
            
        Returns:
            Dictionary with spread analysis
        """
        try:
            if not buy_orders or not sell_orders:
                return {'spread': 0, 'spread_percentage': 0, 'liquidity': 'low'}
            
            highest_bid = float(buy_orders[0][0])
            lowest_ask = float(sell_orders[0][0])
            
            spread = lowest_ask - highest_bid
            mid_price = (highest_bid + lowest_ask) / 2
            spread_percentage = (spread / mid_price * 100) if mid_price > 0 else 0
            
            # Determine liquidity
            if spread_percentage < 0.1:
                liquidity = 'high'
            elif spread_percentage < 0.5:
                liquidity = 'medium'
            else:
                liquidity = 'low'
            
            return {
                'highest_bid': highest_bid,
                'lowest_ask': lowest_ask,
                'spread': spread,
                'spread_percentage': spread_percentage,
                'liquidity': liquidity
            }
        
        except Exception as e:
            current_app.logger.error(f"Spread analysis error: {e}")
            return {'spread': 0, 'spread_percentage': 0, 'liquidity': 'unknown'}
    
    def _prepare_depth_viz(self, buy_orders: List, sell_orders: List, limit: int = 20) -> Dict:
        """
        Prepare data for order book visualization.
        
        Args:
            buy_orders: List of buy orders
            sell_orders: List of sell orders
            limit: Number of orders to include
            
        Returns:
            Dictionary with visualization data
        """
        try:
            return {
                'bids': [
                    {'price': float(order[0]), 'volume': float(order[1])}
                    for order in buy_orders[:limit]
                ],
                'asks': [
                    {'price': float(order[0]), 'volume': float(order[1])}
                    for order in sell_orders[:limit]
                ]
            }
        except Exception as e:
            current_app.logger.error(f"Depth visualization error: {e}")
            return {'bids': [], 'asks': []}
    
    def _calculate_bandarmology_score(self, analysis: Dict) -> float:
        """
        Calculate overall bandarmology score (0-40).
        
        Args:
            analysis: Bandarmology analysis data
            
        Returns:
            Bandarmology score
        """
        score = 20.0  # Start at neutral
        
        # Order book imbalance (±10 points)
        imbalance = analysis.get('order_book_imbalance', {})
        pressure = imbalance.get('pressure', 'neutral')
        
        if pressure == 'strong_buy':
            score += 10
        elif pressure == 'buy':
            score += 5
        elif pressure == 'strong_sell':
            score -= 10
        elif pressure == 'sell':
            score -= 5
        
        # Whale activity (±5 points)
        whale = analysis.get('whale_activity', {})
        if whale.get('whale_detected'):
            whale_pct = whale.get('whale_percentage', 0)
            if whale_pct > 30:
                score += 5
            elif whale_pct > 20:
                score += 3
        
        # Walls detection (±5 points)
        walls = analysis.get('buy_sell_walls', {})
        if walls.get('has_buy_wall') and not walls.get('has_sell_wall'):
            score += 5
        elif walls.get('has_sell_wall') and not walls.get('has_buy_wall'):
            score -= 5
        
        # Spread/liquidity (±5 points)
        spread = analysis.get('spread_analysis', {})
        liquidity = spread.get('liquidity', 'medium')
        
        if liquidity == 'high':
            score += 5
        elif liquidity == 'low':
            score -= 5
        
        # Clamp to 0-40 range
        return max(0, min(40, score))


# Global service instance
_bandarmology_service = None


def get_bandarmology_service() -> BandarmologyService:
    """
    Get or create bandarmology service instance.
    
    Returns:
        BandarmologyService instance
    """
    global _bandarmology_service
    
    if _bandarmology_service is None:
        _bandarmology_service = BandarmologyService()
    
    return _bandarmology_service
