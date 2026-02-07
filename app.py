"""
AI Research Ideation Pipeline
A Flask application that analyzes SOTA papers and synthesizes new research methods
"""

import os

# Load environment variables from .env file FIRST
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed

import json
import requests
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
import tempfile
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import time

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Enable CORS for frontend on different port
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Groq API Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"  # Fast and capable model

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ParsedPaper:
    """Structured representation of a parsed paper"""
    paper_id: str
    title: str
    abstract: Optional[str]
    method: Optional[str]
    experiments: Optional[str]
    limitations: Optional[str]

@dataclass
class PaperWeaknesses:
    """Weaknesses extracted from a paper"""
    paper_id: str
    weaknesses: List[str]

@dataclass
class WeaknessAnalysis:
    """Categorized weaknesses across papers"""
    shared: List[str]
    paper_a_only: List[str]
    paper_b_only: List[str]

@dataclass
class ProposedMethod:
    """Synthesized new research method"""
    method_name: str
    core_idea: str
    components: List[str]
    addresses_weaknesses: str

# ============================================================================
# GROQ API CLIENT
# ============================================================================

class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[Dict], temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Make a chat completion request to Groq"""
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(GROQ_API_URL, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            raise

# ============================================================================
# STEP 1: PDF PARSING (Simulated GROBID)
# ============================================================================

class PaperParser:
    """Parse papers into structured format"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client
    
    def parse_pdf(self, pdf_path: str, paper_id: str) -> ParsedPaper:
        """
        Parse PDF and extract structured sections
        In production, this would use GROBID. Here we simulate with LLM extraction.
        """
        print(f"\n[DEBUG] Parsing PDF: {pdf_path}")
        text = ""
        
        # Read PDF content (simplified - in production use PyPDF2 or similar)
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"[DEBUG] PDF has {len(pdf_reader.pages)} pages")
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text() or ""
                    text += page_text
                    print(f"[DEBUG] Page {i+1}: extracted {len(page_text)} chars")
            print(f"[DEBUG] Total extracted text: {len(text)} chars")
        except Exception as e:
            print(f"[DEBUG] PyPDF2 failed: {e}, trying as text file...")
            # Fallback: treat as text file for demo
            try:
                with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                print(f"[DEBUG] Read as text file: {len(text)} chars")
            except Exception as e2:
                print(f"[DEBUG] Text file read also failed: {e2}")
        
        if len(text) < 100:
            print(f"[WARNING] Very little text extracted ({len(text)} chars). PDF may be scanned/image-based.")
            print(f"[DEBUG] First 500 chars: {text[:500]}")
        
        # Extract sections using LLM
        prompt = f"""Extract the following sections from this research paper. Return ONLY valid JSON.

Paper text:
{text[:8000]}  

Return format:
{{
  "title": "paper title or null",
  "abstract": "abstract text or null",
  "method": "methodology section or null",
  "experiments": "experimental results section or null",
  "limitations": "limitations/discussion section or null"
}}

Rules:
- If section not found, use null
- Do not infer missing content
- Extract verbatim text"""

        messages = [{"role": "user", "content": prompt}]
        response = self.groq.chat_completion(messages, temperature=0.1, max_tokens=3000)
        
        print(f"[DEBUG] LLM response length: {len(response)} chars")
        print(f"[DEBUG] LLM response preview: {response[:300]}...")
        
        # Parse JSON response
        try:
            # Clean response to extract JSON
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            data = json.loads(response)
            print(f"[DEBUG] Parsed paper '{paper_id}':")
            print(f"  - Title: {data.get('title', 'None')[:50] if data.get('title') else 'None'}...")
            print(f"  - Abstract: {'Yes' if data.get('abstract') else 'No'} ({len(data.get('abstract') or '')} chars)")
            print(f"  - Method: {'Yes' if data.get('method') else 'No'} ({len(data.get('method') or '')} chars)")
            print(f"  - Experiments: {'Yes' if data.get('experiments') else 'No'} ({len(data.get('experiments') or '')} chars)")
            print(f"  - Limitations: {'Yes' if data.get('limitations') else 'No'} ({len(data.get('limitations') or '')} chars)")
            
            return ParsedPaper(
                paper_id=paper_id,
                title=data.get('title'),
                abstract=data.get('abstract'),
                method=data.get('method'),
                experiments=data.get('experiments'),
                limitations=data.get('limitations')
            )
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse error: {e}")
            print(f"[DEBUG] Raw response: {response[:500]}")
            # Return minimal structure with abstract as fallback for method
            return ParsedPaper(
                paper_id=paper_id,
                title="Unknown",
                abstract=text[:500] if text else None,
                method=text[:2000] if text else None,  # Use raw text as method fallback
                experiments=None,
                limitations=None
            )

