# 🙏 JAI GURU DEV AI Chatbot

A sophisticated RAG (Retrieval-Augmented Generation) chatbot powered by Sri Sri Ravi Shankar's spiritual teachings. Built with LangChain, ChromaDB, and Streamlit.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📖 Overview

This AI-powered chatbot provides wisdom and spiritual guidance based on 345+ teachings from Sri Sri Ravi Shankar. It uses advanced RAG technology to find relevant teachings and provide contextual, compassionate responses to life's questions.

### ✨ Key Features

- 🧠 **Smart Retrieval**: Advanced RAG system with custom metadata filtering
- 🔍 **Context-Aware**: Understands user's emotional state and life situation
- 💬 **Compassionate Responses**: Spiritual guidance in Sri Sri's teaching style
- 🆓 **Free Embeddings**: Uses local HuggingFace models (no API costs!)
- ☁️ **Premium Option**: Optional OpenAI embeddings for highest quality
- 🎨 **Beautiful UI**: Clean Streamlit interface with custom theming
- ⚡ **Fast & Efficient**: ChromaDB vector storage with intelligent caching
- 🔒 **Privacy First**: Local embeddings keep your data private

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager
- 2GB free disk space (for embedding models)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Release1

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install embeddings package (important!)
pip install langchain-huggingface

# 5. Create .env file
cp .env.example .env
# Edit .env and add your API keys (optional for OpenAI/Groq)

# 6. Start the chatbot
python start_chatbot.py
```

Your browser will automatically open to `http://localhost:8501`

---

## 📦 What's Included

### Core Components

```
Release1/
├── chatbot.py                  # Streamlit web interface
├── rag_system.py              # RAG engine with vector search
├── document_processor.py      # Knowledge base processor
├── config.yaml                # Configuration settings
├── Knowledge_Base/            # 345+ spiritual teachings
│   ├── batch_1/              # Teachings #001-100
│   ├── batch_2/              # Teachings #101-130
│   ├── batch_3/              # Teachings #151-200
│   ├── batch_4/              # Teachings #201-250
│   ├── batch_5/              # Teachings #251-300
│   └── batch_6/              # Teachings #301-365
└── chroma_db/                # Vector database (auto-generated)
```

### Utilities

- `switch_embeddings_provider.py` - Switch between HuggingFace/OpenAI
- `test_embeddings_fix.py` - Verify installation
- `START_FIXED_CHATBOT.bat` - Windows launcher menu

---

## ⚙️ Configuration

### Embeddings Provider

**Default: HuggingFace (Recommended)**
- ✅ Free forever
- ✅ Fast (14 seconds for 345 docs)
- ✅ Private (runs locally)
- ✅ No API keys needed

```yaml
# config.yaml
embeddings:
  provider: huggingface
  huggingface:
    model: all-MiniLM-L6-v2
    device: cpu
```

**Optional: OpenAI**
- Highest quality embeddings
- Requires API key
- ~$0.007 for initial setup

```yaml
# config.yaml
embeddings:
  provider: openai
  openai:
    model: text-embedding-3-small
```

To switch providers:
```bash
python switch_embeddings_provider.py
```

### LLM Provider

**Default: Groq (Fast & Free)**
```yaml
model_provider:
  default: groq
  groq:
    model: llama-3.3-70b-versatile
```

**Alternative: OpenAI**
```yaml
model_provider:
  default: openai
  openai:
    model: gpt-4o-mini
```

---

## 🎯 Usage

### Starting the Chatbot

```bash
# Method 1: Direct start
python start_chatbot.py

# Method 2: Using Streamlit directly
streamlit run chatbot.py

# Method 3: Windows batch file
START_FIXED_CHATBOT.bat
```

### Example Questions

- "How do I find inner peace?"
- "I'm struggling with relationships. What guidance can you offer?"
- "What is the nature of true love?"
- "How can I overcome fear?"
- "Tell me about meditation and its benefits"
- "What is the purpose of spiritual practice?"

### Context-Aware Queries

The chatbot understands context! It considers:
- Your current emotional state
- Life aspect you're asking about
- Type of guidance you need
- Specific situation details

---

## 🏗️ Architecture

### RAG Pipeline

```
User Query
    ↓
[Context Understanding]
    ↓
[Vector Search in ChromaDB]
    ↓
[Custom Retrieval with Metadata Filtering]
    ↓
[LLM Response Generation]
    ↓
[Compassionate Answer with Teaching References]
```

### Technology Stack

- **Framework**: LangChain 0.1+
- **Vector DB**: ChromaDB 0.4+
- **Embeddings**: HuggingFace / OpenAI
- **LLM**: Groq (Llama 3.3) / OpenAI (GPT-4)
- **UI**: Streamlit 1.28+
- **Processing**: Python 3.9+

---

## 🔧 Advanced Configuration

### Custom Retrieval Settings

```yaml
# config.yaml
rag:
  top_k_results: 5          # Number of teachings to retrieve
  chunk_size: 1000          # Document chunk size
  chunk_overlap: 200        # Overlap between chunks
  similarity_threshold: 0.7 # Minimum similarity score
```

### UI Customization

