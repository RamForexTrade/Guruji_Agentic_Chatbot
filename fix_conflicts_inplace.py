"""
Step 1: Fix all conflicts IN PLACE in the current directory
Step 2: Then you can copy or push to Git
"""

import os
import re
from pathlib import Path

def fix_file_conflicts(filepath):
    """Fix Git conflict markers in a file"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if has conflicts
        if '<<<<<<< HEAD' not in content:
            return False, "No conflicts"
        
        original_content = content
        
        # Remove conflict markers - keep HEAD version
        # Pattern: <<<<<<< HEAD\n<keep this>\n=======\n<remove this>\n>>>>>>> hash
        
        lines = content.split('\n')
        cleaned_lines = []
        in_conflict = False
        in_head_section = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('<<<<<<< HEAD'):
                in_conflict = True
                in_head_section = True
                i += 1
                continue
            
            elif line.startswith('=======') and in_conflict:
                in_head_section = False
                i += 1
                continue
            
            elif line.startswith('>>>>>>>') and in_conflict:
                in_conflict = False
                in_head_section = False
                i += 1
                continue
            
            # Keep lines that are:
            # - Not in conflict, OR
            # - In HEAD section of conflict
            if not in_conflict or in_head_section:
                cleaned_lines.append(line)
            
            i += 1
        
        # Join back
        fixed_content = '\n'.join(cleaned_lines)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return True, f"Fixed ({len(content)} -> {len(fixed_content)} bytes)"
        
    except Exception as e:
        return False, f"Error: {e}"

def fix_all_in_current_dir():
    """Fix all conflict markers in current directory"""
    
    print("="*70)
    print("FIXING ALL GIT CONFLICTS IN CURRENT DIRECTORY")
    print("="*70)
    print()
    print("This will modify files IN PLACE by keeping HEAD version")
    print()
    
    # File extensions to fix
    extensions = ['.py', '.yaml', '.yml', '.toml', '.md', '.txt', '.json', '.bat']
    
    current_dir = Path('.')
    fixed_files = []
    failed_files = []
    
    print("Scanning and fixing files...")
    print()
    
    # Walk through directory
    for root, dirs, files in os.walk(current_dir):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', 'venv', 'env', 'chroma_db', 'node_modules', 
                     '.streamlit', 'archive_old_files', 'cleanup'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = Path(root) / file
                rel_path = filepath.relative_to(current_dir)
                
                success, message = fix_file_conflicts(filepath)
                
                if success:
                    fixed_files.append(str(rel_path))
                    print(f"✅ Fixed: {rel_path}")
                elif "Error" in message:
                    failed_files.append((str(rel_path), message))
                    print(f"❌ Failed: {rel_path} - {message}")
    
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()
    print(f"✅ Fixed {len(fixed_files)} files")
    
    if failed_files:
        print(f"❌ Failed {len(failed_files)} files")
    
    print()
    
    if fixed_files:
        print("Fixed files:")
        for f in fixed_files:
            print(f"   ✅ {f}")
    
    if failed_files:
        print()
        print("Failed files:")
        for f, err in failed_files:
            print(f"   ❌ {f}: {err}")
    
    print()
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("1. Test the chatbot:")
    print("   python start_chatbot.py")
    print()
    print("2. If it works, initialize Git:")
    print("   git init")
    print("   git remote add origin https://github.com/RamForexTrade/guruji-ai-chatbot-v2.git")
    print("   git add .")
    print('   git commit -m "Initial commit: v1.0.0"')
    print("   git push -u origin main")
    print()

if __name__ == "__main__":
    import sys
    
    print()
    confirm = input("This will modify files in the current directory. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print()
    
    try:
        fix_all_in_current_dir()
        print("="*70)
        print("✅ DONE! All conflicts fixed.")
        print("="*70)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
