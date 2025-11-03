"""
Recommendation service that combines technical and bandarmology analysis.
"""
from typing import Dict
from flask import current_app


class RecommendationService:
    """Service for generating buy/sell recommendations"""
    
    def generate_recommendation(
        self,
        technical_analysis: Dict,
        bandarmology_analysis: Dict,
        market_data: Dict
    ) -> Dict:
        """
        Generate trading recommendation based on all analyses.
        
        Args:
            technical_analysis: Technical analysis results
            bandarmology_analysis: Bandarmology analysis results
            market_data: Current market data
            
        Returns:
            Dictionary with recommendation and scores
        """
        # Extract scores
        technical_score = technical_analysis.get('technical_score', 20)
        bandarmology_score = bandarmology_analysis.get('bandarmology_score', 20)
        momentum_score = self._calculate_momentum_score(market_data)
        
        # Calculate weighted total score
        total_score = (
            technical_score * 0.4 +          # 40% weight
            bandarmology_score * 0.4 +       # 40% weight
            momentum_score * 0.2             # 20% weight
        )
        
        # Determine action and confidence
        action, confidence = self._determine_action(total_score)
        
        recommendation = {
            'action': action,
            'confidence': confidence,
            'total_score': round(total_score, 2),
            'breakdown': {
                'technical_score': round(technical_score, 2),
                'bandarmology_score': round(bandarmology_score, 2),
                'momentum_score': round(momentum_score, 2)
            },
            'interpretation': self._generate_interpretation(
                action, confidence, total_score, technical_score, 
                bandarmology_score, momentum_score
            ),
            'risk_level': self._assess_risk(total_score, market_data),
            'signals': {
                'technical': technical_analysis.get('signals', {}),
                'bandarmology': {
                    'imbalance': bandarmology_analysis.get('order_book_imbalance', {}),
                    'walls': bandarmology_analysis.get('buy_sell_walls', {}),
                    'whale': bandarmology_analysis.get('whale_activity', {})
                }
            }
        }
        
        return recommendation
    
    def _calculate_momentum_score(self, market_data: Dict) -> float:
        """
        Calculate momentum score from market data (0-20).
        
        Args:
            market_data: Market data including price changes and volume
            
        Returns:
            Momentum score
        """
        score = 10.0  # Start at neutral
        
        try:
            # Price change analysis (±5 points)
            price_change_24h = float(market_data.get('price_change_24h', 0))
            
            if price_change_24h > 10:
                score += 5
            elif price_change_24h > 5:
                score += 3
            elif price_change_24h < -10:
                score -= 5
            elif price_change_24h < -5:
                score -= 3
            
            # Volume trend analysis (±5 points)
            volume_24h = float(market_data.get('volume_24h', 0))
            avg_volume = float(market_data.get('avg_volume', volume_24h))
            
            if avg_volume > 0:
                volume_ratio = volume_24h / avg_volume
                
                if volume_ratio > 1.5:  # 50% above average
                    score += 5
                elif volume_ratio > 1.2:  # 20% above average
                    score += 3
                elif volume_ratio < 0.5:  # 50% below average
                    score -= 5
                elif volume_ratio < 0.8:  # 20% below average
                    score -= 3
            
        except Exception as e:
            current_app.logger.error(f"Momentum calculation error: {e}")
        
        # Clamp to 0-20 range
        return max(0, min(20, score))
    
    def _determine_action(self, total_score: float) -> tuple:
        """
        Determine trading action and confidence level.
        
        Args:
            total_score: Total combined score
            
        Returns:
            Tuple of (action, confidence)
        """
        if total_score >= 75:
            return ('STRONG_BUY', 'HIGH')
        elif total_score >= 60:
            return ('BUY', 'MEDIUM')
        elif total_score >= 50:
            return ('WEAK_BUY', 'LOW')
        elif total_score > 40:
            return ('HOLD', 'MEDIUM')
        elif total_score >= 30:
            return ('WEAK_SELL', 'LOW')
        elif total_score >= 25:
            return ('SELL', 'MEDIUM')
        else:
            return ('STRONG_SELL', 'HIGH')
    
    def _assess_risk(self, total_score: float, market_data: Dict) -> str:
        """
        Assess risk level.
        
        Args:
            total_score: Total score
            market_data: Market data
            
        Returns:
            Risk level string
        """
        # Consider score extremes
        if total_score > 80 or total_score < 20:
            return 'HIGH'
        
        # Consider volatility
        try:
            price_change = abs(float(market_data.get('price_change_24h', 0)))
            if price_change > 15:
                return 'HIGH'
            elif price_change > 10:
                return 'MEDIUM'
        except:
            pass
        
        # Default risk
        if 40 <= total_score <= 60:
            return 'LOW'
        else:
            return 'MEDIUM'
    
    def _generate_interpretation(
        self,
        action: str,
        confidence: str,
        total_score: float,
        technical_score: float,
        bandarmology_score: float,
        momentum_score: float
    ) -> str:
        """
        Generate human-readable interpretation.
        
        Args:
            action: Trading action
            confidence: Confidence level
            total_score: Total score
            technical_score: Technical analysis score
            bandarmology_score: Bandarmology score
            momentum_score: Momentum score
            
        Returns:
            Interpretation string
        """
        interpretations = []
        
        # Overall interpretation
        if total_score >= 60:
            interpretations.append(
                f"Overall bullish signal with {confidence.lower()} confidence. "
                f"Total score of {total_score:.0f}/100 suggests favorable buying conditions."
            )
        elif total_score <= 40:
            interpretations.append(
                f"Overall bearish signal with {confidence.lower()} confidence. "
                f"Total score of {total_score:.0f}/100 suggests caution or selling opportunity."
            )
        else:
            interpretations.append(
                f"Neutral market conditions. Total score of {total_score:.0f}/100 "
                "suggests holding current positions and waiting for clearer signals."
            )
        
        # Technical analysis interpretation
        if technical_score > 25:
            interpretations.append(
                f"Technical indicators are showing positive signals (score: {technical_score:.0f}/40)."
            )
        elif technical_score < 15:
            interpretations.append(
                f"Technical indicators are showing negative signals (score: {technical_score:.0f}/40)."
            )
        else:
            interpretations.append(
                f"Technical indicators are neutral (score: {technical_score:.0f}/40)."
            )
        
        # Bandarmology interpretation
        if bandarmology_score > 25:
            interpretations.append(
                f"Order book analysis indicates buying pressure (score: {bandarmology_score:.0f}/40)."
            )
        elif bandarmology_score < 15:
            interpretations.append(
                f"Order book analysis indicates selling pressure (score: {bandarmology_score:.0f}/40)."
            )
        else:
            interpretations.append(
                f"Order book is balanced (score: {bandarmology_score:.0f}/40)."
            )
        
        # Momentum interpretation
        if momentum_score > 12:
            interpretations.append(
                f"Strong positive momentum detected (score: {momentum_score:.0f}/20)."
            )
        elif momentum_score < 8:
            interpretations.append(
                f"Weak or negative momentum (score: {momentum_score:.0f}/20)."
            )
        
        return " ".join(interpretations)


# Global service instance
_recommendation_service = None


def get_recommendation_service() -> RecommendationService:
    """
    Get or create recommendation service instance.
    
    Returns:
        RecommendationService instance
    """
    global _recommendation_service
    
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    
    return _recommendation_service
