"""
Test script to verify HuggingFace Embeddings fix
"""

import sys

def test_new_import():
    """Test if new langchain-huggingface package is available"""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✅ SUCCESS: langchain-huggingface package is installed")
        print("   You can now use HuggingFaceEmbeddings without deprecation warnings")
        return True
    except ImportError as e:
        print("❌ FAILED: langchain-huggingface package not found")
        print(f"   Error: {e}")
        print("\n   Fix: Run 'pip install langchain-huggingface'")
        return False

def test_old_import():
    """Test if old import still works (with warning)"""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("\n⚠️  WARNING: Using deprecated import from langchain_community")
        print("   This will stop working in LangChain 1.0")
        return True
    except ImportError as e:
        print(f"\n❌ Old import also failed: {e}")
        return False

def test_embeddings_functionality():
    """Test if embeddings actually work"""
    try:
        # Try new import first
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            print("\n✅ Testing with NEW package (langchain-huggingface)...")
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            print("\n⚠️  Testing with OLD package (langchain-community)...")
        
        print("   Creating embeddings model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print("   Testing embedding generation...")
        test_text = "Hello, this is a test."
        embedding = embeddings.embed_query(test_text)
        
        print(f"   ✅ Generated embedding with {len(embedding)} dimensions")
        print(f"   ✅ Embeddings are working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Embeddings test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("HuggingFace Embeddings Fix Verification")
    print("=" * 60)
    
    # Test 1: Check new import
    new_import_ok = test_new_import()
    
    # Test 2: Check old import (for fallback)
    old_import_ok = test_old_import()
    
    # Test 3: Test functionality
    print("\n" + "=" * 60)
    print("Testing Embeddings Functionality")
    print("=" * 60)
    functionality_ok = test_embeddings_functionality()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if new_import_ok and functionality_ok:
        print("✅ ALL TESTS PASSED!")
        print("   Your system is using the latest langchain-huggingface package")
        print("   No deprecation warnings will appear")
        print("\n   You're ready to run your chatbot! 🚀")
        return 0
    elif old_import_ok and functionality_ok:
        print("⚠️  PARTIAL SUCCESS")
        print("   Embeddings work but using deprecated package")
        print("   You'll see deprecation warnings")
        print("\n   Recommendation: Run 'pip install langchain-huggingface'")
        return 1
    else:
        print("❌ TESTS FAILED")
        print("   Something is wrong with your installation")
        print("\n   Fix:")
        print("   1. Run: pip install -U langchain-community langchain-huggingface")
        print("   2. Restart Python")
        print("   3. Run this test again")
        return 2

if __name__ == "__main__":
    sys.exit(main())