# ============================================================================
# STEP 2: WEAKNESS EXTRACTION
# ============================================================================

class WeaknessExtractor:
    """Extract weaknesses from parsed papers"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client
    
    def extract_from_paper(self, paper: ParsedPaper) -> PaperWeaknesses:
        """Extract weaknesses from all sections of a paper"""
        all_weaknesses = []
        
        print(f"\n[DEBUG] Extracting weaknesses from paper {paper.paper_id}...")
        
        # Extract from each section
        sections = {
            'method': paper.method,
            'experiments': paper.experiments,
            'limitations': paper.limitations,
            'abstract': paper.abstract  # Also analyze abstract!
        }
        
        sections_found = 0
        for section_name, section_text in sections.items():
            if section_text and len(section_text) > 50:
                sections_found += 1
                print(f"[DEBUG] Analyzing {section_name} section ({len(section_text)} chars)...")
                weaknesses = self._extract_from_section(section_name, section_text)
                print(f"[DEBUG] Found {len(weaknesses)} weaknesses in {section_name}")
                all_weaknesses.extend(weaknesses)
            else:
                print(f"[DEBUG] Skipping {section_name} (empty or too short)")
        
        print(f"[DEBUG] Total sections analyzed: {sections_found}, Total weaknesses: {len(all_weaknesses)}")
        
        # If no weaknesses found and we have abstract, force extract from abstract
        if not all_weaknesses and paper.abstract:
            print(f"[DEBUG] No weaknesses found, forcing analysis on abstract...")
            weaknesses = self._extract_from_section('paper_content', paper.abstract)
            all_weaknesses.extend(weaknesses)
        
        return PaperWeaknesses(paper_id=paper.paper_id, weaknesses=all_weaknesses)
    
    def _extract_from_section(self, section_name: str, text: str) -> List[str]:
        """Extract weaknesses from a single section"""
        prompt = f"""You are an expert academic paper reviewer analyzing a research paper.

Given the following {section_name} section of a research paper, identify potential weaknesses, limitations, gaps, or areas that could be improved.

Section text:
{text[:3000]}

IMPORTANT: You MUST identify at least 2-3 potential weaknesses. Every research paper has limitations.

Consider these types of weaknesses:
- Methodological limitations (small sample size, limited scope, specific assumptions)
- Scalability concerns
- Generalization issues (tested on limited domains/datasets)
- Missing comparisons or baselines
- Theoretical gaps
- Computational/resource requirements
- Evaluation limitations

Return your response as a bullet-point list:
- [First weakness or limitation]
- [Second weakness or limitation]
- [Third weakness or limitation]

