# 🍏 Apply – The GenAI Multi-Modal Telegram Assistant

A production-grade, asynchronous Telegram bot architecture integrating Google Gemini, local RAG pipelines, and multi-modal vision processing with isolated state management.

---

## 🏛️ System Architecture & Design

The application follows a decoupled, service-oriented structure designed to isolate Telegram routing logic from AI inference pipelines:
### Core Execution Modules
1. **Asynchronous Interface (`main.py`)**: Built on `python-telegram-bot` leveraging non-blocking polling, session-scoped memory dictionaries, and fallback handlers.
2. **Contextual RAG Subsystem (`rag/pipeline.py`)**: Scans the local filesystem directory, compiles textual context dynamically on each query, and passes grounded prompts to `gemini-2.5-flash`.
3. **Vision Processing Subsystem (`vision/caption.py`)**: Handles binary buffer extraction from Telegram image payloads and executes multi-modal inference via Google GenAI SDK parts.

---

## ⚡ Key Capabilities

* **Grounded Question Answering**: Limits LLM hallucination by injecting local document context directly into the generation payload alongside source tracking.
* **Sliding-Window Conversational Memory**: Retains the last 5 turns of user-assistant dialog per session to enable contextual follow-up questions.
* **Dynamic Vision Analysis**: Converts image buffers on the fly to generate descriptive captions and tags.
* **Push-Protection Compliant**: Strict environment-variable abstraction ensures zero secret leakage into version control.

---

## 🚀 Quick Start & Deployment

python -m venv .venv
# Activate environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Install runtime requirements
pip install python-telegram-bot google-genai python-dotenv

TELEGRAM_TOKEN=your_telegram_bot_token

GOOGLE_API_KEY=your_google_genai_api_key

BOT_USERNAME=@Appy_apple_bot
