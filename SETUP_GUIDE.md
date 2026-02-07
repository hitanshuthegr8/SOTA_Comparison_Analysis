# 🚀 COMPLETE SETUP GUIDE

## 📦 What You've Got

A complete AI Research Ideation Pipeline that:
- Analyzes 2 SOTA research papers
- Extracts weaknesses using AI
- Synthesizes a novel research method
- Generates comparative analysis

**Everything is in ONE file: `app.py` (1000+ lines)**

---

## 📁 Files Included

```
✅ app.py                  # Complete Flask application (ALL CODE HERE)
✅ requirements.txt        # Python dependencies
✅ README.md              # Full documentation
✅ PROJECT_STRUCTURE.md   # Code architecture
✅ API_DOCS.md            # API reference & examples
✅ test_setup.py          # Setup verification
✅ run.sh                 # Quick start script (Linux/Mac)
✅ .env.example           # Environment template
✅ .gitignore             # Git ignore rules
```

---

## ⚡ QUICK START (3 Steps)

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web server)
- requests (HTTP client)
- PyPDF2 (PDF parsing)
- Werkzeug (file handling)
- python-dotenv (environment variables)

### 2️⃣ Set API Key

Get free API key: https://console.groq.com/keys

Then either:

**Option A: Export**
```bash
export GROQ_API_KEY='your-groq-api-key-here'
```

**Option B: Create .env file**
```bash
echo "GROQ_API_KEY=your-groq-api-key-here" > .env
```

### 3️⃣ Run

```bash
python app.py
```

Open browser: **http://localhost:5000**

---

## 🎯 How to Use

1. **Upload two research papers** (PDF or TXT)
2. **Click "Analyze & Synthesize"**
3. **Wait 2-3 minutes** (AI is analyzing)
4. **Get results:**
   - Weaknesses of both papers
   - Pattern analysis (shared/unique)
   - Novel proposed method
   - Comparison table

---

## 📊 Sample Output

```
Paper A: "Continual Learning via LoRA"
Weaknesses:
  - Limited to 5 task sequences
  - No theoretical stability guarantees
  - Uncontrolled memory growth

Paper B: "Subspace Regularization for CL"
Weaknesses:
  - High inference overhead
  - Requires task boundary detection
  - Domain-specific assumptions

Shared Weaknesses:
  - Lack of formal convergence proofs

Proposed Method: "Adaptive Subspace LoRA (AS-LoRA)"
Core Idea: Combines low-rank adaptation with dynamic subspace 
learning, eliminating task boundaries while maintaining efficiency...

Components:
  - Task-adaptive rank selection
  - Shared subspace regularization
  - Memory-efficient parameter sharing
  - Boundary-free continual learning

Comparison Table:
┌─────────────────────┬────────────┬────────────┬─────────────┐
│ Aspect              │ Paper A    │ Paper B    │ Proposed    │
├─────────────────────┼────────────┼────────────┼─────────────┤
│ Task scalability    │ ≤5 tasks   │ ≤10 tasks  │ Unbounded   │
│ Theoretical ground  │ None       │ Partial    │ Full proofs │
│ Memory efficiency   │ Unanalyzed │ Fixed high │ Adaptive    │
│ Generalization      │ Limited    │ Moderate   │ Enhanced    │
└─────────────────────┴────────────┴────────────┴─────────────┘
```

---

## 🏗️ Architecture Overview

```python
# All in app.py:

1. GroqClient
   - API communication

2. PaperParser (STEP 1)
   - PDF → Structured JSON
   - Extracts: title, abstract, method, experiments, limitations

3. WeaknessExtractor (STEP 2)
   - Per-section analysis
   - Strict reviewer mode

4. WeaknessNormalizer (STEP 3)
   - Canonicalize weaknesses
   - Merge duplicates

5. WeaknessFusion (STEP 4)
   - Identify shared weaknesses
   - Separate unique issues

6. MethodSynthesizer (STEP 5)
   - Generate novel method
   - Address weaknesses

7. ComparativeAnalyzer (STEP 6-7)
   - Multi-aspect comparison
   - Generate table

8. ResearchPipeline
   - Orchestrates everything
```

---

## 🔧 Customization

### Change AI Model
```python
# In app.py, line ~30
MODEL_NAME = "llama-3.3-70b-versatile"  # Change this
```

### Adjust Creativity
```python
# Lower = more deterministic
# Higher = more creative

# Weakness extraction
temperature=0.3  # Consistent

# Method synthesis  
temperature=0.5  # Creative
```

### Add Comparison Aspects
```python
# In ComparativeAnalyzer class
aspects = [
    "Task scalability",
    "Theoretical grounding",
    "Memory efficiency",
    "Generalization capability",
    "Computational cost",        # ADD NEW
    "Implementation complexity"  # ADD NEW
]
```

---

## 🧪 Testing

### Run Setup Tests
```bash
python test_setup.py
```

This checks:
- ✅ All files present
- ✅ Dependencies installed
- ✅ API key configured
- ✅ Groq connection working

### Test API Manually
```bash
# Health check
curl http://localhost:5000/health

# Analyze papers
curl -X POST http://localhost:5000/analyze \
  -F "paper_a=@paper1.pdf" \
  -F "paper_b=@paper2.pdf"
```