If you truly cannot identify any weaknesses, explain why in a bullet point."""

        messages = [{"role": "user", "content": prompt}]
        response = self.groq.chat_completion(messages, temperature=0.4, max_tokens=1000)
        
        print(f"[DEBUG] Weakness extraction response preview: {response[:200]}...")
        
        # Parse bullet points (handle both - and • and numbered lists)
        weaknesses = []
        for line in response.split('\n'):
            line = line.strip()
            # Match bullet points, numbered lists, or asterisks
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                weakness = line.lstrip('-•*').strip()
                if weakness and weakness.lower() not in ['none', 'n/a', 'not applicable']:
                    weaknesses.append(weakness)
            elif len(line) > 2 and line[0].isdigit() and (line[1] == '.' or line[1] == ')'):
                weakness = line[2:].strip()
                if weakness and weakness.lower() not in ['none', 'n/a']:
                    weaknesses.append(weakness)
        
        print(f"[DEBUG] Parsed {len(weaknesses)} weaknesses from response")
        return weaknesses

# ============================================================================
# STEP 3: WEAKNESS NORMALIZATION
# ============================================================================

class WeaknessNormalizer:
    """Normalize and canonicalize weaknesses"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client
    
    def normalize(self, weaknesses: List[str]) -> List[str]:
        """Group and canonicalize weaknesses"""
        if not weaknesses:
            return []
        
        weaknesses_text = '\n'.join(f"- {w}" for w in weaknesses)
        
        prompt = f"""You are an academic paper reviewer. Rephrase and consolidate the following weaknesses into clear, readable academic language.

Raw weaknesses identified:
{weaknesses_text}

Instructions:
1. Merge similar or duplicate weaknesses
2. Use clear, complete sentences (NOT CamelCase or abbreviations)
3. Each weakness should be a standalone, understandable statement
4. Use professional academic language (e.g., "Limited evaluation across diverse datasets" NOT "LimitedDatasetEvaluation")
5. Keep each weakness concise but informative (10-20 words)
6. Return 3-6 consolidated weaknesses maximum

Format your response as:
- [Clear weakness description 1]
- [Clear weakness description 2]
- [Clear weakness description 3]

Example good format:
- Absence of computational complexity or resource requirement analysis
- Limited evaluation scope restricted to specific benchmark datasets
- Insufficient discussion of algorithmic trade-offs and failure modes"""

        messages = [{"role": "user", "content": prompt}]
        response = self.groq.chat_completion(messages, temperature=0.2, max_tokens=800)
        
        print(f"[DEBUG] Normalization response: {response[:200]}...")
        
        # Parse normalized weaknesses
        normalized = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                weakness = line.lstrip('-•*').strip()
                if weakness and len(weakness) > 10:
                    normalized.append(weakness)
        
        return normalized

# ============================================================================
# STEP 4: WEAKNESS FUSION & GAP ANALYSIS
# ============================================================================

class WeaknessFusion:
    """Analyze and categorize weaknesses across papers"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client
    
    def analyze(self, weaknesses_a: List[str], weaknesses_b: List[str]) -> WeaknessAnalysis:
        """Identify shared and unique weaknesses"""
        prompt = f"""Compare these two lists of research paper weaknesses.
Identify:
1. Shared weaknesses (present in both)
2. Weaknesses unique to Paper A
3. Weaknesses unique to Paper B

Paper A weaknesses:
{chr(10).join(f"- {w}" for w in weaknesses_a)}

Paper B weaknesses:
{chr(10).join(f"- {w}" for w in weaknesses_b)}

