# 🧠 AI Research Ideation Pipeline

An automated system that analyzes SOTA (State-of-the-Art) research papers, extracts weaknesses, and synthesizes novel research methods using AI.

## 🎯 What It Does

This pipeline:
1. **Analyzes 2 SOTA papers** → Extracts structured content
2. **Identifies weaknesses** → Uses LLM as a strict reviewer
3. **Synthesizes a NEW method** → Combines strengths, addresses weaknesses
4. **Produces comparative analysis** → Shows why the new method is better

### Output

- ✅ Weaknesses of Paper A
- ✅ Weaknesses of Paper B  
- ✅ A proposed new research method
- ✅ Comparative table: Paper A vs Paper B vs Proposed Method

## 🏗️ Architecture

```
Paper A ─┐
         ├─ Parse ──→ Extract Weaknesses ─┐
Paper B ─┘                                 │
                                           ↓
                              Weakness Normalization
                                           ↓
                         Weakness Fusion & Gap Analysis
                                           ↓
                        New Method Synthesis (LLM)
                                           ↓
                       Comparative Analysis & Table
```

## 📋 Prerequisites

- Python 3.8+
- Groq API Key (free at [console.groq.com](https://console.groq.com/keys))

## 🚀 Quick Start

### 1. Clone/Download the files

```bash
# Your project structure should be:
research-pipeline/
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Groq API key
# Or export directly:
export GROQ_API_KEY='your-groq-api-key-here'
```

### 4. Run the server

```bash
python app.py
```

### 5. Open in browser

Navigate to: **http://localhost:5000**

## 📖 Usage

1. **Upload two research papers** (PDF or TXT format)
2. **Click "Analyze & Synthesize"**
3. **Wait 2-3 minutes** for the pipeline to process
4. **Review the results:**
   - Weaknesses identified in each paper
   - Shared vs unique weaknesses
   - Proposed new method with components
   - Comparative analysis table

## 🎨 Features

### ✨ Smart Analysis
- **Section-wise weakness extraction** - Analyzes method, experiments, and limitations separately
- **Weakness normalization** - Groups similar weaknesses to avoid duplicates
- **Pattern detection** - Identifies shared weaknesses across papers

### 🔬 Method Synthesis
- **Constraint-aware generation** - No new datasets or assumptions required
- **Strength combination** - Implicitly combines best aspects of both papers
- **Weakness-driven design** - Explicitly addresses identified gaps

### 📊 Comparative Analysis
- **Multi-dimensional comparison** - Task scalability, theoretical grounding, memory efficiency, generalization
- **Evidence-based** - Uses only provided weaknesses and method descriptions
- **No hallucination** - Structured prompts prevent speculation

## 🛠️ Technical Details

### Models Used
- **Groq LLaMA 3.3 70B** - Fast and capable for structured reasoning

### Pipeline Steps

1. **PDF Parsing** (GROBID-inspired)
   - Extracts: Title, Abstract, Method, Experiments, Limitations
   - Returns structured JSON

2. **Weakness Extraction** (Per section, strict reviewer mode)
   - Multiple small LLM calls
   - No speculation beyond text
   - Bullet-point format

3. **Weakness Normalization**
   - Canonicalizes similar weaknesses
   - Merges duplicates
   - Research-style labels

4. **Weakness Fusion & Gap Analysis**
   - Identifies shared weaknesses
   - Finds unique weaknesses per paper
   - Deterministic where possible

5. **Method Synthesis**
   - Switches LLM from reviewer → research author
   - Generates method name, core idea, components
   - Explains how weaknesses are addressed

6. **Comparative Analysis**
   - Compares across fixed aspects
   - Uses only provided information
   - Schema-fixed table output

### API Endpoints

- `GET /` - Web interface
- `POST /analyze` - Main analysis endpoint
- `GET /health` - Health check

## 🔒 Safety & Reliability

### Prevents Hallucination
- ✅ Structured inputs at every step
- ✅ Small, scoped prompts
- ✅ No new data allowed in synthesis
- ✅ Canonical weakness mapping
- ✅ Deterministic fusion logic

### Error Handling
- Graceful fallbacks for JSON parsing
- Timeout protection
- Input validation
- Comprehensive logging

## 📝 Example Output

```
Paper A: "Continual Learning via LoRA Adaptation"
Weaknesses:
- Short task sequence (≤5 tasks)
- No theoretical stability guarantees
- Unanalyzed memory growth

Paper B: "Subspace Regularization for CL"
Weaknesses:
- High inference overhead
- Limited to similar task domains
- Requires task boundary detection

Proposed Method: "Unified Subspace-Regularized LoRA (USR-LoRA)"
Core Idea: Combines adaptive low-rank adaptation with task-invariant 
subspace regularization, eliminating task boundaries while controlling 
memory growth through explicit budget constraints.

Components:
- Shared low-rank subspace with adaptive gating
- Task-invariant regularization constraint
- Memory-aware parameter budget
- Boundary-free continual learning
```

## 🤝 Contributing

This is a research tool. Feel free to:
- Extend the weakness taxonomy
- Add more comparison aspects
- Improve parsing accuracy
- Add support for more paper formats

## 📄 License

MIT License - Feel free to use for research and education

## 🙏 Acknowledgments

Built with:
- Groq for fast LLM inference
- Flask for the web framework
- Inspired by GROBID for paper parsing

## 📞 Support

Issues? Questions?
- Check that GROQ_API_KEY is set correctly
- Ensure papers are in PDF or TXT format
- Try with smaller papers first (< 20 pages)

---

**Happy researching! 🚀**
