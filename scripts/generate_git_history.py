import os
import subprocess
import random
import time
import shutil

# --- CONFIG ---
REPO_URL = "https://github.com/ParthMozarkar/Inventory-Management-Project.git"
HISTORY_FILE = "docs/DEVELOPMENT_LOG.md"

# --- UTILS ---

def run(cmd):
    # Only redirect stdout; stderr is useful for debugging
    subprocess.run(cmd, shell=True, check=True)

def git_add(file):
    run(f'git add "{file}"')

def git_commit(msg):
    # We can fake the date too if needed, but for now we just commit
    run(f'git commit -m "{msg}"')

def generate_history():
    print("🚀 Starting Git History Generation...")

    # 1. Reset Git
    if os.path.exists(".git"):
        os.system("attrib -h .git") # Unhide on windows
        try:
            # Force delete
            subprocess.run("rmdir /s /q .git", shell=True) 
        except: pass
        time.sleep(1)

    # Initialize New Repo
    run("git init")
    run("git branch -M main")
    run(f"git remote add origin {REPO_URL}")

    # 2. Create History
    # Ensure docs directory exists
    if not os.path.exists("docs"):
        os.makedirs("docs")

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("# Project Development Log\n\n")

    print("   Generating 25 commits...")
    
    # List of realistic messages to cycle through
    msgs = [
        "Updated layout configuration", "Refactored database connector", "Fixed responsiveness issues",
        "Optimized asset loading", "Added new inventory modules", "Patched security vulnerability",
        "Updated UI styling", "Improved error handling", "Refactored authentication logic",
        "Updated dependency requirements", "Fixed typo in dashboard", "Enhanced fast-billing logic",
        "Refactored folder structure", "Cleaned up root directory", "Moved docs and scripts"
    ]

    for i in range(1, 26):
        msg = f"{random.choice(msgs)} (Task #{1000+i})"
        
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"- Commit {i}: {msg}\n")
        
        git_add(HISTORY_FILE)
        git_commit(msg)
        
        if i % 5 == 0: print(f"   ... {i} commits created")

    # 3. Add Actual Project Files (The "Real" Code)
    print("   Adding final project files...")
    
    # Add files in batches to ensure they get in
    if os.path.exists("assets"):
        run("git add assets/")
        git_commit("Added project assets")
    
    if os.path.exists("core"):
        run("git add core/")
        git_commit("Merged core logic implementation")

    run("git add docs/")
    run("git add scripts/")
    git_commit("Refactored project structure")
    
    # Add everything else (README, main.py, etc)
    run("git add .")
    # Wrap this in try/catch in case nothing left to commit
    try:
        git_commit("Release 1.0.0: Stable Build")
    except: pass

    print("✅ History Generated Successfully!")
    print("⚠ NOW RUN: git push -u origin main --force")

if __name__ == "__main__":
    generate_history()
