import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMIN_ID, GROUP_LINK
from database import (
    init_db,
    create_registration,
    approve_registration,
    reject_registration,
    get_registration
)

logging.basicConfig(level=logging.INFO)

# Conversation states
ASK_NAME, ASK_PHONE = range(2)

# Image path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WELCOME_IMAGE = os.path.join(BASE_DIR, "images", "welcome.png")


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(WELCOME_IMAGE):
        with open(WELCOME_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="👋 Welcome! Please enter your full name to register."
            )
    else:
        await update.message.reply_text(
            "👋 Welcome! Please enter your full name to register."
        )

    return ASK_NAME


# ---------------- ASK NAME ----------------
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text

    await update.message.reply_text("📞 Now send your phone number.")
    return ASK_PHONE


# ---------------- ASK PHONE ----------------
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    user_id = user.id
    username = user.username or "No username"
    full_name = context.user_data["full_name"]
    phone = update.message.text

    # Save to DB
    create_registration(user_id, full_name, phone, username)

    await update.message.reply_text(
        "✅ Registration submitted!\nWaiting for admin approval..."
    )

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📌 New Registration\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Name: {full_name}\n"
            f"📞 Phone: {phone}\n"
            f"💬 Username: @{username}\n\n"
            f"Approve: /approve {user_id}\n"
            f"Reject: /reject {user_id}"
        )
    )

    return ConversationHandler.END


# ---------------- APPROVE ----------------
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    user_id = int(context.args[0])
    user_data = get_registration(user_id)

    if not user_data:
        await update.message.reply_text("❌ User not found.")
        return

    approve_registration(user_id)

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "🎉 You are approved!\n\n"
            f"Join the group here:\n{GROUP_LINK}"
        )
    )

    await update.message.reply_text(f"✅ Approved {user_id}")


# ---------------- REJECT ----------------
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /reject <user_id>")
        return

    user_id = int(context.args[0])
    user_data = get_registration(user_id)

    if not user_data:
        await update.message.reply_text("❌ User not found.")
        return

    reject_registration(user_id)

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ Your registration was rejected."
    )

    await update.message.reply_text(f"❌ Rejected {user_id}")


# ---------------- MAIN ----------------
def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()