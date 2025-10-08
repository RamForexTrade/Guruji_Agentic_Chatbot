"""
Switch Embeddings Provider
Utility to switch between HuggingFace (free, local) and OpenAI (paid, cloud) embeddings
"""

import yaml
import os
from pathlib import Path

CONFIG_FILE = "config.yaml"

def load_config():
    """Load current config"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found: {CONFIG_FILE}")
        return None
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config):
    """Save updated config"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def get_current_provider(config):
    """Get current embeddings provider"""
    return config['embeddings'].get('provider', 'huggingface')

def show_provider_info():
    """Display information about both providers"""
    print("\n" + "="*70)
    print("📊 EMBEDDINGS PROVIDER COMPARISON")
    print("="*70)
    
    print("\n🏠 HuggingFace (Local)")
    print("   ✅ Pros:")
    print("      • FREE - No API costs")
    print("      • FAST - Runs locally on your machine")
    print("      • PRIVATE - Data never leaves your computer")
    print("      • OFFLINE - Works without internet")
    print("   ⚠️  Cons:")
    print("      • Slightly lower quality than OpenAI")
    print("      • Uses ~500MB disk space (model download)")
    print("      • First run downloads model (1-2 minutes)")
    print("   📦 Model: all-MiniLM-L6-v2 (384 dimensions)")
    
    print("\n☁️  OpenAI (Cloud)")
    print("   ✅ Pros:")
    print("      • Highest quality embeddings")
    print("      • No local storage needed")
    print("      • Always up-to-date")
    print("   ⚠️  Cons:")
    print("      • PAID - Costs $0.00002 per 1K tokens (~$0.007 for 340 docs)")
    print("      • SLOWER - API calls take time")
    print("      • Requires internet connection")
    print("      • Data sent to OpenAI servers")
    print("      • Requires OPENAI_API_KEY in .env file")
    print("   📦 Model: text-embedding-3-small (1536 dimensions)")
    
    print("\n💡 Recommendation:")
    print("   → Use HuggingFace for development and personal use")
    print("   → Use OpenAI only if you need highest quality or have API credits")
    print("="*70 + "\n")

def switch_provider(config, new_provider):
    """Switch to a different provider"""
    if new_provider not in ['huggingface', 'openai']:
        print(f"❌ Invalid provider: {new_provider}")
        print("   Valid options: 'huggingface' or 'openai'")
        return False
    
    current_provider = get_current_provider(config)
    
    if current_provider == new_provider:
        print(f"ℹ️  Already using {new_provider} embeddings")
        return False
    
    # Update config
    config['embeddings']['provider'] = new_provider
    save_config(config)
    
    print(f"\n✅ Switched embeddings provider: {current_provider} → {new_provider}")
    
    # Show next steps
    if new_provider == 'openai':
        print("\n⚠️  IMPORTANT NEXT STEPS:")
        print("   1. Ensure OPENAI_API_KEY is set in your .env file")
        print("   2. ChromaDB will be recreated on next run (costs ~$0.007)")
        print("   3. Old HuggingFace database will be replaced")
    else:
        print("\n📝 NEXT STEPS:")
        print("   1. First run will download HuggingFace model (~500MB, one-time)")
        print("   2. ChromaDB will be recreated on next run (free)")
        print("   3. Old OpenAI database will be replaced")
    
    print("\n▶️  Run your chatbot to apply changes:")
    print("   python start_chatbot.py")
    
    return True

def interactive_mode():
    """Interactive provider selection"""
    config = load_config()
    if not config:
        return
    
    current_provider = get_current_provider(config)
    
    print("\n" + "="*70)
    print("🔄 SWITCH EMBEDDINGS PROVIDER")
    print("="*70)
    print(f"\n📍 Current provider: {current_provider.upper()}")
    
    show_provider_info()
    
    print("Select embeddings provider:")
    print("  1. HuggingFace (Free, Local, Fast)")
    print("  2. OpenAI (Paid, Cloud, Highest Quality)")
    print("  3. Show info again")
    print("  4. Exit")
    
    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            if switch_provider(config, 'huggingface'):
                break
            else:
                print("\n▶️  Already using HuggingFace. Starting chatbot...")
                print("   Run: python start_chatbot.py")
                break
        elif choice == '2':
            # Check for OpenAI API key
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                print("\n❌ ERROR: OPENAI_API_KEY not found in .env file")
                print("\n📝 To use OpenAI embeddings:")
                print("   1. Open .env file")
                print("   2. Add: OPENAI_API_KEY=your-key-here")
                print("   3. Run this script again")
                continue
            
            if switch_provider(config, 'openai'):
                break
            else:
                print("\n▶️  Already using OpenAI. Starting chatbot...")
                print("   Run: python start_chatbot.py")
                break
        elif choice == '3':
            show_provider_info()
        elif choice == '4':
            print("\n👋 Exiting without changes")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        provider = sys.argv[1].lower()
        config = load_config()
        if config:
            switch_provider(config, provider)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
