#!/usr/bin/env python3
"""
JAI GURU DEV AI Chatbot Launcher
Detects execution method and handles appropriately
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def is_running_in_streamlit():
    """Check if this script is being run by streamlit"""
    return (
        'streamlit' in sys.modules or
        'STREAMLIT_SERVER_PORT' in os.environ or
        'streamlit' in ' '.join(sys.argv).lower() or
        any('streamlit' in arg for arg in sys.argv)
    )

def streamlit_mode():
    """Handle when script is run with 'streamlit run start_chatbot.py'"""
    import streamlit as st
    
    st.set_page_config(
        page_title="🙏 JAI GURU DEV AI - Launcher",
        page_icon="🙏",
        layout="centered"
    )
    
    st.markdown("""
    # 🙏 JAI GURU DEV AI Chatbot
    
    ## ⚠️ Incorrect Launch Method Detected
    
    You ran: `streamlit run start_chatbot.py`
    
    This causes conflicts. Please use one of these methods instead:
    
    ### ✅ Correct Launch Methods:
    
    **Option 1: Simple Launcher**
    ```bash
    python launch_simple.py
    ```
    
    **Option 2: Enhanced Launcher**  
    ```bash
    python start_chatbot.py
    ```
    
    **Option 3: Direct Method**
    ```bash
    streamlit run chatbot.py
    ```
    
    **Option 4: Windows Batch File**
    ```bash
    quick_start.bat
    ```
    
    ### 🎯 Quick Fix:
    1. Close this browser tab
    2. Press Ctrl+C in your terminal
    3. Run: `python launch_simple.py`
    
    ---
    
    **🙏 Jai Guru Dev!**
    """)
    
    return

def normal_mode():
    """Handle normal Python execution"""
    print("🙏 Starting JAI GURU DEV AI Chatbot...")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")
    
    # Kill existing processes
    print("🔄 Cleaning up any existing Streamlit processes...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/f", "/im", "streamlit.exe"], 
                         capture_output=True, check=False)
    except:
        pass
    
    time.sleep(1)
    
    # Check required files
    if not Path("chatbot.py").exists():
        print("❌ chatbot.py not found!")
        return False
        
    if not Path("config.yaml").exists():
        print("❌ config.yaml not found!")
        return False
        
    if not Path("Knowledge_Base").exists():
        print("❌ Knowledge_Base folder not found!")
        return False
    
    # Launch Streamlit
    print("\n" + "=" * 60)
    print("🚀 Launching JAI GURU DEV AI Chatbot...")
    print("🌐 Will open at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "chatbot.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--theme.primaryColor", "#FF8C00"
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 JAI GURU DEV AI Chatbot stopped.")
        print("🙏 Jai Guru Dev!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try: python launch_simple.py")
    
    return True

def main():
    """Main function - detects execution method"""
    if is_running_in_streamlit():
        streamlit_mode()
    else:
        normal_mode()

if __name__ == "__main__":
    main()
