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
from database import create_registration, init_db, approve_registration, reject_registration, get_pending_registrations, get_registration
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
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📱 Great! Now please provide your Telegram username (without @).")
    return ASK_USERNAME


async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text.strip("@")  # Remove @ if user includes it

    # Save registration
    telegram_id = update.effective_user.id
    create_registration(
        telegram_id,
        context.user_data["full_name"],
        context.user_data["phone"],
        context.user_data["username"]
    )

    await update.message.reply_text(
        f"✅ Thanks {context.user_data['full_name']}!\n"
        f"Phone: {context.user_data['phone']}\n"
        f"Telegram username: @{context.user_data['username']}\n\n"
        f"Your registration is submitted and awaiting approval!"
    )
    return ConversationHandler.END


# ---------------------------
# Admin commands
# ---------------------------
async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied.")
        return

    pending_regs = get_pending_registrations()
    if not pending_regs:
        await update.message.reply_text("No pending registrations.")
        return

    message = "📋 Pending Registrations:\n\n"
    for reg in pending_regs:
        message += f"ID: {reg['id']}\nName: {reg['full_name']}\nPhone: {reg['phone']}\nUsername: @{reg['username']}\n\n"
    message += "Use /approve <id> or /reject <id>"
    await update.message.reply_text(message)


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied.")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /approve <registration_id>")
        return

    try:
        reg_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid registration ID.")
        return

    reg = get_registration(reg_id)
    if not reg:
        await update.message.reply_text("❌ Registration not found.")
        return

    if reg['status'] != 'PENDING':
        await update.message.reply_text("❌ Registration is not pending.")
        return

    approve_registration(reg_id)

    # Send approval message with group link
    await bot.send_message(
        chat_id=reg["telegram_id"],
        text=f"✅ Your registration has been approved!\n\nJoin the workshop group: {GROUP_LINK}"
    )

    await update.message.reply_text(f"✅ Registration {reg_id} approved.")


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied.")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /reject <registration_id>")
        return

    try:
        reg_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid registration ID.")
        return

    reg = get_registration(reg_id)
    if not reg:
        await update.message.reply_text("❌ Registration not found.")
        return

    if reg['status'] != 'PENDING':
        await update.message.reply_text("❌ Registration is not pending.")
        return

    reject_registration(reg_id)

    await bot.send_message(
        chat_id=reg["telegram_id"],
        text="❌ Your registration has been rejected. Please contact support."
    )

    await update.message.reply_text(f"❌ Registration {reg_id} rejected.")


# ---------------------------
# Conversation handler
# ---------------------------
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_username)],
    },
    fallbacks=[],
)

# ---------------------------
# Register handlers
# ---------------------------
app.add_handler(conv_handler)
app.add_handler(CommandHandler("pending", pending))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))

# ---------------------------
# Run bot
# ---------------------------
if __name__ == "__main__":
    init_db()
    print("🤖 Bot is running...")
    app.run_polling()
