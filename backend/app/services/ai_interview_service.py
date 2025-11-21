"""
AI Interview Service
Analyzes candidate responses during AI video interviews
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from textblob import TextBlob
import numpy as np


class AIInterviewService:
    """Service for analyzing AI video interview responses"""
    
    def __init__(self):
        self.min_word_count = 20
        self.ideal_wpm_range = (120, 160)
        self.max_filler_word_ratio = 0.05
        
    def analyze_response(
        self,
        transcript: str,
        question: str,
        duration: int,
        question_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single interview response
        
        Args:
            transcript: The candidate's spoken response
            question: The interview question asked
            duration: Response duration in seconds
            question_type: Type of question (introduction, behavioral, technical, etc.)
            
        Returns:
            Dictionary containing detailed analysis
        """
        # Basic metrics
        word_count = self._count_words(transcript)
        words_per_minute = self._calculate_wpm(word_count, duration)
        
        # Content analysis
        sentiment = self._analyze_sentiment(transcript)
        clarity_score = self._analyze_clarity(transcript)
        confidence_score = self._analyze_confidence(transcript)
        
        # Communication analysis
        filler_words = self._detect_filler_words(transcript)
        structure_score = self._analyze_structure(transcript)
        
        # Technical analysis (if applicable)
        technical_terms = self._extract_technical_terms(transcript, question_type)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score({
            'word_count': word_count,
            'wpm': words_per_minute,
            'sentiment': sentiment,
            'clarity': clarity_score,
            'confidence': confidence_score,
            'structure': structure_score,
            'filler_ratio': len(filler_words) / max(word_count, 1)
        })
        
        return {
            'overall_score': overall_score,
            'metrics': {
                'word_count': word_count,
                'duration': duration,
                'words_per_minute': words_per_minute,
                'filler_word_count': len(filler_words),
                'filler_word_ratio': len(filler_words) / max(word_count, 1)
            },
            'analysis': {
                'sentiment': sentiment,
                'clarity_score': clarity_score,
                'confidence_score': confidence_score,
                'structure_score': structure_score
            },
            'content': {
                'technical_terms': technical_terms,
                'key_points': self._extract_key_points(transcript),
                'filler_words': filler_words
            },
            'feedback': self._generate_feedback(
                overall_score,
                word_count,
                words_per_minute,
                sentiment,
                clarity_score,
                len(filler_words) / max(word_count, 1)
            )
        }
    
    def analyze_full_interview(
        self,
        responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze complete interview with all responses
        
        Args:
            responses: List of response dictionaries with analysis
            
        Returns:
            Comprehensive interview analysis
        """
        if not responses:
            return self._empty_analysis()
        
        # Aggregate metrics
        total_words = sum(r.get('analysis', {}).get('metrics', {}).get('word_count', 0) 
                         for r in responses)
        total_duration = sum(r.get('analysis', {}).get('metrics', {}).get('duration', 0) 
                            for r in responses)
        avg_score = np.mean([r.get('analysis', {}).get('overall_score', 0) 
                            for r in responses])
        
        # Consistency analysis
        score_variance = np.var([r.get('analysis', {}).get('overall_score', 0) 
                                for r in responses])
        consistency_score = max(0, 100 - (score_variance * 10))
        
        # Improvement trend
        scores = [r.get('analysis', {}).get('overall_score', 0) for r in responses]
        improvement_trend = self._calculate_trend(scores)
        
        # Strengths and weaknesses
        strengths = self._identify_strengths(responses)
        weaknesses = self._identify_weaknesses(responses)
        
        return {
            'overall_score': round(avg_score, 1),
            'total_questions': len(responses),
            'aggregate_metrics': {
                'total_words': total_words,
                'total_duration': total_duration,
                'avg_words_per_minute': round(total_words / (total_duration / 60), 1) if total_duration > 0 else 0,
                'consistency_score': round(consistency_score, 1)
            },
            'performance': {
                'improvement_trend': improvement_trend,
                'best_question': self._find_best_response(responses),
                'needs_improvement': self._find_weakest_response(responses)
            },
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': self._generate_recommendations(responses, strengths, weaknesses),
            'question_scores': [
                {
                    'question_number': i + 1,
                    'score': r.get('analysis', {}).get('overall_score', 0),
                    'type': r.get('type', 'general')
                }
                for i, r in enumerate(responses)
            ]
        }
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def _calculate_wpm(self, word_count: int, duration: int) -> int:
        """Calculate words per minute"""
        if duration == 0:
            return 0
        return round((word_count / duration) * 60)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of response"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment_label = 'positive'
            elif polarity < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            return {
                'label': sentiment_label,
                'polarity': round(polarity, 2),
                'subjectivity': round(subjectivity, 2),
                'score': round((polarity + 1) * 50, 1)  # Convert to 0-100 scale
            }
        except:
            return {
                'label': 'neutral',
                'polarity': 0,
                'subjectivity': 0.5,
                'score': 50
            }
    
    def _analyze_clarity(self, text: str) -> float:
        """Analyze clarity of communication"""
        # Simple clarity metrics
        sentences = text.split('.')
        avg_sentence_length = len(text.split()) / max(len(sentences), 1)
        
        # Ideal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            length_score = 100
        else:
            length_score = max(0, 100 - abs(avg_sentence_length - 17.5) * 3)
        
        # Check for clear structure words
        structure_words = ['first', 'second', 'then', 'finally', 'because', 'therefore', 'however']
        structure_count = sum(1 for word in structure_words if word in text.lower())
        structure_score = min(100, structure_count * 20)
        
        return round((length_score + structure_score) / 2, 1)
    
    def _analyze_confidence(self, text: str) -> float:
        """Analyze confidence level in response"""
        # Confidence indicators
        confident_words = ['definitely', 'certainly', 'confident', 'sure', 'absolutely', 'clearly']
        uncertain_words = ['maybe', 'perhaps', 'might', 'possibly', 'not sure', 'i think', 'i guess']
        
        text_lower = text.lower()
        confident_count = sum(1 for word in confident_words if word in text_lower)
        uncertain_count = sum(1 for word in uncertain_words if word in text_lower)
        
        # Calculate confidence score
        confidence_score = 50 + (confident_count * 10) - (uncertain_count * 10)
        return round(max(0, min(100, confidence_score)), 1)
    
    def _detect_filler_words(self, text: str) -> List[str]:
        """Detect filler words in response"""
        filler_words = ['um', 'uh', 'like', 'you know', 'sort of', 'kind of', 'basically', 'actually']
        text_lower = text.lower()
        
        found_fillers = []
        for filler in filler_words:
            count = text_lower.count(filler)
            found_fillers.extend([filler] * count)
        
        return found_fillers
    
    def _analyze_structure(self, text: str) -> float:
        """Analyze response structure"""
        # Check for introduction, body, conclusion
        has_intro = any(word in text.lower()[:100] for word in ['let me', 'i would', 'to answer'])
        has_conclusion = any(word in text.lower()[-100:] for word in ['in conclusion', 'overall', 'to summarize', 'finally'])
        
        # Check for examples
        has_examples = any(word in text.lower() for word in ['for example', 'for instance', 'such as'])
        
        structure_score = 0
        if has_intro:
            structure_score += 33
        if has_examples:
            structure_score += 34
        if has_conclusion:
            structure_score += 33
        
        return round(structure_score, 1)
    
    def _extract_technical_terms(self, text: str, question_type: str) -> List[str]:
        """Extract technical terms from response"""
        # Common technical terms (can be expanded)
        technical_terms = [
            'algorithm', 'database', 'api', 'framework', 'architecture',
            'optimization', 'scalability', 'performance', 'security',
            'testing', 'deployment', 'integration', 'microservices'
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in technical_terms if term in text_lower]
        
        return found_terms
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from response"""
        # Simple extraction based on sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return sentences[:3]  # Return top 3 key points
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall response score"""
        # Weighted scoring
        weights = {
            'word_count': 0.15,
            'wpm': 0.15,
            'sentiment': 0.15,
            'clarity': 0.20,
            'confidence': 0.20,
            'structure': 0.15
        }
        
        # Normalize metrics to 0-100 scale
        normalized = {}
        
        # Word count (50-200 words is ideal)
        wc = metrics['word_count']
        normalized['word_count'] = min(100, (wc / 150) * 100) if wc < 150 else max(0, 100 - (wc - 150) / 2)
        
        # WPM (120-160 is ideal)
        wpm = metrics['wpm']
        if 120 <= wpm <= 160:
            normalized['wpm'] = 100
        else:
            normalized['wpm'] = max(0, 100 - abs(wpm - 140) / 2)
        
        # Sentiment (already 0-100)
        normalized['sentiment'] = metrics['sentiment'].get('score', 50)
        
        # Other metrics (already 0-100)
        normalized['clarity'] = metrics['clarity']
        normalized['confidence'] = metrics['confidence']
        normalized['structure'] = metrics['structure']
        
        # Penalty for too many filler words
        filler_penalty = min(20, metrics['filler_ratio'] * 400)
        
        # Calculate weighted score
        score = sum(normalized[key] * weights[key] for key in weights.keys())
        score = max(0, score - filler_penalty)
        
        return round(score, 1)
    
    def _generate_feedback(
        self,
        overall_score: float,
        word_count: int,
        wpm: int,
        sentiment: Dict,
        clarity: float,
        filler_ratio: float
    ) -> Dict[str, List[str]]:
        """Generate personalized feedback"""
        strengths = []
        improvements = []
        
        # Score-based feedback
        if overall_score >= 80:
            strengths.append("Excellent overall performance")
        elif overall_score >= 60:
            strengths.append("Good response quality")
        else:
            improvements.append("Focus on providing more comprehensive answers")
        
        # Word count feedback
        if 50 <= word_count <= 200:
            strengths.append("Appropriate response length")
        elif word_count < 50:
            improvements.append("Provide more detailed answers")
        else:
            improvements.append("Be more concise in your responses")
        
        # WPM feedback
        if 120 <= wpm <= 160:
            strengths.append("Excellent speaking pace")
        elif wpm < 120:
            improvements.append("Try to speak a bit faster")
        else:
            improvements.append("Slow down your speaking pace")
        
        # Sentiment feedback
        if sentiment['label'] == 'positive':
            strengths.append("Positive and enthusiastic tone")
        elif sentiment['label'] == 'negative':
            improvements.append("Maintain a more positive tone")
        
        # Clarity feedback
        if clarity >= 70:
            strengths.append("Clear and well-structured communication")
        else:
            improvements.append("Improve answer structure and clarity")
        
        # Filler words feedback
        if filler_ratio < 0.03:
            strengths.append("Minimal use of filler words")
        else:
            improvements.append("Reduce filler words (um, uh, like)")
        
        return {
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate performance trend"""
        if len(scores) < 2:
            return 'stable'
        
        # Simple linear regression
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        if slope > 2:
            return 'improving'
        elif slope < -2:
            return 'declining'
        else:
            return 'stable'
    
    def _identify_strengths(self, responses: List[Dict]) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        # Analyze all responses
        avg_clarity = np.mean([r.get('analysis', {}).get('analysis', {}).get('clarity_score', 0) 
                              for r in responses])
        avg_confidence = np.mean([r.get('analysis', {}).get('analysis', {}).get('confidence_score', 0) 
                                 for r in responses])
        
        if avg_clarity >= 70:
            strengths.append("Clear and articulate communication")
        if avg_confidence >= 70:
            strengths.append("Confident delivery")
        
        # Check for technical knowledge
        technical_count = sum(len(r.get('analysis', {}).get('content', {}).get('technical_terms', [])) 
                            for r in responses)
        if technical_count >= 5:
            strengths.append("Strong technical vocabulary")
        
        return strengths if strengths else ["Completed all interview questions"]
    
    def _identify_weaknesses(self, responses: List[Dict]) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        # Analyze all responses
        avg_structure = np.mean([r.get('analysis', {}).get('analysis', {}).get('structure_score', 0) 
                                for r in responses])
        avg_filler_ratio = np.mean([r.get('analysis', {}).get('metrics', {}).get('filler_word_ratio', 0) 
                                   for r in responses])
        
        if avg_structure < 50:
            weaknesses.append("Improve answer structure")
        if avg_filler_ratio > 0.05:
            weaknesses.append("Reduce filler words")
        
        return weaknesses if weaknesses else ["Continue practicing to improve further"]
    
    def _generate_recommendations(
        self,
        responses: List[Dict],
        strengths: List[str],
        weaknesses: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if "Improve answer structure" in weaknesses:
            recommendations.append("Use the STAR method (Situation, Task, Action, Result) for behavioral questions")
        
        if "Reduce filler words" in weaknesses:
            recommendations.append("Practice pausing instead of using filler words")
        
        if len(strengths) >= 3:
            recommendations.append("Maintain your strong communication style")
        
        recommendations.append("Review your responses and practice similar questions")
        
        return recommendations
    
    def _find_best_response(self, responses: List[Dict]) -> Dict[str, Any]:
        """Find the best response"""
        if not responses:
            return {}
        
        best = max(responses, key=lambda r: r.get('analysis', {}).get('overall_score', 0))
        return {
            'question_number': responses.index(best) + 1,
            'score': best.get('analysis', {}).get('overall_score', 0)
        }
    
    def _find_weakest_response(self, responses: List[Dict]) -> Dict[str, Any]:
        """Find the weakest response"""
        if not responses:
            return {}
        
        weakest = min(responses, key=lambda r: r.get('analysis', {}).get('overall_score', 0))
        return {
            'question_number': responses.index(weakest) + 1,
            'score': weakest.get('analysis', {}).get('overall_score', 0)
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'overall_score': 0,
            'total_questions': 0,
            'aggregate_metrics': {},
            'performance': {},
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'question_scores': []
        }


# Singleton instance
ai_interview_service = AIInterviewService()
