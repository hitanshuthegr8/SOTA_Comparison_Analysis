# =====================================================================
# SOTA IDENTIFICATION MODULE
# =====================================================================

import logging
import os
from typing import List, Dict, Optional
from services.api_wrapper import ArxivWrapper, SemanticScholarWrapper
from services.semantic_engine import SemanticEngine

logger = logging.getLogger(__name__)

class SOTAIdentifier:
    """
    Identifies top-K SOTA papers for a given research topic.
    Uses ArXiv search + Semantic Scholar metrics + LLM-based ranking.
    """

    def __init__(self, groq_api_key: str = None):
        self.arxiv_api = ArxivWrapper()
        self.semantic_scholar_api = SemanticScholarWrapper()
        self.semantic_engine = SemanticEngine(groq_api_key)
        self.groq_api_key = groq_api_key or os.environ.get('GROQ_API_KEY', '')

    def identify_sota(
        self,
        topic: str,
        max_results: int = 20,
        top_k: int = 2,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_metrics: bool = True
    ) -> Dict:
        """
        Returns top-K SOTA papers ranked by semantic relevance with metrics.

        Args:
            topic: Research topic/description to search for
            max_results: Maximum papers to fetch from ArXiv
            top_k: Number of top papers to return
            start_date: Filter papers published after this date (YYYY-MM-DD)
            end_date: Filter papers published before this date (YYYY-MM-DD)
            include_metrics: Whether to fetch citation metrics from Semantic Scholar

        Returns:
            {
                "topic": "...",
                "total_found": 20,
                "top_k": 2,
                "sota_papers": [
                    {
                        "sota_rank": 1,
                        "paper_id": "arXiv:XXXX.XXXXX",
                        "title": "...",
                        "abstract": "...",
                        "authors": [...],
                        "url": "...",
                        "pdf_url": "...",
                        "published_date": "2024-01-15",
                        "relevance_score": 0.92,
                        "metrics": {
                            "citation_count": 150,
                            "influential_citations": 25,
                            "recency_score": 0.85
                        },
                        "relevance_reason": "..."
                    }
                ]
            }
        """

        logger.info(f"[SOTA] Identifying SOTA papers for topic: {topic}")

        result = {
            "topic": topic,
            "total_found": 0,
            "top_k": top_k,
            "sota_papers": [],
            "search_params": {
                "max_results": max_results,
                "start_date": start_date,
                "end_date": end_date
            }
        }

        # ---- Step 1: Fetch candidates from ArXiv ----
        logger.info("[SOTA] Step 1: Fetching papers from ArXiv...")
        arxiv_results = self.arxiv_api.search(
            query=topic,
            start_date=start_date,
            end_date=end_date,
            max_results=max_results,
            sort_by="relevance"
        )

        if not arxiv_results:
            logger.warning("[SOTA] No papers found on ArXiv")
            return result

        result["total_found"] = len(arxiv_results)
        logger.info(f"[SOTA] Found {len(arxiv_results)} candidate papers")

        # ---- Step 2: Semantic ranking ----
        logger.info("[SOTA] Step 2: Ranking papers by semantic relevance...")
        ranked_papers = self.semantic_engine.rank_papers(
            topic, 
            arxiv_results, 
            top_k=min(top_k * 2, len(arxiv_results))  # Get more than needed for filtering
        )

        # ---- Step 3: Enrich with Semantic Scholar metrics ----
        if include_metrics:
            logger.info("[SOTA] Step 3: Fetching citation metrics...")
            ranked_papers = self.semantic_scholar_api.enrich_papers(ranked_papers[:top_k * 2])

        # ---- Step 4: Final ranking and selection ----
        logger.info("[SOTA] Step 4: Computing final scores and selecting top papers...")
        final_papers = self._compute_final_ranking(ranked_papers, topic, top_k)

        # ---- Step 5: Generate relevance explanations ----
        logger.info("[SOTA] Step 5: Generating relevance explanations...")
        for paper in final_papers:
            paper['relevance_reason'] = self.semantic_engine.compute_relevance_explanation(
                topic, paper
            )

        result["sota_papers"] = final_papers
        logger.info(f"[SOTA] Successfully identified top-{len(final_papers)} SOTA papers")
        
        return result

    def _compute_final_ranking(self, papers: List[Dict], topic: str, top_k: int) -> List[Dict]:
        """
        Compute final ranking combining relevance, citations, and recency.
        """
        from datetime import datetime
        
        scored_papers = []
        
        for paper in papers:
            # Get base relevance score
            relevance_score = paper.get('score', 0.5)
            
            # Compute citation score (normalized)
            citation_count = paper.get('citation_count', 0)
            citation_score = min(1.0, citation_count / 500) if citation_count else 0
            
            # Compute recency score (papers from last 2 years get higher score)
            recency_score = 0.5
            pub_date = paper.get('published_date')
            if pub_date:
                try:
                    pub = datetime.strptime(pub_date, '%Y-%m-%d')
                    days_old = (datetime.now() - pub).days
                    if days_old < 180:  # < 6 months
                        recency_score = 1.0
                    elif days_old < 365:  # < 1 year
                        recency_score = 0.9
                    elif days_old < 730:  # < 2 years
                        recency_score = 0.7
                    else:
                        recency_score = max(0.3, 1.0 - (days_old / 3650))  # Decay over 10 years
                except ValueError:
                    pass
            
            # Compute final composite score
            # Weights: Relevance (50%), Citations (25%), Recency (25%)
            final_score = (
                relevance_score * 0.50 +
                citation_score * 0.25 +
                recency_score * 0.25
            )
            
            # Build output structure
            scored_papers.append({
                "paper_id": paper.get('paper_id'),
                "arxiv_id": paper.get('arxiv_id'),
                "title": paper.get('title'),
                "abstract": paper.get('abstract', '')[:500] + '...' if len(paper.get('abstract', '')) > 500 else paper.get('abstract', ''),
                "authors": paper.get('authors', [])[:5],  # Limit authors
                "url": paper.get('url'),
                "pdf_url": paper.get('pdf_url'),
                "published_date": paper.get('published_date'),
                "categories": paper.get('categories', []),
                "relevance_score": round(relevance_score, 3),
                "final_score": round(final_score, 3),
                "metrics": {
                    "citation_count": citation_count,
                    "influential_citations": paper.get('influential_citation_count', 0),
                    "reference_count": paper.get('reference_count', 0),
                    "recency_score": round(recency_score, 2),
                    "citation_score": round(citation_score, 2)
                }
            })
        
        # Sort by final score
        scored_papers.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Assign ranks
        for i, paper in enumerate(scored_papers[:top_k]):
            paper['sota_rank'] = i + 1
        
        return scored_papers[:top_k]


def search_sota_papers(topic: str, top_k: int = 2) -> Dict:
    """
    Convenience function to search for SOTA papers.
    
    Usage:
        from services.sota_identifier import search_sota_papers
        results = search_sota_papers("transformer attention mechanisms", top_k=2)
    """
    identifier = SOTAIdentifier()
    return identifier.identify_sota(topic=topic, top_k=top_k)
