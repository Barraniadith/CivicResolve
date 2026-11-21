import os
import uvicorn

if __name__ == "__main__":
    # Load .env if present
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    print("\n=======================================================")
    print(" 🏛️ CivicResolve: AI Citizen Grievance Platform")
    print(" PromptWars x GDG on-Campus PSG iTech Hackathon")
    print("=======================================================")
    print("🚀 Server starting at: http://localhost:8000")
    print("📖 API Interactive Docs: http://localhost:8000/docs")
    print(f"✨ Gemini API Key Configured: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO (Running in resilient Heuristic AI mode)'}")
    print("=======================================================\n")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