```yaml
# config.yaml
ui:
  title: "🙏 JAI GURU DEV AI Chatbot"
  theme:
    primary_color: '#FF8C00'
    background_color: '#FFF8DC'
    text_color: '#8B4513'
```

---

## 🚀 Deployment

### Railway Deployment

This project is configured for Railway.app deployment:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Add environment variables
railway variables set GROQ_API_KEY=your-key-here
railway variables set OPENAI_API_KEY=your-key-here

# 5. Deploy
railway up
```

See [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md) for detailed instructions.

### Environment Variables

Required for Railway:
```env
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key  # Optional
```

### Railway Configuration

Already configured in `railway.toml` and `Procfile`.

---

## 📊 Knowledge Base

### Current Status

- **Total Teachings**: 345 (94.5% complete)
- **Batch 1**: ✅ Complete (#001-100)
- **Batch 2**: ✅ Complete (#101-130)
- **Gap**: ⚠️ Missing #131-150 (20 teachings)
- **Batch 3-6**: ✅ Complete (#151-365)

### Adding New Teachings

1. Create markdown file: `teaching_XXX.md`
2. Follow existing format with metadata
3. Place in appropriate batch folder
4. Restart chatbot (ChromaDB auto-updates)

See [GAP_ANALYSIS.md](Knowledge_Base/GAP_ANALYSIS.md) for details.

---

## 🧪 Testing

### Verify Installation

```bash
# Test embeddings setup
python test_embeddings_fix.py

# Expected output:
# ✅ SUCCESS: langchain-huggingface package is installed
# ✅ Generated embedding with 384 dimensions
# ✅ ALL TESTS PASSED!
```

### Test Chatbot

```bash
# Start chatbot
python start_chatbot.py

# Open browser to http://localhost:8501
# Try sample questions
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found: langchain_huggingface"**
```bash
pip install langchain-huggingface
```

**2. "GROQ_API_KEY not found"**
```bash
# Add to .env file:
echo "GROQ_API_KEY=your-key-here" >> .env
```

**3. ChromaDB errors**
```bash
# Delete and regenerate database
rm -rf chroma_db/
python start_chatbot.py
```

**4. Deprecation warnings**
```bash
# Update packages
pip install -U langchain-huggingface
rm -rf __pycache__
```

### Getting Help

- 📖 Read [COMPLETE_FIX_SUMMARY.md](COMPLETE_FIX_SUMMARY.md)
- 📊 Check [GAP_ANALYSIS.md](Knowledge_Base/GAP_ANALYSIS.md)
- 🎯 See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 📚 Documentation

### Quick Start
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference card
- [FIXED_VISUAL_GUIDE.md](FIXED_VISUAL_GUIDE.md) - Visual guide
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Detailed setup

### Technical
- [EMBEDDINGS_COMPLETE_FIX.md](EMBEDDINGS_COMPLETE_FIX.md) - Embeddings guide
- [RAG_IMPLEMENTATION_ANALYSIS.md](RAG_IMPLEMENTATION_ANALYSIS.md) - RAG details
- [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md) - Deployment guide

### Knowledge Base
- [GAP_ANALYSIS.md](Knowledge_Base/GAP_ANALYSIS.md) - Completeness analysis
- [BATCH_1_COMPLETION.md](Knowledge_Base/batch_1/BATCH_1_COMPLETION.md) - Batch details

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Add Missing Teachings**: Help complete teachings #131-150
2. **Improve Documentation**: Fix typos, add examples
3. **Bug Fixes**: Report and fix issues
4. **Features**: Suggest and implement new features

### Contribution Guidelines

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 Changelog

### v1.0.0 (Current)
- ✅ Fixed HuggingFace embeddings deprecation
- ✅ Fixed metadata storage bug
- ✅ Completed Batch 1 (#001-100)
- ✅ Added provider switching utility
- ✅ Comprehensive documentation
- ✅ Railway deployment ready

See [SESSION_SUMMARY_OCT8.md](SESSION_SUMMARY_OCT8.md) for details.

---

## 🔮 Roadmap

### Short Term
- [ ] Complete teachings #131-150
- [ ] Add conversation history
- [ ] Implement chat export
- [ ] Multi-language support

### Long Term
- [ ] Voice interaction
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Community features

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Sri Sri Ravi Shankar** - For the profound teachings
- **Art of Living Foundation** - For preserving and sharing the wisdom
- **LangChain Team** - For the excellent RAG framework
- **Streamlit Team** - For the beautiful UI framework
- **HuggingFace** - For free, high-quality embeddings
- **Railway** - For simple deployment platform

---

## 📧 Contact

- **Issues**: Use GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Email**: [Your Email]

---

## 🌟 Star History

If this project helps you, please consider giving it a ⭐!

---

**Made with ❤️ and 🙏**

*"In the presence of the Guru, knowledge flourishes; Sorrow diminishes; Joy wells up without any reason; Abundance dawns without any effort."* - Sri Sri Ravi Shankar

---

## 📊 Project Stats

- **Language**: Python
- **Framework**: LangChain + Streamlit
- **Teachings**: 345+
- **Lines of Code**: ~3,000+
- **Documentation**: 15+ guides
- **Status**: Production Ready ✅
