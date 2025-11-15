# Test functions for API connections
import os
import yaml
from typing import Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_groq import ChatGroq


def test_openai_connection() -> Dict[str, Any]:
    """Test OpenAI API connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {"success": False, "error": "OPENAI_API_KEY not found in environment variables"}
        
        client = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key
        )
        
        response = client.invoke("Say 'Hello'")
        
        return {"success": True, "message": "OpenAI connection successful!", "response": response.content}
        
    except Exception as e:
        return {"success": False, "error": f"OpenAI connection failed: {str(e)}"}


def test_groq_connection() -> Dict[str, Any]:
    """Test Groq API connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return {"success": False, "error": "GROQ_API_KEY not found in environment variables"}
        
        client = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=api_key
        )
        
        response = client.invoke("Say 'Hello'")
        
        return {"success": True, "message": "Groq connection successful!", "response": response.content}
        
    except Exception as e:
        return {"success": False, "error": f"Groq connection failed: {str(e)}"}


def test_embeddings_connection(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Test embeddings connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Load config to determine embeddings provider
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        provider = config['embeddings'].get('provider', 'huggingface')
        
        if provider == 'huggingface':
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings
            
            hf_config = config['embeddings']['huggingface']
            embeddings = HuggingFaceEmbeddings(
                model_name=hf_config['model'],
                model_kwargs={'device': hf_config.get('device', 'cpu')},
                encode_kwargs={'normalize_embeddings': True}
            )
        elif provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return {"success": False, "error": "OPENAI_API_KEY not found for OpenAI embeddings"}
            
            openai_config = config['embeddings']['openai']
            embeddings = OpenAIEmbeddings(
                model=openai_config['model'],
                api_key=api_key
            )
        else:
            return {"success": False, "error": f"Unsupported embeddings provider: {provider}"}
        
        # Test embedding
        test_embedding = embeddings.embed_query("Hello world")
        
        return {"success": True, "message": f"Embeddings connection successful! (dimension: {len(test_embedding)})"}
        
    except Exception as e:
        return {"success": False, "error": f"Embeddings connection failed: {str(e)}"}
