# bot.py

import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from database import create_registration, init_db
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

# ---------------------------
# Image Base Directory (SAFE PATH)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

WELCOME_IMAGE = os.path.join(IMAGES_DIR, "welcome.png")

# ---------------------------
# Conversation states
# ---------------------------
ASK_NAME, ASK_PHONE = range(2)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# ---------------------------
# /start command
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if os.path.exists(WELCOME_IMAGE):
        with open(WELCOME_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="👋 Welcome! To register for the workshop, please tell me your full name."
            )
    else:
        await update.message.reply_text(
            "👋 Welcome! To register for the workshop, please tell me your full name."
        )

    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("📞 Great! Now send me your phone number.")
    return ASK_PHONE


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    telegram_username = update.effective_user.username or "No username"
    context.user_data["username"] = telegram_username

    # Save registration
    telegram_id = update.effective_user.id
    create_registration(
        telegram_id,
        context.user_data["full_name"],
        context.user_data["phone"],
        telegram_username
    )

    await update.message.reply_text(
        f"✅ Thanks {context.user_data['full_name']}!\n"
        f"Telegram username: @{telegram_username}\n"
        f"Phone: {context.user_data['phone']}\n\n"
        f"You are now registered for the workshop!"
    )
    return ConversationHandler.END


# ---------------------------
# Conversation handler
# ---------------------------
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
    },
    fallbacks=[],
)

# ---------------------------
# Register handlers
# ---------------------------
app.add_handler(conv_handler)

# ---------------------------
# Run bot
# ---------------------------
if __name__ == "__main__":
    init_db()
    print("🤖 Bot is running...")
    app.run_polling()
