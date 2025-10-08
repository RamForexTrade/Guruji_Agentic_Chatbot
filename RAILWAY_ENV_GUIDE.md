# Environment Variables - Local vs Railway Deployment

## ✅ FIXES APPLIED

### 1. Fixed Import Errors
- Created `test_functions.py` with all API test functions
- Updated `chatbot.py` to import test functions from the correct module
- Fixed indentation error in `document_processor.py`
- Completed incomplete `_save_db_metadata()` method in `rag_system.py`

### 2. Environment Variable Handling

Your code properly handles environment variables for BOTH local and Railway deployment:

#### **Current Implementation** ✅
```python
from dotenv import load_dotenv
load_dotenv()  # This loads from .env file if it exists

api_key = os.getenv('GROQ_API_KEY')  # This reads from environment variables
```

#### **Why This Works for Both:**

**LOCAL DEVELOPMENT:**
- `load_dotenv()` reads from `.env` file
- Environment variables are loaded into `os.environ`
- `os.getenv()` retrieves them

**RAILWAY DEPLOYMENT:**
- Railway sets environment variables directly in the container
- `load_dotenv()` does nothing (no `.env` file) but doesn't fail
- `os.getenv()` still works because it reads from system environment variables
- Railway's "Service Variables" are accessible via `os.getenv()`

### 3. Railway Setup Instructions

#### **Step 1: Set Environment Variables in Railway**
Go to your Railway project → Service → Variables tab and add:
```
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional, if using OpenAI
```

#### **Step 2: No .env file needed**
- Railway ignores `.env` files (they're in `.gitignore`)
- All variables come from Railway dashboard

#### **Step 3: Config Files**
Make sure `config.yaml` is in your repository and committed:
```yaml
model_provider:
  default: "groq"  # or "openai"
  
embeddings:
  provider: "huggingface"  # Free local embeddings
```

### 4. Code is Already Railway-Ready! ✅

Your current implementation:
```python
from dotenv import load_dotenv
load_dotenv()  # Safe to call - does nothing on Railway

# Works in both local and Railway
api_key = os.getenv('GROQ_API_KEY')
```

**Why it's perfect:**
- `load_dotenv()` is idempotent - safe to call even when `.env` doesn't exist
- `os.getenv()` reads from system environment (works everywhere)
- No code changes needed between local and Railway

### 5. Best Practices ✅ (Already Implemented)

Your code already follows best practices:

1. **Environment variables for secrets** ✅
   - API keys are in environment variables, not hardcoded
   
2. **dotenv for local development** ✅
   - `.env` file for local testing
   - `.env` in `.gitignore` (never committed)

3. **Graceful fallback** ✅
   - Code checks if API key exists before using it
   - Clear error messages if missing

### 6. Testing Locally vs Railway

**LOCAL:**
```bash
# Create .env file
GROQ_API_KEY=your_key_here

# Run
streamlit run chatbot.py
```

**RAILWAY:**
```
1. Set variables in Railway dashboard
2. Push code to GitHub
3. Railway auto-deploys
4. Variables are automatically available
```

### 7. Common Pitfalls (Avoided in Your Code) ✅

❌ **Bad:**
```python
api_key = "hardcoded_key"  # Never do this!
```

✅ **Good (Your current code):**
```python
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY not found")
```

## Summary

**Your environment variable handling is already perfect for Railway deployment!** 

- ✅ Works locally with `.env` file
- ✅ Works on Railway with Service Variables  
- ✅ No code changes needed
- ✅ Proper error handling
- ✅ Secure (no hardcoded secrets)

Just set your environment variables in the Railway dashboard and deploy!
