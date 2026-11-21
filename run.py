import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    env_file = os.path.join(backend_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    print("\n" + "="*62)
    print(" 🏛️  CivicResolve: AI Citizen Grievance Platform")
    print("    PromptWars x GDG on-Campus PSG iTech Hackathon")
    print("="*62)
    print(" 🚀 Live Web Application: http://localhost:8000")
    print(" 📖 Interactive API Docs: http://localhost:8000/docs")
    print(f" ✨ Gemini API Configured: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO (Running in Resilient Heuristic AI Mode)'}")
    print("="*62 + "\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
