# 📚 API Documentation & Usage Examples

## 🌐 REST API

### Base URL
```
http://localhost:5000
```

---

## Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "groq_api_configured": true
}
```

---

### 2. Analyze Papers
```http
POST /analyze
Content-Type: multipart/form-data
```

**Request:**
```
paper_a: File (PDF or TXT)
paper_b: File (PDF or TXT)
```

**Response:**
```json
{
  "paper_a": {
    "paper_id": "A",
    "title": "Continual Learning via LoRA",
    "abstract": "...",
    "method": "...",
    "experiments": "...",
    "limitations": "..."
  },
  "paper_b": {
    "paper_id": "B",
    "title": "Subspace Regularization",
    "abstract": "...",
    "method": "...",
    "experiments": "...",
    "limitations": "..."
  },
  "weaknesses_a": [
    "Short task sequence evaluation",
    "No theoretical stability guarantees",
    "Limited memory analysis"
  ],
  "weaknesses_b": [
    "High inference computational cost",
    "Task boundary detection required",
    "Limited domain generalization"
  ],
  "weakness_analysis": {
    "shared": [
      "Lack of theoretical convergence proofs"
    ],
    "paper_a_only": [
      "Short task sequence evaluation"
    ],
    "paper_b_only": [
      "High inference computational cost"
    ]
  },
  "proposed_method": {
    "method_name": "Adaptive Subspace LoRA (AS-LoRA)",
    "core_idea": "Combines low-rank adaptation with dynamic subspace learning...",
    "components": [
      "Task-adaptive rank selection",
      "Shared subspace regularization",
      "Memory-efficient parameter sharing"
    ],
    "addresses_weaknesses": "Eliminates task boundaries while maintaining efficiency..."
  },
  "comparison_table": {
    "Task scalability": {
      "paper_a": "Limited to 5 tasks",
      "paper_b": "Up to 10 tasks with boundaries",
      "proposed": "Unbounded continual learning"
    },
    "Theoretical grounding": {
      "paper_a": "Empirical only",
      "paper_b": "Partial convergence analysis",
      "proposed": "Full stability guarantees"
    },
    "Memory efficiency": {
      "paper_a": "Linear growth uncontrolled",
      "paper_b": "Fixed but high overhead",
      "proposed": "Budget-constrained adaptive"
    },
    "Generalization capability": {
      "paper_a": "Task-specific",
      "paper_b": "Domain-limited",
      "proposed": "Cross-domain via shared subspace"
    }
  }
}
```

**Error Response:**
```json
{
  "error": "Error message here"
}
```

---

## 📝 Usage Examples

### Example 1: cURL

```bash
curl -X POST http://localhost:5000/analyze \
  -F "paper_a=@paper1.pdf" \
  -F "paper_b=@paper2.pdf"
```

### Example 2: Python

```python
import requests

url = "http://localhost:5000/analyze"

files = {
    'paper_a': open('paper1.pdf', 'rb'),
    'paper_b': open('paper2.pdf', 'rb')
}

response = requests.post(url, files=files)
results = response.json()

print("Proposed Method:", results['proposed_method']['method_name'])
print("Core Idea:", results['proposed_method']['core_idea'])
```

### Example 3: JavaScript (Fetch)

```javascript
const formData = new FormData();
formData.append('paper_a', fileInputA.files[0]);
formData.append('paper_b', fileInputB.files[0]);

fetch('http://localhost:5000/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Weaknesses A:', data.weaknesses_a);
  console.log('Weaknesses B:', data.weaknesses_b);
  console.log('Proposed:', data.proposed_method);
});
```

---

## 🎯 Integration Examples

### Example 4: Batch Processing

```python
import os
import requests
import json

def analyze_paper_pair(paper_a_path, paper_b_path):
    """Analyze a pair of papers"""
    url = "http://localhost:5000/analyze"
    
    with open(paper_a_path, 'rb') as fa, open(paper_b_path, 'rb') as fb:
        files = {
            'paper_a': fa,
            'paper_b': fb
        }
        response = requests.post(url, files=files)
    
    return response.json()

# Process multiple pairs
paper_pairs = [
    ('papers/rl_paper1.pdf', 'papers/rl_paper2.pdf'),
    ('papers/nlp_paper1.pdf', 'papers/nlp_paper2.pdf'),
]

results = []
for paper_a, paper_b in paper_pairs:
    print(f"Processing: {paper_a} vs {paper_b}")
    result = analyze_paper_pair(paper_a, paper_b)
    results.append(result)
    
    # Save individual result
    output_file = f"result_{len(results)}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Saved to {output_file}\n")
