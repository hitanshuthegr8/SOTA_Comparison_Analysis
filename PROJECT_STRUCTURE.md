# 📁 Project Structure

```
research-pipeline/
│
├── 📄 app.py                    # Main Flask application (ALL CODE IN ONE FILE)
│   ├── Data Structures
│   │   ├── ParsedPaper
│   │   ├── PaperWeaknesses
│   │   ├── WeaknessAnalysis
│   │   └── ProposedMethod
│   │
│   ├── Core Components
│   │   ├── GroqClient              # API communication
│   │   ├── PaperParser             # STEP 1: PDF → Structured JSON
│   │   ├── WeaknessExtractor       # STEP 2: Extract weaknesses
│   │   ├── WeaknessNormalizer      # STEP 3: Canonicalize weaknesses
│   │   ├── WeaknessFusion          # STEP 4: Analyze patterns
│   │   ├── MethodSynthesizer       # STEP 5: Generate new method
│   │   └── ComparativeAnalyzer     # STEP 6-7: Compare & table
│   │
│   ├── Pipeline Orchestrator
│   │   └── ResearchPipeline        # Coordinates all steps
│   │
│   └── Flask Routes
│       ├── / (GET)                 # Web interface
│       ├── /analyze (POST)         # Main analysis endpoint
│       └── /health (GET)           # Health check
│
├── 📄 requirements.txt          # Python dependencies
│   ├── Flask==3.0.0
│   ├── requests==2.31.0
│   ├── PyPDF2==3.0.1
│   ├── Werkzeug==3.0.1
│   └── python-dotenv==1.0.0
│
├── 📄 .env.example              # Environment variables template
│   └── GROQ_API_KEY=your_key_here
│
├── 📄 README.md                 # Full documentation
│
├── 📄 PROJECT_STRUCTURE.md      # This file
│
├── 📄 test_setup.py             # Setup verification script
│   ├── test_imports()
│   ├── test_api_key()
│   ├── test_groq_connection()
│   └── test_file_structure()
│
├── 📄 run.sh                    # Quick start script (Linux/Mac)
│
└── 📄 .gitignore                # Git ignore rules

```

## 🔄 Data Flow

```
Upload PDFs
    ↓
┌─────────────────────────────────────────────────────────┐
│                    ResearchPipeline                      │
│                                                          │
│  1. PaperParser                                         │
│     Input: PDF files                                     │
│     Output: ParsedPaper (title, abstract, method, etc)  │
│                                                          │
│  2. WeaknessExtractor                                   │
│     Input: ParsedPaper                                   │
│     Output: PaperWeaknesses (list of weaknesses)        │
│                                                          │
│  3. WeaknessNormalizer                                  │
│     Input: Raw weaknesses                               │
│     Output: Canonical weaknesses                        │
│                                                          │
│  4. WeaknessFusion                                      │
│     Input: Weaknesses from both papers                  │
│     Output: WeaknessAnalysis (shared, unique)           │
│                                                          │
│  5. MethodSynthesizer                                   │
│     Input: WeaknessAnalysis                             │
│     Output: ProposedMethod (name, idea, components)     │
│                                                          │
│  6. ComparativeAnalyzer                                 │
│     Input: Papers + Weaknesses + ProposedMethod         │
│     Output: Comparison table                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
    ↓
Display Results
```

## 🎯 Key Classes

### 1. **GroqClient**
- Handles all API communication
- Single method: `chat_completion(messages, temperature, max_tokens)`
- Error handling and retries

### 2. **PaperParser**
- Extracts structured sections from PDFs
- Uses LLM to identify: title, abstract, method, experiments, limitations
- Returns: `ParsedPaper` dataclass

### 3. **WeaknessExtractor**
- Section-wise analysis (method, experiments, limitations)
- Strict reviewer mode prompting
- Returns: `PaperWeaknesses` with list of issues

### 4. **WeaknessNormalizer**
- Groups similar weaknesses
- Merges duplicates
- Creates canonical research-style labels

### 5. **WeaknessFusion**
- Identifies shared weaknesses
- Separates unique weaknesses per paper
- Returns: `WeaknessAnalysis` dataclass

### 6. **MethodSynthesizer**
- Switches LLM from reviewer → author mode
- Generates novel method addressing weaknesses
- Returns: `ProposedMethod` with components

### 7. **ComparativeAnalyzer**
- Multi-aspect comparison
- Fixed schema for consistency
- Returns: Comparison table dict

### 8. **ResearchPipeline**
- Orchestrates entire workflow
- Manages data flow between components
- Single entry point: `process(pdf_a, pdf_b)`

## 🌐 API Endpoints

### `GET /`
- Serves HTML interface
- Embedded CSS and JavaScript
- File upload form
- Results display area

### `POST /analyze`
- Accepts: `multipart/form-data` with two PDF files
- Validates: File presence and API key
- Processes: Runs complete pipeline
- Returns: JSON with all results

### `GET /health`
- Health check
- Returns: Server status and API configuration

## 📊 Data Structures

### ParsedPaper
```python
{
    "paper_id": "A" | "B",
    "title": str | null,
    "abstract": str | null,
    "method": str | null,
    "experiments": str | null,
    "limitations": str | null
}
```

### PaperWeaknesses
```python
{
    "paper_id": "A" | "B",
    "weaknesses": [str, ...]
}
```

### WeaknessAnalysis
```python
{
    "shared": [str, ...],
    "paper_a_only": [str, ...],
    "paper_b_only": [str, ...]
}
```

### ProposedMethod
```python
{
    "method_name": str,
    "core_idea": str,
    "components": [str, ...],
    "addresses_weaknesses": str
}
```

### Comparison Table
```python
{
    "Task scalability": {
        "paper_a": str,
        "paper_b": str,
        "proposed": str
    },
    "Theoretical grounding": { ... },
    "Memory efficiency": { ... },
    "Generalization capability": { ... }
}
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY` - Required for API access
- `FLASK_DEBUG` - Optional, defaults to True in dev

### Model Configuration
- Model: `llama-3.3-70b-versatile`
- Temperature: 0.1-0.5 (varies by step)
- Max tokens: 800-3000 (varies by step)

## 🚀 Execution Flow

1. **User uploads** two PDFs via web interface
2. **Flask receives** POST request at `/analyze`
3. **Files saved** to temporary directory
4. **Pipeline created** with Groq API client
5. **Process runs** through all 6 steps
6. **Results returned** as JSON
7. **JavaScript renders** results in UI
8. **Temp files cleaned** up

## 💾 Storage

- **Temporary**: Uses system temp directory
- **Uploads**: Saved only during processing
- **Cleanup**: Automatic after each request
- **No persistence**: Stateless design

## 🎨 Frontend

- **Single-page app**: All HTML/CSS/JS embedded
- **No build step**: Pure vanilla JavaScript
- **Responsive**: Works on mobile and desktop
- **Real-time updates**: Loading states and progress

## 🔒 Security

- **File size limits**: 50MB max
- **File type validation**: PDF/TXT only
- **Secure filenames**: Using Werkzeug
- **Temp directory**: Isolated per request
- **No file retention**: Immediate cleanup

---

**Total Lines of Code: ~1,000 lines in single file**
**Dependencies: 5 packages**
**Complexity: Production-ready research tool**
