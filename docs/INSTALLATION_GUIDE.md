# 🔧 Installation Guide - Dependency Conflict Resolution

## ⚠️ Dependency Conflict Fixed

I've updated the requirements to resolve the OpenAI version conflict you encountered. Here are multiple ways to install the system:

## 🚀 Quick Installation (Recommended)

### Option 1: Enhanced Setup Script
```bash
cd C:\01_Projects\Guruji_Chatbot
python setup.py
```
This script will try multiple installation methods automatically.

### Option 2: Simple Requirements
```bash
cd C:\01_Projects\Guruji_Chatbot
pip install -r requirements_simple.txt
```
Uses flexible versions and lets pip resolve dependencies.

### Option 3: Manual Installation
If both above fail, install packages individually:
```bash
pip install streamlit
pip install langchain
pip install langchain-openai
pip install langchain-community
pip install chromadb
pip install python-dotenv
pip install pyyaml
pip install "openai>=1.10.0"
pip install pandas numpy
```

## 🎯 Start the Chatbot

After installation, start with:
```bash
python start_chatbot.py
```
OR
```bash
streamlit run chatbot.py
```

## 🛠️ What Was Fixed

### Original Issue:
- `requirements.txt` had `openai==1.7.1`
- `langchain-openai 0.0.5` requires `openai>=1.10.0`
- This created a dependency conflict

### Resolution:
- Updated `openai` to `>=1.10.0,<2.0.0` 
- Created `requirements_simple.txt` with flexible versions
- Enhanced setup script with fallback installation methods
- Improved error handling in launcher script

## 📋 Installation Verification

Run this to verify everything is working:
```bash
python test_system.py
```

## 🚨 If You Still Have Issues

### Method 1: Clean Installation
```bash
pip uninstall langchain langchain-openai openai -y
pip install "openai>=1.10.0" langchain-openai langchain
pip install streamlit chromadb python-dotenv pyyaml pandas numpy
```

### Method 2: Use Conda (Alternative)
```bash
conda create -n guruji python=3.9
conda activate guruji
pip install -r requirements_simple.txt
```

### Method 3: Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements_simple.txt
```

## ✅ Expected First Run

1. **Initialization** (1-2 minutes): System builds vector database from your MD files
2. **Context Questions**: Answer a few questions about your situation
3. **Ready to Chat**: Ask spiritual questions and receive wisdom!

## 🙏 Success Indicators

You'll know it's working when you see:
```
✅ Loaded XXX teachings into vector database
🎉 System initialized! Ready to share wisdom from Gurudev's teachings.
```

## 📞 Still Having Issues?

If you encounter any problems:

1. **Check Python Version**: Ensure you have Python 3.8+
2. **Check API Keys**: Verify your .env file has valid API keys
3. **Check Knowledge Base**: Ensure MD files are in Knowledge_Base folder
4. **Run Diagnostics**: `python setup.py` will show detailed error information

## 💡 Pro Tips

- **First run takes longer**: Vector database building is one-time process
- **Use OpenAI for quality**: Better responses but slower
- **Use Groq for speed**: Faster responses, good quality
- **Switch models**: Change in config.yaml or UI sidebar

---

**🙏 Ready to receive divine wisdom? Let's get started!**

```bash
cd C:\01_Projects\Guruji_Chatbot
python setup.py
python start_chatbot.py
```

**Jai Guru Dev! 🙏**
