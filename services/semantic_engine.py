# =====================================================================
# SEMANTIC RANKING ENGINE
# =====================================================================

import logging
import os
from typing import List, Dict
import requests

logger = logging.getLogger(__name__)

class SemanticEngine:
    """
    Ranks papers by semantic relevance to a query using Groq LLM.
    This provides a smarter ranking than keyword matching.
    """
    
    def __init__(self, groq_api_key: str = None):
        self.api_key = groq_api_key or os.environ.get('GROQ_API_KEY', '')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
    
    def rank_papers(self, query: str, papers: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        Rank papers by semantic relevance to the query.
        
        Uses LLM to score each paper's relevance to the research topic.
        Falls back to simple scoring if LLM unavailable.
        """
        
        if not papers:
            return []
        
        # If only a few papers, score them all
        if len(papers) <= top_k:
            return self._score_papers(query, papers)
        
        # For many papers, do batch scoring
        scored = self._score_papers(query, papers)
        
        # Sort by score descending
        scored.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored[:top_k]
    
    def _score_papers(self, query: str, papers: List[Dict]) -> List[Dict]:
        """Score each paper's relevance to the query."""
        
        # Try LLM-based scoring first
        if self.api_key:
            try:
                return self._llm_score_papers(query, papers)
            except Exception as e:
                logger.warning(f"[SemanticEngine] LLM scoring failed, using fallback: {e}")
        
        # Fallback to simple keyword scoring
        return self._keyword_score_papers(query, papers)
    
    def _llm_score_papers(self, query: str, papers: List[Dict]) -> List[Dict]:
        """Use LLM to score paper relevance."""
        
        # Format papers for LLM
        paper_list = []
        for i, p in enumerate(papers[:15]):  # Limit to avoid token limits
            paper_list.append(f"{i+1}. \"{p.get('title', 'Unknown')}\"")
        
        prompt = f"""You are a research paper relevance scorer. Given a research topic and a list of paper titles, rate each paper's relevance to the topic.

Research Topic: {query}

Papers:
{chr(10).join(paper_list)}

For each paper, provide a relevance score from 0.0 to 1.0 where:
- 1.0 = Directly addresses the core topic
- 0.7-0.9 = Highly relevant, addresses key aspects
- 0.4-0.6 = Moderately relevant, touches on related concepts
- 0.1-0.3 = Tangentially related
- 0.0 = Not relevant

Return ONLY a JSON array of scores in order, like: [0.95, 0.72, 0.45, ...]
No explanation, just the array."""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.1,
            'max_tokens': 200
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()['choices'][0]['message']['content'].strip()
        
        # Parse scores
        import json
        try:
            # Clean the response
            result = result.replace('```json', '').replace('```', '').strip()
            scores = json.loads(result)
            
            # Apply scores to papers
            for i, paper in enumerate(papers[:len(scores)]):
                paper['score'] = scores[i] if i < len(scores) else 0.5
                
            # Score remaining papers with 0.5 default
            for paper in papers[len(scores):]:
                paper['score'] = 0.5
                
        except json.JSONDecodeError:
            logger.warning("[SemanticEngine] Failed to parse LLM scores")
            return self._keyword_score_papers(query, papers)
        
        return papers
    
    def _keyword_score_papers(self, query: str, papers: List[Dict]) -> List[Dict]:
        """Simple keyword-based scoring as fallback."""
        
        query_words = set(query.lower().split())
        
        for paper in papers:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            
            # Combine text
            text = title + ' ' + abstract
            text_words = set(text.split())
            
            # Calculate overlap
            overlap = len(query_words & text_words)
            max_possible = len(query_words)
            
            # Bonus for title matches
            title_words = set(title.split())
            title_overlap = len(query_words & title_words)
            
            # Calculate score
            if max_possible > 0:
                base_score = overlap / max_possible
                title_bonus = (title_overlap / max_possible) * 0.3
                paper['score'] = min(1.0, base_score * 0.7 + title_bonus + 0.1)
            else:
                paper['score'] = 0.5
        
        return papers
    
    def compute_relevance_explanation(self, query: str, paper: Dict) -> str:
        """Generate a brief explanation of why a paper is relevant."""
        
        if not self.api_key:
            return "Paper matches search criteria based on title and abstract content."
        
        prompt = f"""In one sentence, explain why this paper is relevant to the research topic.

Topic: {query}
Paper Title: {paper.get('title', 'Unknown')}
Abstract: {paper.get('abstract', '')[:500]}

Response (one sentence only):"""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 100
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.debug(f"[SemanticEngine] Explanation generation failed: {e}")
            return "Relevant based on semantic similarity to the research topic."
