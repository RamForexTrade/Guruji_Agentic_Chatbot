# Contributing to JAI GURU DEV AI Chatbot

First off, thank you for considering contributing to this spiritual AI project! 🙏

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Submitting Changes](#submitting-changes)

---

## Code of Conduct

This project is built with love and spiritual intention. We expect all contributors to:

- Be respectful and compassionate
- Maintain the spiritual integrity of the teachings
- Focus on making wisdom more accessible
- Help create a welcoming community
- Respect the source material (Sri Sri Ravi Shankar's teachings)

---

## How Can I Contribute?

### 1. 📝 Complete Missing Teachings

**High Priority**: We're missing teachings #131-150

**How to help:**
1. Check if you have access to these teachings
2. Format them as markdown files
3. Follow the existing template
4. Submit a pull request

See [GAP_ANALYSIS.md](Knowledge_Base/GAP_ANALYSIS.md) for details.

### 2. 🐛 Report Bugs

**Before submitting:**
- Check existing issues
- Verify it's reproducible
- Include error messages
- Describe expected vs actual behavior

**Create issue with:**
- Clear title
- Steps to reproduce
- Environment details (OS, Python version)
- Screenshots if applicable

### 3. 💡 Suggest Features

**Good feature requests include:**
- Clear use case
- How it helps users
- Implementation ideas (optional)
- Mockups or examples (optional)

### 4. 📖 Improve Documentation

- Fix typos and grammar
- Add examples
- Clarify confusing sections
- Translate to other languages
- Add FAQs

### 5. 🧪 Add Tests

- Unit tests for core functions
- Integration tests for RAG system
- UI tests for Streamlit interface
- Performance benchmarks

### 6. 🎨 Enhance UI/UX

- Improve Streamlit interface
- Add visualizations
- Better mobile responsiveness
- Accessibility improvements

---

## Development Setup

### Prerequisites

```bash
- Python 3.9+
- Git
- pip
- Virtual environment (recommended)
```

### Initial Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/guruji-chatbot.git
cd guruji-chatbot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install langchain-huggingface

# 4. Create .env file
cp .env.example .env
# Add your API keys

# 5. Test installation
python test_embeddings_fix.py

# 6. Start chatbot
python start_chatbot.py
```

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# ... edit files ...

# 3. Test changes
python start_chatbot.py
# Verify everything works

# 4. Commit with clear message
git add .
git commit -m "Add: Brief description of changes"

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Create Pull Request
# Go to GitHub and create PR
```

---

## Contribution Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

**Example:**
```python
def process_teaching(teaching: Teaching) -> Document:
    """
    Convert a Teaching object to a LangChain Document.
    
    Args:
        teaching: Teaching object with content and metadata
        
    Returns:
        Document object ready for embedding
    """
    # Implementation here
    pass
```

### Commit Messages

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat: Add conversation history feature

Implements conversation history with session storage.
Users can now see previous questions and answers.

Closes #123

fix: Resolve ChromaDB initialization error

Fixed metadata storage to handle provider-specific config.
Now correctly reads from nested config structure.

Fixes #45
```

### Teaching Files

**Format for new teachings:**

```markdown
# Sri Sri Ravishankar Teaching #XXX

## Teaching #XXX: [Title]
**Date:** [Date]
**Location:** [Location]
**Topics:** [topic1, topic2, ...]
**Keywords:** [keyword1, keyword2, ...]
**Problem Categories:** [category1, category2, ...]
**Emotional States:** [state1, state2, ...]
**Life Situations:** [situation1, situation2, ...]

### Content:
[Teaching content here]
```

**Guidelines:**
- Maintain exact wording from source
- Include all metadata
- Use consistent formatting
- Add appropriate topics/keywords
- Place in correct batch folder

### Testing Requirements

**Before submitting PR:**

```bash
# 1. Test embeddings
python test_embeddings_fix.py

# 2. Start chatbot
python start_chatbot.py

# 3. Test queries
# - Try sample questions
# - Verify responses
# - Check teaching references

# 4. Check for errors
# - No warnings in console
# - ChromaDB loads properly
# - UI renders correctly
```

### Documentation Requirements

**For new features:**
- Update README.md
- Add to relevant .md files
- Include examples
- Update configuration docs

**For bug fixes:**
- Describe the issue
- Explain the fix
- Add to CHANGELOG.md

---

## Submitting Changes

### Pull Request Process

1. **Before Creating PR:**
   - [ ] Code tested locally
   - [ ] No console errors
   - [ ] Documentation updated
   - [ ] Commits are clean

2. **PR Description Should Include:**
   - What changed
   - Why it changed
   - How to test it
   - Screenshots (if UI change)
   - Related issues

3. **PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing Done
- [ ] Local testing passed
- [ ] No errors in console
- [ ] UI renders correctly

## Screenshots (if applicable)
[Add screenshots]

## Related Issues
Closes #123
```

4. **Review Process:**
   - Maintainer will review
   - May request changes
   - Once approved, will be merged
   - Changes deployed to production

---

## Areas Needing Help

### High Priority

1. **Missing Teachings** (#131-150)
   - Need source material
   - Need markdown conversion
   - 20 teachings to add

2. **Testing**
   - Unit tests for core functions
   - Integration tests
   - Performance benchmarks

3. **Documentation**
   - Beginner guides
   - Video tutorials
   - FAQ expansion

### Medium Priority

1. **Features**
   - Conversation history
   - Chat export
   - User preferences
   - Multi-language support

2. **UI/UX**
   - Mobile optimization
   - Dark mode
   - Accessibility
   - Better error messages

3. **Performance**
   - Query optimization
   - Caching improvements
   - Load time reduction

### Low Priority

1. **Integrations**
   - WhatsApp bot
   - Telegram bot
   - Discord bot

2. **Analytics**
   - Usage statistics
   - Popular queries
   - Teaching frequency

---

## Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Given credit in documentation
- Part of our grateful community 🙏

---

## Questions?

- **Issues**: Use GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Email**: [Project Email]

---

## Thank You! 🙏

Your contributions help make spiritual wisdom more accessible to everyone.

*"Service is the expression of love."* - Sri Sri Ravi Shankar
