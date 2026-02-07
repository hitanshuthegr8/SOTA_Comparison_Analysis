# =====================================================================
# API WRAPPERS FOR ARXIV AND SEMANTIC SCHOLAR
# =====================================================================

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class ArxivWrapper:
    """
    Wrapper for ArXiv API to search and fetch papers.
    ArXiv API: https://arxiv.org/help/api/
    """
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResearchIdeationPipeline/1.0'
        })
    
    def search(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 20,
        sort_by: str = "relevance",
        sort_order: str = "descending"
    ) -> List[Dict]:
        """
        Search ArXiv for papers matching the query.
        
        Args:
            query: Search query (topic description)
            start_date: Filter papers after this date (YYYY-MM-DD)
            end_date: Filter papers before this date (YYYY-MM-DD)
            max_results: Maximum number of results to return
            sort_by: Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate'
            sort_order: 'ascending' or 'descending'
        
        Returns:
            List of paper dictionaries
        """
        
        # Build search query
        search_query = self._build_query(query)
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        
        try:
            logger.info(f"[ArXiv] Searching for: {query}")
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            papers = self._parse_response(response.text)
            
            # Filter by date if specified
            if start_date or end_date:
                papers = self._filter_by_date(papers, start_date, end_date)
            
            logger.info(f"[ArXiv] Found {len(papers)} papers")
            return papers
            
        except requests.RequestException as e:
            logger.error(f"[ArXiv] API error: {e}")
            return []
    
    def _build_query(self, query: str) -> str:
        """Build ArXiv search query string."""
        # Search in title, abstract, and categories
        # Clean and format query
        clean_query = query.replace('"', '').strip()
        
        # Search in all fields with OR between title and abstract
        return f'all:"{clean_query}" OR ti:"{clean_query}" OR abs:"{clean_query}"'
    
    def _parse_response(self, xml_text: str) -> List[Dict]:
        """Parse ArXiv API XML response."""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = self._parse_entry(entry, ns)
                if paper:
                    papers.append(paper)
                    
        except ET.ParseError as e:
            logger.error(f"[ArXiv] XML parse error: {e}")
            
        return papers
    
    def _parse_entry(self, entry, ns: dict) -> Optional[Dict]:
        """Parse a single ArXiv entry."""
        try:
            # Extract paper ID
            id_elem = entry.find('atom:id', ns)
            if id_elem is None:
                return None
                
            arxiv_url = id_elem.text
            paper_id = arxiv_url.split('/')[-1]
            
            # Extract title
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Unknown"
            
            # Extract abstract
            summary_elem = entry.find('atom:summary', ns)
            abstract = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # Extract published date
            published_elem = entry.find('atom:published', ns)
            published = published_elem.text[:10] if published_elem is not None else None
            
            # Extract updated date
            updated_elem = entry.find('atom:updated', ns)
            updated = updated_elem.text[:10] if updated_elem is not None else None
            
            # Extract categories
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # Get PDF link
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            
            # Extract citation count placeholder (ArXiv doesn't provide this)
            # We'll try to get it from Semantic Scholar later
            
            return {
                'paper_id': f"arXiv:{paper_id}",
                'arxiv_id': paper_id,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'published_date': published,
                'updated_date': updated,
                'categories': categories,
                'url': arxiv_url,
                'pdf_url': pdf_url,
                'source': 'arxiv'
            }
            
        except Exception as e:
            logger.error(f"[ArXiv] Entry parse error: {e}")
            return None
    
    def _filter_by_date(self, papers: List[Dict], start_date: str, end_date: str) -> List[Dict]:
        """Filter papers by date range."""
        filtered = []
        
        for paper in papers:
            pub_date = paper.get('published_date')
            if not pub_date:
                continue
                
            try:
                pub = datetime.strptime(pub_date, '%Y-%m-%d')
                
                if start_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    if pub < start:
                        continue
                        
                if end_date:
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if pub > end:
                        continue
                        
                filtered.append(paper)
                
            except ValueError:
                filtered.append(paper)  # Include if date parsing fails
                
        return filtered


class SemanticScholarWrapper:
    """
    Wrapper for Semantic Scholar API to get citation metrics.
    API: https://api.semanticscholar.org/
    """
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'ResearchIdeationPipeline/1.0'
        }
        if api_key:
            self.headers['x-api-key'] = api_key
        self.session.headers.update(self.headers)
    
    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get paper details and metrics from Semantic Scholar using ArXiv ID.
        """
        # Clean ArXiv ID
        clean_id = arxiv_id.replace('arXiv:', '').strip()
        
        url = f"{self.BASE_URL}/paper/arXiv:{clean_id}"
        params = {
            'fields': 'title,abstract,year,citationCount,influentialCitationCount,referenceCount,fieldsOfStudy,publicationTypes,authors'
        }
        
        try:
            # Rate limiting - be nice to the API
            time.sleep(0.5)
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 404:
                logger.debug(f"[SemanticScholar] Paper not found: {arxiv_id}")
                return None
                
            response.raise_for_status()
            data = response.json()
            
            return {
                'semantic_scholar_id': data.get('paperId'),
                'citation_count': data.get('citationCount', 0),
                'influential_citation_count': data.get('influentialCitationCount', 0),
                'reference_count': data.get('referenceCount', 0),
                'fields_of_study': data.get('fieldsOfStudy', []),
                'year': data.get('year')
            }
            
        except requests.RequestException as e:
            logger.debug(f"[SemanticScholar] API error for {arxiv_id}: {e}")
            return None
    
    def enrich_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Enrich a list of papers with Semantic Scholar metrics.
        """
        enriched = []
        
        for paper in papers:
            arxiv_id = paper.get('arxiv_id')
            if arxiv_id:
                metrics = self.get_paper_by_arxiv_id(arxiv_id)
                if metrics:
                    paper.update(metrics)
            enriched.append(paper)
            
        return enriched
