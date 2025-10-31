#!/usr/bin/env python3
"""
Check the LMSConnect directory to understand its structure
"""
import os
from pathlib import Path
 
def main():
    target_path = Path(r"C:\github\LMSconnect")
    
    if not target_path.exists():
        print(f"❌ Target path does not exist: {target_path}")
        return
    
    print(f"✅ Target path exists: {target_path}")
    print(f"   Is directory: {target_path.is_dir()}")
    
    # Count files and directories
    file_count = 0
    dir_count = 0
    file_types = {}
    
    for root, dirs, files in os.walk(target_path):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', '.idea', '_normalized']]
        dir_count += len(dirs)
        file_count += len(files)
        
        # Count file types
        for file in files:
            ext = Path(file).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
    
    print(f"📊 Statistics:")
    print(f"   Total directories: {dir_count}")
    print(f"   Total files: {file_count}")
    print(f"   File types:")
    for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"     {ext or '(no extension)'}: {count}")
    
    # Show some sample files
    print(f"\n📂 Sample files:")
    count = 0
    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', '.idea', '_normalized']]
        for file in files[:5]:  # Show first 5 files
            file_path = Path(root) / file
            rel_path = file_path.relative_to(target_path)
            size_kb = file_path.stat().st_size // 1024
            print(f"   {rel_path} ({size_kb} KB)")
            count += 1
            if count >= 10:
                break
        if count >= 10:
            break
    
    if count == 0:
        print("   No files found!")

if __name__ == "__main__":
    main()