Return ONLY valid JSON:
{{
  "shared": ["weakness 1", "weakness 2"],
  "paper_a_only": ["weakness 1"],
  "paper_b_only": ["weakness 1"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.groq.chat_completion(messages, temperature=0.2, max_tokens=1500)
        
        # Parse JSON
        try:
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            data = json.loads(response)
            return WeaknessAnalysis(
                shared=data.get('shared', []),
                paper_a_only=data.get('paper_a_only', []),
                paper_b_only=data.get('paper_b_only', [])
            )
        except:
            # Fallback to simple set operations
            set_a = set(weaknesses_a)
            set_b = set(weaknesses_b)
            return WeaknessAnalysis(
                shared=list(set_a & set_b),
                paper_a_only=list(set_a - set_b),
                paper_b_only=list(set_b - set_a)
            )

# ============================================================================
# STEP 5: NEW METHOD SYNTHESIS
# ============================================================================

class MethodSynthesizer:
    """Synthesize new research methods addressing identified weaknesses"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client
    
    def synthesize(self, analysis: WeaknessAnalysis, paper_a_title: str, paper_b_title: str) -> ProposedMethod:
        """Generate a new method addressing the weaknesses"""
        
        # Combine all weaknesses for context
        all_weaknesses = analysis.shared + analysis.paper_a_only + analysis.paper_b_only
        
        prompt = f"""You are a senior research scientist proposing a novel method for an academic paper.

=== CONTEXT ===
Paper A: "{paper_a_title}"
Paper B: "{paper_b_title}"

=== IDENTIFIED WEAKNESSES TO ADDRESS ===
Shared limitations (both papers):
{chr(10).join(f"• {w}" for w in analysis.shared) if analysis.shared else "• No shared weaknesses identified"}

Paper A specific limitations:
{chr(10).join(f"• {w}" for w in analysis.paper_a_only) if analysis.paper_a_only else "• No unique weaknesses"}

Paper B specific limitations:
{chr(10).join(f"• {w}" for w in analysis.paper_b_only) if analysis.paper_b_only else "• No unique weaknesses"}

=== YOUR TASK ===
Propose a novel hybrid method that:
1. Combines the strengths of both papers
2. Explicitly addresses the identified weaknesses
3. Is practically implementable without new datasets

=== NAMING GUIDELINES ===
- Use a descriptive, memorable name (e.g., "Adaptive Unified Framework", "Hierarchical Hybrid Architecture")
- Avoid generic names like "New Method" or "Hybrid Approach"
- Format: "[Adjective] [Core Concept] [Type]" (e.g., "Robust Multi-Scale Fusion Network")

=== OUTPUT FORMAT ===
Return ONLY valid JSON:
{{
  "method_name": "Your Descriptive Method Name",
  "core_idea": "A clear 2-3 sentence description of the method's key innovation and how it works. Write in academic style.",
  "components": [
    "Component 1: Brief description of what it does",
    "Component 2: Brief description of what it does",
    "Component 3: Brief description of what it does",
    "Component 4: Brief description of what it does"
  ],
  "addresses_weaknesses": "A paragraph explaining specifically how this method addresses each major weakness identified above. Be concrete and reference the components."
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.groq.chat_completion(messages, temperature=0.5, max_tokens=2500)
        
        print(f"[DEBUG] Method synthesis response preview: {response[:300]}...")
        
        # Parse JSON
        try:
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            data = json.loads(response)
            return ProposedMethod(
                method_name=data.get('method_name', 'Unified Adaptive Framework'),
                core_idea=data.get('core_idea', ''),
                components=data.get('components', []),
                addresses_weaknesses=data.get('addresses_weaknesses', '')
            )
        except Exception as e:
            print(f"[ERROR] Parsing method synthesis: {e}")
            return ProposedMethod(
                method_name="Unified Adaptive Hybrid Framework",
                core_idea="A method that combines the complementary strengths of both analyzed approaches while introducing novel components to address identified limitations.",
                components=[
                    "Adaptive Integration Module: Dynamically combines features from both paradigms",
                    "Scalability Enhancement Layer: Addresses computational efficiency concerns",
                    "Generalization Mechanism: Improves cross-domain applicability",
                    "Theoretical Grounding: Provides formal convergence guarantees"
                ],
                addresses_weaknesses="This framework addresses the identified weaknesses through its modular design that allows for flexible adaptation to different scenarios while maintaining theoretical soundness."
            )

# ============================================================================
# STEP 6 & 7: COMPARATIVE ANALYSIS
# ============================================================================

class ComparativeAnalyzer:
    """Generate comparative analysis and table"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client
    
    def generate_comparison(self, 
                          paper_a: ParsedPaper,
                          paper_b: ParsedPaper,
                          weaknesses_a: List[str],
                          weaknesses_b: List[str],
                          proposed: ProposedMethod) -> Dict:
        """Generate comprehensive comparison"""
        
        aspects = [
            "Task Scalability",
            "Theoretical Foundation",
            "Computational Efficiency",
            "Generalization Capability",
            "Practical Applicability"
        ]
        
        prompt = f"""You are writing a comparative analysis table for an academic paper.

Compare the following three approaches. Write DETAILED, READABLE assessments (not single words).

=== PAPER A ===
Title: {paper_a.title or 'Untitled Paper A'}
Key Limitations: {'; '.join(weaknesses_a[:4]) if weaknesses_a else 'Not specified'}

=== PAPER B ===
Title: {paper_b.title or 'Untitled Paper B'}
Key Limitations: {'; '.join(weaknesses_b[:4]) if weaknesses_b else 'Not specified'}

=== PROPOSED METHOD ===
Name: {proposed.method_name}
Core Idea: {proposed.core_idea}
Key Components: {', '.join(proposed.components)}

=== COMPARISON ASPECTS ===
{chr(10).join(f"- {a}" for a in aspects)}

IMPORTANT INSTRUCTIONS:
1. Each assessment should be 8-15 words (complete sentences or phrases)
2. Be specific about WHY something is limited or enhanced
3. For proposed method, highlight improvements over both papers
4. Do NOT use single words like "Limited" or "Good"
5. If information is missing, write "Requires further empirical validation" instead of "No information"

Example good assessments:
- "Evaluated on 3 benchmark datasets; scalability to larger tasks untested"
- "Strong theoretical grounding with formal convergence guarantees"
- "Explicitly optimized for memory efficiency through sparse representations"

Return ONLY valid JSON in this exact format:
{{
  "Task Scalability": {{
    "paper_a": "detailed assessment here",
    "paper_b": "detailed assessment here",
    "proposed": "detailed assessment showing improvement"
  }},
  "Theoretical Foundation": {{
    "paper_a": "detailed assessment",
    "paper_b": "detailed assessment",
    "proposed": "detailed assessment"
  }},
  "Computational Efficiency": {{
    "paper_a": "detailed assessment",
    "paper_b": "detailed assessment", 
    "proposed": "detailed assessment"
  }},
  "Generalization Capability": {{
    "paper_a": "detailed assessment",
    "paper_b": "detailed assessment",
    "proposed": "detailed assessment"
  }},
  "Practical Applicability": {{
    "paper_a": "detailed assessment",
    "paper_b": "detailed assessment",
    "proposed": "detailed assessment"
  }}
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.groq.chat_completion(messages, temperature=0.3, max_tokens=2500)
        
        print(f"[DEBUG] Comparison response preview: {response[:300]}...")
        
        # Parse JSON
        try:
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            comparison = json.loads(response)
            return comparison
        except Exception as e:
            print(f"[ERROR] Failed to parse comparison JSON: {e}")
            # Return detailed default structure
            return {aspect: {
                "paper_a": "Analysis based on identified limitations shows room for improvement",
                "paper_b": "Moderate performance with some documented constraints", 
                "proposed": "Designed to address identified gaps through hybrid approach"
            } for aspect in aspects}

# ============================================================================
# MAIN PIPELINE ORCHESTRATOR
# ============================================================================

class ResearchPipeline:
    """Main pipeline orchestrating all steps"""
    
    def __init__(self, groq_api_key: str):
        self.groq = GroqClient(groq_api_key)
        self.parser = PaperParser(self.groq)
        self.weakness_extractor = WeaknessExtractor(self.groq)
        self.weakness_normalizer = WeaknessNormalizer(self.groq)
        self.weakness_fusion = WeaknessFusion(self.groq)
        self.method_synthesizer = MethodSynthesizer(self.groq)
        self.comparative_analyzer = ComparativeAnalyzer(self.groq)
    
    def process(self, pdf_a_path: str, pdf_b_path: str) -> Dict:
        """Run the complete pipeline"""
        results = {}
        
        # Step 1: Parse papers
        print("Step 1: Parsing papers...")
        paper_a = self.parser.parse_pdf(pdf_a_path, "A")
        paper_b = self.parser.parse_pdf(pdf_b_path, "B")
        results['paper_a'] = asdict(paper_a)
        results['paper_b'] = asdict(paper_b)
        
        # Step 2: Extract weaknesses
        print("Step 2: Extracting weaknesses...")
        weaknesses_a = self.weakness_extractor.extract_from_paper(paper_a)
        weaknesses_b = self.weakness_extractor.extract_from_paper(paper_b)
        
        # Step 3: Normalize weaknesses
        print("Step 3: Normalizing weaknesses...")
        normalized_a = self.weakness_normalizer.normalize(weaknesses_a.weaknesses)
        normalized_b = self.weakness_normalizer.normalize(weaknesses_b.weaknesses)
        results['weaknesses_a'] = normalized_a
        results['weaknesses_b'] = normalized_b
        
        # Step 4: Weakness fusion
        print("Step 4: Analyzing weakness patterns...")
        analysis = self.weakness_fusion.analyze(normalized_a, normalized_b)
        results['weakness_analysis'] = asdict(analysis)
        
        # Step 5: Synthesize new method
        print("Step 5: Synthesizing new method...")
        proposed = self.method_synthesizer.synthesize(
            analysis, 
            paper_a.title or "Paper A",
            paper_b.title or "Paper B"
        )
        results['proposed_method'] = asdict(proposed)
        
        # Step 6 & 7: Comparative analysis
        print("Step 6: Generating comparative analysis...")
        comparison = self.comparative_analyzer.generate_comparison(
            paper_a, paper_b, normalized_a, normalized_b, proposed
        )
        results['comparison_table'] = comparison
        
        return results

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render main UI"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Research Ideation Pipeline</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .upload-section {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }
            .file-input-wrapper {
                margin-bottom: 20px;
            }
            label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #444;
            }
            input[type="file"] {
                width: 100%;
                padding: 12px;
                border: 2px dashed #ddd;
                border-radius: 8px;
                background: white;
                cursor: pointer;
            }
            input[type="file"]:hover {
                border-color: #667eea;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s;
                width: 100%;
            }
            button:hover:not(:disabled) {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            #results {
                margin-top: 30px;
            }
            .result-section {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 12px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .result-section h3 {
                color: #333;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }
            .result-section h3::before {
                content: '🔍';
                margin-right: 10px;
            }
            .weakness-list {
                list-style: none;
                padding-left: 0;
            }
            .weakness-list li {
                padding: 10px;
                margin-bottom: 8px;
                background: white;
                border-radius: 6px;
                border-left: 3px solid #ff6b6b;
            }
            .proposed-method {
                background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                padding: 25px;
                border-radius: 12px;
                margin: 20px 0;
            }
            .proposed-method h2 {
                color: #667eea;
                margin-bottom: 15px;
            }
            .component-list li {
                padding: 10px;
                margin-bottom: 8px;
                background: white;
                border-radius: 6px;
                border-left: 3px solid #51cf66;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background: white;
                border-radius: 8px;
                overflow: hidden;
            }
            th, td {
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }
            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: 600;
            }
            tr:hover {
                background: #f8f9fa;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 1.2em;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 AI Research Ideation Pipeline</h1>
            <p class="subtitle">Analyze SOTA papers, extract weaknesses, and synthesize novel research methods</p>
            
            <div class="upload-section">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="file-input-wrapper">
                        <label for="paper_a">📄 SOTA Paper A (PDF)</label>
                        <input type="file" id="paper_a" name="paper_a" accept=".pdf,.txt" required>
                    </div>
                    
                    <div class="file-input-wrapper">
                        <label for="paper_b">📄 SOTA Paper B (PDF)</label>
                        <input type="file" id="paper_b" name="paper_b" accept=".pdf,.txt" required>
                    </div>
                    
                    <button type="submit" id="submitBtn">🚀 Analyze & Synthesize</button>
                </form>
            </div>
            
            <div id="results"></div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const submitBtn = document.getElementById('submitBtn');
                const resultsDiv = document.getElementById('results');
                
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Processing...';
                resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Running research pipeline... This may take 2-3 minutes.</div>';
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<div class="result-section" style="border-left-color: #ff6b6b;"><h3>❌ Error</h3><p>${data.error}</p></div>`;
                    } else {
                        displayResults(data);
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="result-section" style="border-left-color: #ff6b6b;"><h3>❌ Error</h3><p>${error.message}</p></div>`;
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Analyze & Synthesize';
                }
            });
            
            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                
                let html = '<h2 style="margin-bottom: 20px;">📊 Analysis Results</h2>';
                
                // Paper summaries
                html += `
                    <div class="result-section">
                        <h3>📄 Paper A: ${data.paper_a.title || 'Unknown'}</h3>
                    </div>
                    
                    <div class="result-section">
                        <h3>📄 Paper B: ${data.paper_b.title || 'Unknown'}</h3>
                    </div>
                `;
                
                // Weaknesses
                html += `
                    <div class="result-section">
                        <h3>⚠️ Weaknesses of Paper A</h3>
                        <ul class="weakness-list">
                            ${data.weaknesses_a.map(w => `<li>${w}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="result-section">
                        <h3>⚠️ Weaknesses of Paper B</h3>
                        <ul class="weakness-list">
                            ${data.weaknesses_b.map(w => `<li>${w}</li>`).join('')}
                        </ul>
                    </div>
                `;
                
                // Weakness Analysis
                const analysis = data.weakness_analysis;
                html += `
                    <div class="result-section">
                        <h3>🔄 Weakness Pattern Analysis</h3>
                        <p><strong>Shared weaknesses:</strong></p>
                        <ul class="weakness-list">
                            ${analysis.shared.map(w => `<li>${w}</li>`).join('') || '<li>None identified</li>'}
                        </ul>
                        <p style="margin-top: 15px;"><strong>Unique to Paper A:</strong></p>
                        <ul class="weakness-list">
                            ${analysis.paper_a_only.map(w => `<li>${w}</li>`).join('') || '<li>None identified</li>'}
                        </ul>
                        <p style="margin-top: 15px;"><strong>Unique to Paper B:</strong></p>
                        <ul class="weakness-list">
                            ${analysis.paper_b_only.map(w => `<li>${w}</li>`).join('') || '<li>None identified</li>'}
                        </ul>
                    </div>
                `;
                
                // Proposed Method
                const method = data.proposed_method;
                html += `
                    <div class="proposed-method">
                        <h2>💡 ${method.method_name}</h2>
                        <p style="margin: 15px 0; line-height: 1.6;"><strong>Core Idea:</strong> ${method.core_idea}</p>
                        <p><strong>Key Components:</strong></p>
                        <ul class="component-list">
                            ${method.components.map(c => `<li>${c}</li>`).join('')}
                        </ul>
                        <p style="margin-top: 15px; line-height: 1.6;"><strong>Addresses Weaknesses:</strong> ${method.addresses_weaknesses}</p>
                    </div>
                `;
                
                // Comparison Table
                html += `
                    <div class="result-section">
                        <h3>📊 Comparative Analysis</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Aspect</th>
                                    <th>Paper A</th>
                                    <th>Paper B</th>
                                    <th>Proposed Method</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                for (const [aspect, values] of Object.entries(data.comparison_table)) {
                    html += `
                        <tr>
                            <td><strong>${aspect}</strong></td>
                            <td>${values.paper_a || 'N/A'}</td>
                            <td>${values.paper_b || 'N/A'}</td>
                            <td>${values.proposed || 'N/A'}</td>
                        </tr>
                    `;
                }
                
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
                
                resultsDiv.innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        # Check for API key
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not set in environment variables'}), 500
        
        # Get uploaded files
        if 'paper_a' not in request.files or 'paper_b' not in request.files:
            return jsonify({'error': 'Both paper files are required'}), 400
        
        paper_a = request.files['paper_a']
        paper_b = request.files['paper_b']
        
        if paper_a.filename == '' or paper_b.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Save files temporarily
        temp_dir = tempfile.mkdtemp()
        paper_a_path = os.path.join(temp_dir, secure_filename(paper_a.filename))
        paper_b_path = os.path.join(temp_dir, secure_filename(paper_b.filename))
        
        paper_a.save(paper_a_path)
        paper_b.save(paper_b_path)
        
        # Run pipeline
        pipeline = ResearchPipeline(GROQ_API_KEY)
        results = pipeline.process(paper_a_path, paper_b_path)
        
        # Cleanup
        os.remove(paper_a_path)
        os.remove(paper_b_path)
        os.rmdir(temp_dir)
        
        return jsonify(results)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'groq_api_configured': bool(GROQ_API_KEY),
        'groq_api_key_length': len(GROQ_API_KEY) if GROQ_API_KEY else 0,
        'model': MODEL_NAME
    })

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to test configuration"""
    result = {
        'api_key_set': bool(GROQ_API_KEY),
        'api_key_preview': f"{GROQ_API_KEY[:10]}..." if GROQ_API_KEY else "NOT SET",
        'model': MODEL_NAME,
        'test_connection': False,
        'test_response': None
    }
    
    # Test Groq connection
    if GROQ_API_KEY:
        try:
            groq = GroqClient(GROQ_API_KEY)
            response = groq.chat_completion(
                [{"role": "user", "content": "Say 'API working' and nothing else"}],
                temperature=0.1,
                max_tokens=20
            )
            result['test_connection'] = True
            result['test_response'] = response
        except Exception as e:
            result['test_error'] = str(e)
    
    return jsonify(result)

# ============================================================================
# SOTA IDENTIFICATION ENDPOINT
# ============================================================================

@app.route('/sota', methods=['POST', 'OPTIONS'])
def identify_sota():
    """
    Identify top SOTA papers for a given research topic.
    
    Request body:
    {
        "topic": "research topic description",
        "top_k": 2,  // optional, default 2
        "max_results": 20,  // optional, default 20
        "start_date": "2023-01-01",  // optional
        "end_date": "2024-12-31"  // optional
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check for API key
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not set in environment variables'}), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Research topic is required'}), 400
        
        # Optional parameters
        top_k = min(int(data.get('top_k', 2)), 10)  # Max 10 papers
        max_results = min(int(data.get('max_results', 20)), 50)  # Max 50 candidates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        print(f"\n[SOTA API] Searching for: {topic}")
        print(f"[SOTA API] Parameters: top_k={top_k}, max_results={max_results}")
        
        # Import and run SOTA identifier
        from services.sota_identifier import SOTAIdentifier
        
        identifier = SOTAIdentifier(GROQ_API_KEY)
        results = identifier.identify_sota(
            topic=topic,
            max_results=max_results,
            top_k=top_k,
            start_date=start_date,
            end_date=end_date,
            include_metrics=True
        )
        
        print(f"[SOTA API] Found {len(results.get('sota_papers', []))} SOTA papers")
        
        return jsonify(results)
        
    except Exception as e:
        import traceback
        print(f"[SOTA API] Error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/sota/quick', methods=['GET'])
def quick_sota():
    """
    Quick SOTA search via GET request.
    Usage: /sota/quick?topic=transformer+attention&top_k=2
    """
    try:
        topic = request.args.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'topic parameter is required'}), 400
        
        top_k = min(int(request.args.get('top_k', 2)), 5)
        
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not configured'}), 500
        
        from services.sota_identifier import SOTAIdentifier
        
        identifier = SOTAIdentifier(GROQ_API_KEY)
        results = identifier.identify_sota(
            topic=topic,
            max_results=15,
            top_k=top_k,
            include_metrics=True
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🧠 AI Research Ideation Pipeline")
    print("=" * 60)
    print(f"Groq API configured: {bool(GROQ_API_KEY)}")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)
    
    if not GROQ_API_KEY:
        print("\n⚠️  WARNING: GROQ_API_KEY not set!")
        print("Set it with: export GROQ_API_KEY='your-key-here'")
        print()
    
    app.run(debug=True, host='0.0.0.0', port=9001)
