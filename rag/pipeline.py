import os
from pathlib import Path
from google import genai
from google.genai import types

# Initialize client with direct string key instead of os.getenv()
client = genai.Client(api_key="GOOGLE_API_KEY")

DOCS_DIR = Path("docs")

def reload_docs():
    """Stub or logic to reload documents if you index them locally."""
    if not DOCS_DIR.exists():
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
    return "Documents directory checked/reloaded."

def rag_answer(query: str) -> str:
    """Answers a query using local files or fallback context via Gemini."""
    try:
        # Check if docs folder has any files
        context = ""
        if DOCS_DIR.exists():
            files = list(DOCS_DIR.glob("*.*"))
            if files:
                for file in files:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        context += f"\n--- {file.name} ---\n" + f.read()

        # Construct prompt with context if available
        prompt = f"Use the following document context if relevant to answer the user query.\n\nContext:\n{context}\n\nQuery: {query}" if context else query

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error processing query: {str(e)}"