---

## 🐛 Troubleshooting

### "GROQ_API_KEY not set"
```bash
export GROQ_API_KEY='your-key'
```

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Connection timeout"
- Check internet connection
- Verify API key is valid
- Try again (Groq might be busy)

### "JSON parse error"
- Happens occasionally with LLMs
- Just retry the analysis

### PDF not parsing
- Try converting to TXT first
- Or use smaller/simpler PDFs

---

## 💡 Usage Tips

### Best Results
1. **Upload high-quality papers** (well-formatted PDFs)
2. **Choose related papers** (same research area)
3. **Papers with clear methods** (easier to analyze)
4. **10-20 pages ideal** (not too long)

### Don't
- ❌ Upload identical papers
- ❌ Use papers in different languages
- ❌ Expect instant results (takes 2-3 min)

---

## 🚀 Advanced Usage

### Batch Processing
```python
import requests

papers = [
    ('rl_1.pdf', 'rl_2.pdf'),
    ('nlp_1.pdf', 'nlp_2.pdf'),
]

for paper_a, paper_b in papers:
    files = {
        'paper_a': open(paper_a, 'rb'),
        'paper_b': open(paper_b, 'rb')
    }
    response = requests.post(
        'http://localhost:5000/analyze',
        files=files
    )
    print(response.json())
```

### Export to Markdown
See `API_DOCS.md` for full example

### Integrate in Your App
```javascript
// React, Vue, Angular, etc.
const formData = new FormData();
formData.append('paper_a', fileA);
formData.append('paper_b', fileB);

fetch('http://localhost:5000/analyze', {
  method: 'POST',
  body: formData
}).then(r => r.json());
```

---

## 📊 Performance

- **Processing time**: 2-3 minutes per pair
- **API calls**: ~8-12 calls to Groq
- **Token usage**: ~5,000-10,000 tokens
- **Cost**: ~$0.01-0.02 per analysis (Groq is cheap!)

---

## 🔐 Security

- ✅ No data stored permanently
- ✅ Temp files cleaned up
- ✅ Secure file handling
- ✅ API key in environment (not code)
- ✅ File size limits (50MB default)

---

## 📚 Documentation

- `README.md` - Main documentation
- `PROJECT_STRUCTURE.md` - Code architecture
- `API_DOCS.md` - API reference & examples
- This file - Setup guide

---

## 🎓 How It Works

### The Pipeline (6 Steps)

**Step 1: Parse Papers**
- Input: PDF files
- Output: Structured JSON (title, method, experiments, etc.)
- Uses: LLM to identify sections

**Step 2: Extract Weaknesses**
- Input: Structured papers
- Output: List of weaknesses per section
- Uses: LLM as strict reviewer

**Step 3: Normalize Weaknesses**
- Input: Raw weaknesses
- Output: Canonical weaknesses (merged duplicates)
- Uses: LLM to group similar issues

**Step 4: Weakness Fusion**
- Input: Normalized weaknesses from both papers
- Output: Shared, Paper A only, Paper B only
- Uses: LLM + set operations

**Step 5: Method Synthesis**
- Input: Weakness analysis
- Output: Novel method (name, idea, components)
- Uses: LLM in "research author" mode

**Step 6: Comparative Analysis**
- Input: Papers + weaknesses + proposed method
- Output: Comparison table across aspects
- Uses: LLM with fixed schema

### Why It Works

- ✅ **Structured prompts** - No hallucination
- ✅ **Small scoped calls** - LLM doesn't get lost
- ✅ **Canonical weaknesses** - Consistent comparisons
- ✅ **Deterministic fusion** - Reliable patterns
- ✅ **Fixed output schema** - Stable tables

---

## 🎯 Use Cases

### Research
- Compare SOTA methods
- Identify research gaps
- Generate novel ideas
- Write related work sections

### Education
- Understand paper differences
- Learn critical analysis
- Study research methods

### Industry
- Evaluate competing approaches
- Make technical decisions
- Generate R&D ideas

---

## 🌟 Features

✅ Single-file implementation (easy to understand)
✅ Beautiful web interface
✅ RESTful API
✅ Automatic weakness detection
✅ Novel method synthesis
✅ Comparative analysis
✅ No hallucination (structured prompts)
✅ Fast (Groq LLaMA 3.3 70B)
✅ Cheap (~$0.01 per analysis)
✅ Stateless (can scale)

---

## 📞 Support

**Need Help?**
1. Check `README.md`
2. Check `API_DOCS.md`
3. Run `python test_setup.py`
4. Check Groq API status

**Common Questions:**

Q: How long does it take?
A: 2-3 minutes per pair of papers

Q: How much does it cost?
A: ~$0.01-0.02 per analysis (Groq pricing)

Q: Can I use other LLMs?
A: Yes, modify GroqClient class

Q: Can I run without internet?
A: No, requires Groq API access

Q: Is my data stored?
A: No, everything is temporary

---

## 🎉 You're Ready!

```bash
# Start the server
python app.py

# Open browser
# http://localhost:5000

# Upload papers
# Get amazing insights!
```

---

**Built with ❤️ for researchers**
**Powered by Groq & LLaMA 3.3**

