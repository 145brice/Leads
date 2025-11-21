"""
AI-powered lead scoring system using HuggingFace models
"""
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, List
import re


class LeadScorer:
    """Score building permits for contractor lead quality"""
    
    def __init__(self, model_name='distilbert-base-uncased-finetuned-sst-2-english'):
        """Initialize the AI model for scoring"""
        print(f"Loading model: {model_name}")
        self.sentiment_analyzer = pipeline('sentiment-analysis', model=model_name)
        
        # High-value permit types
        self.high_value_types = [
            'new construction', 'commercial', 'addition', 'renovation',
            'remodel', 'multi-family', 'retail', 'restaurant'
        ]
        
        # Desirable areas (can be configured based on market)
        self.premium_areas = [
            'downtown', 'green hills', 'brentwood', 'franklin',
            'murfreesboro', 'gallatin', 'hendersonville'
        ]
    
    def score_permit(self, permit: Dict) -> Dict:
        """
        Score a single permit on multiple factors
        Returns permit dict with added 'score' and 'score_breakdown' fields
        """
        scores = {
            'size_score': self._score_job_size(permit),
            'location_score': self._score_location(permit),
            'urgency_score': self._score_urgency(permit),
            'type_score': self._score_permit_type(permit)
        }
        
        # Weighted total score (0-100)
        total_score = (
            scores['size_score'] * 0.35 +
            scores['location_score'] * 0.25 +
            scores['urgency_score'] * 0.20 +
            scores['type_score'] * 0.20
        )
        
        permit['score'] = round(total_score, 2)
        permit['score_breakdown'] = scores
        
        return permit
    
    def score_batch(self, permits: List[Dict]) -> List[Dict]:
        """Score multiple permits and return sorted by score"""
        scored_permits = [self.score_permit(permit) for permit in permits]
        return sorted(scored_permits, key=lambda x: x['score'], reverse=True)
    
    def _score_job_size(self, permit: Dict) -> float:
        """Score based on estimated project value (0-100)"""
        value = permit.get('estimated_value', 0)
        
        if value == 0:
            return 30  # Unknown value gets neutral score
        elif value < 10000:
            return 20
        elif value < 50000:
            return 40
        elif value < 100000:
            return 60
        elif value < 250000:
            return 80
        else:
            return 100  # $250k+ projects
    
    def _score_location(self, permit: Dict) -> float:
        """Score based on location desirability (0-100)"""
        address = permit.get('address', '').lower()
        county = permit.get('county', '').lower()
        
        score = 50  # Base score
        
        # Check for premium areas
        for area in self.premium_areas:
            if area in address or area in county:
                score = 85
                break
        
        # Bonus for specific desirable counties
        if 'williamson' in county:
            score += 15
        elif 'davidson' in county:
            score += 10
        
        return min(score, 100)
    
    def _score_urgency(self, permit: Dict) -> float:
        """
        Score urgency using AI sentiment analysis on description
        Higher sentiment = more exciting/urgent project
        """
        description = permit.get('work_description', '')
        permit_type = permit.get('permit_type', '')
        
        # Combine text for analysis
        text = f"{permit_type} {description}".strip()
        
        if not text or len(text) < 10:
            return 50  # Neutral score for missing data
        
        try:
            # Truncate to model max length
            text = text[:512]
            
            # Get sentiment score
            result = self.sentiment_analyzer(text)[0]
            
            # Convert to 0-100 scale
            if result['label'] == 'POSITIVE':
                score = 50 + (result['score'] * 50)  # 50-100
            else:
                score = 50 - (result['score'] * 30)  # 20-50
            
            return round(score, 2)
        
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 50
    
    def _score_permit_type(self, permit: Dict) -> float:
        """Score based on permit type profitability (0-100)"""
        permit_type = permit.get('permit_type', '').lower()
        
        # Check for high-value types
        for high_value in self.high_value_types:
            if high_value in permit_type:
                return 90
        
        # Medium value types
        medium_value = ['repair', 'alteration', 'replacement', 'install']
        for medium in medium_value:
            if medium in permit_type:
                return 60
        
        # Low value
        low_value = ['fence', 'sign', 'demolition', 'pool']
        for low in low_value:
            if low in permit_type:
                return 30
        
        return 50  # Unknown type
    
    def get_top_leads(self, permits: List[Dict], n: int = 10) -> List[Dict]:
        """Get top N scored leads"""
        scored = self.score_batch(permits)
        return scored[:n]