```

### Example 5: Export to Markdown Report

```python
def generate_markdown_report(results):
    """Convert API results to Markdown report"""
    
    md = f"""# Research Analysis Report

## Papers Analyzed

### Paper A: {results['paper_a']['title']}
### Paper B: {results['paper_b']['title']}

---

## Identified Weaknesses

### Paper A Weaknesses
{chr(10).join(f'- {w}' for w in results['weaknesses_a'])}

### Paper B Weaknesses
{chr(10).join(f'- {w}' for w in results['weaknesses_b'])}

---

## Weakness Pattern Analysis

### Shared Weaknesses
{chr(10).join(f'- {w}' for w in results['weakness_analysis']['shared'])}

### Unique to Paper A
{chr(10).join(f'- {w}' for w in results['weakness_analysis']['paper_a_only'])}

### Unique to Paper B
{chr(10).join(f'- {w}' for w in results['weakness_analysis']['paper_b_only'])}

---

## Proposed Method: {results['proposed_method']['method_name']}

**Core Idea:** {results['proposed_method']['core_idea']}

**Key Components:**
{chr(10).join(f'- {c}' for c in results['proposed_method']['components'])}

**Addresses Weaknesses:** {results['proposed_method']['addresses_weaknesses']}

---

## Comparative Analysis

| Aspect | Paper A | Paper B | Proposed Method |
|--------|---------|---------|-----------------|
"""
    
    for aspect, values in results['comparison_table'].items():
        md += f"| {aspect} | {values['paper_a']} | {values['paper_b']} | {values['proposed']} |\n"
    
    return md

# Usage
results = analyze_paper_pair('paper1.pdf', 'paper2.pdf')
markdown_report = generate_markdown_report(results)

with open('research_report.md', 'w') as f:
    f.write(markdown_report)
```

### Example 6: Web Integration (React)

```jsx
import React, { useState } from 'react';

function ResearchAnalyzer() {
  const [paperA, setPaperA] = useState(null);
  const [paperB, setPaperB] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    
    const formData = new FormData();
    formData.append('paper_a', paperA);
    formData.append('paper_b', paperB);

    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={(e) => setPaperA(e.target.files[0])} 
      />
      <input 
        type="file" 
        onChange={(e) => setPaperB(e.target.files[0])} 
      />
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Papers'}
      </button>

      {results && (
        <div>
          <h2>{results.proposed_method.method_name}</h2>
          <p>{results.proposed_method.core_idea}</p>
          {/* Display full results */}
        </div>
      )}
    </div>
  );
}
```

---

## 🔧 Advanced Configuration

### Custom Groq Settings

You can modify the Groq API settings in `app.py`:

```python
# Change model
MODEL_NAME = "llama-3.3-70b-versatile"  # or other Groq models

# Adjust temperatures for different steps
# Lower = more deterministic, Higher = more creative

# Step 2: Weakness Extraction
temperature=0.3  # Strict and consistent

# Step 3: Normalization
temperature=0.2  # Very deterministic

# Step 5: Method Synthesis
temperature=0.5  # More creative

# Adjust max tokens
max_tokens=2000  # For longer responses
```

---

## 🎨 Customizing Prompts

All prompts are in `app.py`. You can customize them:

```python
class WeaknessExtractor:
    def _extract_from_section(self, section_name: str, text: str):
        prompt = f"""You are a strict conference reviewer.
        
        # Customize this prompt
        Focus on: {custom_focus_areas}
        Ignore: {aspects_to_ignore}
        
        Given the following {section_name} section...
        """
```

---

## 📊 Output Schemas

### Weakness Categories (Customizable)

Default aspects compared:
- Task scalability
- Theoretical grounding
- Memory efficiency
- Generalization capability

Add more in `ComparativeAnalyzer`:

```python
aspects = [
    "Task scalability",
    "Theoretical grounding", 
    "Memory efficiency",
    "Generalization capability",
    "Computational cost",        # New
    "Ease of implementation",    # New
    "Hyperparameter sensitivity" # New
]
```

---

## ⚡ Performance Tips

1. **File Size**: Keep papers under 20 pages for faster processing
2. **Concurrent Requests**: Pipeline is stateless, can handle multiple requests
3. **Caching**: Add Redis for repeated paper pairs
4. **Rate Limiting**: Groq has rate limits, add queuing for high volume

---

## 🐛 Troubleshooting

### Common Issues

**Error: "GROQ_API_KEY not set"**
```bash
export GROQ_API_KEY='your-key-here'
```

**Error: "JSON parse error"**
- LLM returned malformed JSON
- Check prompt clarity
- Reduce max_tokens if truncated

**Error: "File too large"**
```python
# Increase in app.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

**Timeout errors**
```python
# Increase timeout in GroqClient
response = requests.post(..., timeout=60)  # 60 seconds
```

---

## 📈 Monitoring

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# In each step
logging.info(f"Step 1: Parsed paper {paper.title}")
```

### Track Processing Time

```python
import time

start_time = time.time()
results = pipeline.process(pdf_a, pdf_b)
duration = time.time() - start_time

print(f"Processing took {duration:.2f} seconds")
```

---

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
ENV GROQ_API_KEY=""

EXPOSE 5000
CMD ["python", "app.py"]
```

### Deploy Command
```bash
docker build -t research-pipeline .
docker run -p 5000:5000 -e GROQ_API_KEY='your-key' research-pipeline
```

---

**Happy researching! 🎓**
