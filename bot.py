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
from database import (
    create_registration, init_db, approve_registration,
    reject_registration, get_pending_registrations, get_registration
)
from config import BOT_TOKEN, ADMIN_ID, GROUP_LINK

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
ASK_NAME, ASK_PHONE, ASK_USERNAME = range(3)

app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = app.bot

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
    user = update.effective_user
    telegram_id = user.id
    username = user.username or "No username"

    registrations[telegram_id] = {
        "full_name": context.user_data["full_name"],
        "phone": update.message.text,
        "username": username
    }

    await update.message.reply_text(
        f"✅ Thanks {context.user_data['full_name']}!\n"
        f"📞 Phone: {update.message.text}\n\n"
        f"⏳ Your registration is submitted.\n"
        f"Waiting for admin approval..."
    )

    # Notify Admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📌 New Registration!\n\n"
            f"🆔 User ID: {telegram_id}\n"
            f"👤 Name: {context.user_data['full_name']}\n"
            f"📞 Phone: {update.message.text}\n"
            f"💬 Telegram: @{username}\n\n"
            f"Approve with:\n/approve {telegram_id}"
        )
    )

    return ConversationHandler.END


# ---------------------------
# APPROVE USER
# ---------------------------
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed to use this.")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /approve <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    if user_id not in registrations:
        await update.message.reply_text("❌ User not found.")
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 You have been approved for the workshop!\n\n"
                "👉 Join the official group here:\n"
                f"{GROUP_LINK}"
            )
        )

        await update.message.reply_text(f"✅ Approved user {user_id}")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message.\nError: {e}")


# ---------------------------
# REJECT USER (optional)
# ---------------------------
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /reject <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    if user_id not in registrations:
        await update.message.reply_text("❌ User not found.")
        return

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ Your registration was not approved. Please contact admin."
    )

    await update.message.reply_text(f"❌ Rejected user {user_id}")


# ---------------------------
# Conversation handler
# ---------------------------
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
    },
    fallbacks=[]
)

# ---------------------------
# Register handlers
# ---------------------------
app.add_handler(conv_handler)
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))

# ---------------------------
# Run bot
# ---------------------------
if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run_polling()
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username or "No username"

    registrations[telegram_id] = {
        "full_name": context.user_data["full_name"],
        "phone": update.message.text,
        "username": username
    }

    await update.message.reply_text(
        f"✅ Thanks {context.user_data['full_name']}!\n"
        f"📞 Phone: {update.message.text}\n\n"
        f"⏳ Your registration is submitted.\n"
        f"Waiting for admin approval..."
    )

    # Notify Admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📌 New Registration!\n\n"
            f"🆔 User ID: {telegram_id}\n"
            f"👤 Name: {context.user_data['full_name']}\n"
            f"📞 Phone: {update.message.text}\n"
            f"💬 Telegram: @{username}\n\n"
            f"Approve with:\n/approve {telegram_id}"
        )
    )

    return ConversationHandler.END


# ---------------------------
# APPROVE USER
# ---------------------------
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed to use this.")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /approve <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    if user_id not in registrations:
        await update.message.reply_text("❌ User not found.")
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 You have been approved for the workshop!\n\n"
                "👉 Join the official group here:\n"
                f"{GROUP_LINK}"
            )
        )

        await update.message.reply_text(f"✅ Approved user {user_id}")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message.\nError: {e}")


# ---------------------------
# REJECT USER (optional)
# ---------------------------
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /reject <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    if user_id not in registrations:
        await update.message.reply_text("❌ User not found.")
        return

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ Your registration was not approved. Please contact admin."
    )

    await update.message.reply_text(f"❌ Rejected user {user_id}")


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
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))

# ---------------------------
# Run bot
# ---------------------------
if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run_polling()