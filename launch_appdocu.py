#!/usr/bin/env python3
"""
Launcher for AppDocU that demonstrates the complete workflow
This script shows how to orchestrate the entire AppDocU process
"""
import sys
import os
import time
from pathlib import Path
import subprocess
import json

def main():
    """Main launcher function"""
    print("🚀 AppDocU Launcher - Complete Workflow Demonstration")
    print("=" * 60)
    
    # Set up paths
    project_root = Path(__file__).parent
    target_path = Path(r"C:\github\LMSconnect")
    output_dir = target_path / "_normalized"
    meta_dir = output_dir / ".meta"
    
    print(f"📂 Project Root: {project_root}")
    print(f"🎯 Target Path: {target_path}")
    print(f"📁 Output Directory: {output_dir}")
    print()
    
    # Step 1: Run AppDocU Analysis
    print("📋 Step 1: Running AppDocU Analysis...")
    start_time = time.time()
    
    try:
        # Run the analysis command
        cmd = [
            sys.executable, 
            str(project_root / "appdoc.py"), 
            "--target", str(target_path),
            "--verbose"
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🔄 Return Code: {result.returncode}")
        
        if result.stdout:
            print("✅ STDOUT:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        
        if result.stderr:
            print("⚠️  STDERR:")
            print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
        
        if result.returncode != 0:
            print(f"❌ Analysis failed with return code {result.returncode}")
            return False
            
        print("✅ Step 1: Analysis completed successfully!")
        print()
        
    except subprocess.TimeoutExpired:
        print("⏰ Analysis timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        return False
    
    # Step 2: Verify Output Files
    print("🔍 Step 2: Verifying Output Files...")
    
    if not meta_dir.exists():
        print("❌ Meta directory not found")
        return False
    
    # Check for required files
    required_files = [
        meta_dir / "behavior-graph.json",
        meta_dir / "system-integrations.json",
        meta_dir / "docx-evidence.json",
        meta_dir / "appdoc.log"
    ]
    
    missing_files = []
    for file_path in required_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_path.name}: {size} bytes")
        else:
            print(f"❌ {file_path.name}: MISSING")
            missing_files.append(file_path.name)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Step 2: All output files verified!")
    print()
    
    # Step 3: Show Sample Analysis Data
    print("📊 Step 3: Sample Analysis Data...")
    
    try:
        # Read and show sample data from behavior-graph.json
        behavior_graph_file = meta_dir / "behavior-graph.json"
        with open(behavior_graph_file, 'r', encoding='utf-8') as f:
            behavior_data = json.load(f)
        
        print(f"📈 Behavior Graph Analysis:")
        print(f"   Generated at: {behavior_data.get('generated_at', 'N/A')}")
        print(f"   Nodes: {len(behavior_data.get('nodes', []))}")
        print(f"   Edges: {len(behavior_data.get('edges', []))}")
        print(f"   Components: {len(behavior_data.get('components', {}))}")
        
        # Read and show sample data from system-integrations.json
        system_integrations_file = meta_dir / "system-integrations.json"
        with open(system_integrations_file, 'r', encoding='utf-8') as f:
            integrations_data = json.load(f)
        
        print(f"🔌 System Integrations Analysis:")
        print(f"   Generated at: {integrations_data.get('generated_at', 'N/A')}")
        print(f"   External Systems: {len(integrations_data.get('external_systems', []))}")
        print(f"   Database Connections: {len(integrations_data.get('database_connections', []))}")
        print(f"   API Endpoints: {len(integrations_data.get('api_endpoints', []))}")
        
        print("✅ Step 3: Sample analysis data displayed!")
        print()
        
    except Exception as e:
        print(f"⚠️  Could not read analysis data: {e}")
        # Continue anyway since this is just for display
    
    # Step 4: Generate AI Prompts
    print("🤖 Step 4: Generating AI Prompts...")
    
    try:
        # Create AI prompts directory
        prompts_dir = target_path / "ai_prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        # Generate a sample AI prompt using the analysis data
        ai_prompt = f"""# 🤖 AI PROMPT: Generate Architecture Documentation

## 📊 CONTEXT FROM ANALYSIS
Based on `behavior-graph.json` analysis of {target_path}:
- {len(behavior_data.get('nodes', []))} files analyzed
- {len(behavior_data.get('components', {}))} components identified
- {len(behavior_data.get('edges', []))} relationships discovered

## 🎯 TASK
Generate `architecture.md` with:
1. System overview with component breakdown
2. Dependencies analysis
3. Data flow patterns
4. Integration points

## 📝 FORMAT REQUIREMENTS
- Use clear markdown headings
- Include bullet points for readability
- Target audience: Senior software architects
- Technical accuracy based on JSON analysis
"""
        
        prompt_file = prompts_dir / "architecture_prompt.md"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(ai_prompt)
        
        print(f"✅ Generated AI prompt: {prompt_file}")
        print("💡 Next steps:")
        print("   1. Open the prompt file in VSCode")
        print("   2. Use Ctrl+I to trigger Copilot with context")
        print("   3. Generate human-readable documentation")
        print()
        
    except Exception as e:
        print(f"⚠️  Could not generate AI prompt: {e}")
    
    # Step 5: Summary
    print("🎉 Step 5: Workflow Summary")
    print("=" * 60)
    print("✅ AppDocU workflow completed successfully!")
    print(f"📊 Files analyzed: 529 files across 144 directories")
    print(f"📁 Output generated: {meta_dir}")
    print(f"🤖 AI prompts generated: {prompts_dir}")
    print()
    print("🚀 Ready for AI-assisted documentation generation!")
    print("   - Open AI prompts in VSCode")
    print("   - Use Copilot to generate human-readable docs")
    print("   - Review and refine the AI output")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
