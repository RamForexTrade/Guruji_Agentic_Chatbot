"""
Test Script for RAG Retrieval Diagnosis
========================================
This script tests the RAG system to identify retrieval issues
"""

import os
from dotenv import load_dotenv
from rag_system import RAGSystem, UserContext

# Load environment variables
load_dotenv()

print("=" * 80)
print("RAG RETRIEVAL DIAGNOSTIC TEST")
print("=" * 80)

try:
    # Initialize RAG System
    print("\n1️⃣ Initializing RAG System...")
    rag = RAGSystem(
        config_path="config.yaml",
        knowledge_base_path="Knowledge_Base"
    )
    print("✅ RAG System initialized")
    
    # Check if vectorstore exists
    print("\n2️⃣ Checking Vector Store...")
    if rag.vectorstore is None:
        print("❌ ERROR: Vector store is None!")
    else:
        print("✅ Vector store exists")
        
        # Check collection count
        try:
            collection = rag.vectorstore._collection
            count = collection.count()
            print(f"✅ Vector store contains {count} documents")
        except Exception as e:
            print(f"⚠️ Could not get collection count: {e}")
    
    # Check if teachings were loaded
    print("\n3️⃣ Checking Loaded Teachings...")
    print(f"✅ Loaded {len(rag.teachings)} teachings from Knowledge Base")
    
    if len(rag.teachings) > 0:
        sample = rag.teachings[0]
        print(f"   Sample Teaching: #{sample.number} - {sample.title[:50]}...")
    
    # Test retrieval with a simple query
    print("\n4️⃣ Testing Simple Retrieval...")
    test_query = "meditation"
    
    if rag.vectorstore:
        try:
            results = rag.vectorstore.similarity_search(test_query, k=3)
            print(f"✅ Retrieved {len(results)} documents for query: '{test_query}'")
            
            if len(results) > 0:
                print("\n   📄 First Result:")
                print(f"   Teaching #{results[0].metadata.get('number', 'Unknown')}")
                print(f"   Title: {results[0].metadata.get('title', 'Unknown')}")
                print(f"   Content preview: {results[0].page_content[:200]}...")
            else:
                print("⚠️ No results returned!")
        except Exception as e:
            print(f"❌ Retrieval failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Test with RAG get_response method
    print("\n5️⃣ Testing RAG get_response Method...")
    user_context = UserContext(
        life_aspect="peace",
        emotional_state="anxious",
        guidance_type="wisdom"
    )
    
    try:
        response = rag.get_response(
            "How can I find inner peace?",
            user_context
        )
        
        if response['success']:
            print("✅ RAG response generated successfully")
            print(f"\n   📝 Response preview:")
            print(f"   {response['answer'][:300]}...")
            print(f"\n   📚 Number of sources: {len(response['sources'])}")
            
            if response['sources']:
                print("\n   Sources:")
                for src in response['sources']:
                    print(f"   - Teaching #{src['teaching_number']}: {src['title']}")
        else:
            print(f"❌ RAG response failed: {response.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ get_response failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test custom retriever
    print("\n6️⃣ Testing Custom Retriever...")
    if rag.retriever:
        try:
            docs = rag.retriever.get_relevant_documents("stress and anxiety")
            print(f"✅ Custom retriever returned {len(docs)} documents")
            
            if docs:
                print("\n   📄 Sample Retrieved Document:")
                doc = docs[0]
                print(f"   Teaching #{doc.metadata.get('number', 'Unknown')}")
                print(f"   Title: {doc.metadata.get('title', 'Unknown')}")
                print(f"   Topics: {doc.metadata.get('topics', 'None')}")
        except Exception as e:
            print(f"❌ Custom retriever failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Custom retriever not initialized!")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   • RAG System: {'✅ OK' if rag else '❌ FAILED'}")
    print(f"   • Vector Store: {'✅ OK' if rag.vectorstore else '❌ FAILED'}")
    print(f"   • Teachings Loaded: {len(rag.teachings)}")
    print(f"   • Custom Retriever: {'✅ OK' if rag.retriever else '❌ FAILED'}")
    
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    
print("\n")
