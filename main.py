import os
import logging
from typing import Final
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()

# Define the tokens so other files can import them cleanly
TOKEN: Final = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY: Final = os.getenv("GOOGLE_API_KEY") 
BOT_USERNAME: Final = "@Appy_apple_bot"

# Imports for RAG and Vision modules
try:
    from rag.pipeline import rag_answer, reload_docs
    RAG_ENABLED = True
except Exception as e:
    print(f"RAG Load Error: {e}")
    RAG_ENABLED = False

try:
    from vision.caption import generate_caption
    VISION_ENABLED = True
except Exception as e:
    print(f"Vision Load Error: {e}")
    VISION_ENABLED = False

# --------> LOGGING <--------
logging.basicConfig(level=logging.INFO)

# --------> USER MEMORY STORAGE <--------
user_memory = {}
user_image_mode = {}

# --------> BASIC COMMANDS <--------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START triggered")
    await update.message.reply_text(
        "Hello! Thanks for chatting with me! I am an apple!\n\n"
        "Available Commands:\n"
        "/ask <query> - Ask from your documents\n"
        "/reload - Reload your documents\n"
        "/image - Enable image processing mode\n"
        "/reset - Clear your chat history\n"
        "/help - Show help options"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am an apple! Here is what you can do:\n"
        "- Type anything for basic chat responses.\n"
        "- Use /ask <query> to search through your project documents.\n"
        "- Use /image then send a photo for captioning.\n"
        "- Use /reload to refresh documents."
    )

async def custom_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")

# --------> CHAT RESPONSE LOGIC <--------
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if "hello" in processed:
        return "Hey there!"
    if "how are you" in processed:
        return "I am good!"
    if "i love python" in processed:
        return "Great start"

    return "I do not understand what you wrote..."

# --------> RAG QUERY HANDLER <--------
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not RAG_ENABLED:
        await update.message.reply_text("RAG pipeline module is not loaded yet.")
        return
    try:
        user_id = update.effective_user.id
        query = " ".join(context.args)

        if not query:
            query = update.message.text

        if not query:
            await update.message.reply_text("Please provide a query.")
            return

        await update.message.reply_text("Thinking... ")

        if user_id not in user_memory:
            user_memory[user_id] = []

        user_memory[user_id].append({"role": "user", "content": query})

        context_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in user_memory[user_id][-5:]]
        )

        answer, sources = rag_answer(context_text)

        user_memory[user_id].append({"role": "assistant", "content": answer})

        response = f"{answer}\n\nSource: {', '.join(sources) if sources else 'None'}"
        await update.message.reply_text(response)

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text(f"Error: {str(e)}")

# --------> RELOAD DOCUMENTS COMMAND <--------
async def reload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not RAG_ENABLED:
        await update.message.reply_text("RAG module not available.")
        return
    try:
        reload_docs()
        await update.message.reply_text("Documents reloaded successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# --------> RESET MEMORY <--------
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_memory:
        user_memory[user_id] = []
    await update.message.reply_text("Memory cleared successfully.")

# --------> VISION HANDLING <--------
async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not VISION_ENABLED:
        await update.message.reply_text("Vision module not available.")
        return

    user_id = update.effective_user.id
    user_image_mode[user_id] = True
    await update.message.reply_text("Send me an image and I'll describe it for you!")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if not user_image_mode.get(user_id):
            return

        photo = update.message.photo[-1]
        file = await photo.get_file()

        os.makedirs("temp", exist_ok=True)
        path = f"temp/{user_id}.jpg"
        await file.download_to_drive(path)

        await update.message.reply_text("Processing image... ")
        caption, tags = generate_caption(path)

        await update.message.reply_text(f"🖼 Caption: {caption}\n🏷 Tags: {', '.join(tags)}")
        user_image_mode[user_id] = False

    except Exception as e:
        print("Vision error:", e)
        await update.message.reply_text("Error processing image.")

# --------> GENERAL MESSAGE HANDLER <--------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print("Bot:", response)
    await update.message.reply_text(response)

# --------> ERROR HANDLER <--------
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# --------> MAIN ENTRY POINT <--------
def main():
    TOKEN = "8798997310:AAGOT5pcXoiK3iGctjtOljpvse2O0PHxtUo"
    
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN not set")
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Register Command Handlers
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("custom", custom_cmd))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("image", image_cmd))
    app.add_handler(CommandHandler("reload", reload_cmd))
    app.add_handler(CommandHandler("reset", reset))

    # Register Message Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Register Error Handler
    app.add_error_handler(error)

    print("Bot is running...")
    app.run_polling(poll_interval=3, drop_pending_updates=True)

if __name__ == "__main__":
    main()
