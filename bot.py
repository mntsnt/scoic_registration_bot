# bot.py

import uuid
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
    create_order,
    add_proof,
    mark_approved,
    mark_rejected,
    get_order,
    get_latest_pending_order
)
from config import BOT_TOKEN, WORKSHOP_PRICE, ADMIN_ID

logging.basicConfig(level=logging.INFO)

# ---------------------------
# Image Base Directory (SAFE PATH)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

WELCOME_IMAGE = os.path.join(IMAGES_DIR, "welcome.png")
PAYMENT_IMAGE = os.path.join(IMAGES_DIR, "payment.png")
PROOF_IMAGE = os.path.join(IMAGES_DIR, "proof_received.png")

# ---------------------------
# Conversation states
# ---------------------------
ASK_NAME, ASK_PHONE = range(2)

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
    telegram_username = update.effective_user.username or "No username"
    context.user_data["username"] = telegram_username

    await update.message.reply_text(
        f"✅ Thanks {context.user_data['full_name']}!\n"
        f"Telegram username: @{telegram_username}\n"
        f"Phone: {context.user_data['phone']}\n\n"
        f"Now you can proceed to pay using /pay"
    )
    return ConversationHandler.END


# ---------------------------
# /pay command
# ---------------------------
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    order_id = str(uuid.uuid4())

    create_order(
        telegram_id,
        order_id,
        WORKSHOP_PRICE,
        full_name=context.user_data.get("full_name"),
        phone=context.user_data.get("phone"),
        username=context.user_data.get("username")
    )

    if os.path.exists(PAYMENT_IMAGE):
        with open(PAYMENT_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    f"💰 Please pay {WORKSHOP_PRICE} ETB.\n"
                    f"After payment using Telebirr, send your transaction ID here.\n"
                    f"Your order ID is: {order_id}"
                )
            )
    else:
        await update.message.reply_text(
            f"💰 Please pay {WORKSHOP_PRICE} ETB.\n"
            f"After payment using Telebirr, send your transaction ID here.\n"
            f"Your order ID is: {order_id}"
        )


# ---------------------------
# Handle payment proof
# ---------------------------
async def proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if update.message.text:
        proof = update.message.text
    elif update.message.photo:
        proof = update.message.photo[-1].file_id
    else:
        await update.message.reply_text("Send a screenshot or transaction ID only.")
        return

    order = get_latest_pending_order(telegram_id)
    if not order:
        await update.message.reply_text("No pending order found. Please /pay first.")
        return

    order_id = order["order_id"]
    add_proof(order_id, proof)

    if os.path.exists(PROOF_IMAGE):
        with open(PROOF_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"✅ Proof received for order {order_id}. Awaiting admin approval."
            )
    else:
        await update.message.reply_text(
            f"✅ Proof received for order {order_id}. Awaiting admin approval."
        )

    # Notify admin
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📌 New payment proof received!\n"
            f"Order ID: {order_id}\n"
            f"Full Name: {order['full_name']}\n"
            f"Phone: {order['phone']}\n"
            f"Telegram: @{order['username']}\n"
            f"Proof: {proof}\n\n"
            f"Use /approve {order_id} or /reject {order_id}"
        )
    )


# ---------------------------
# Admin commands
# ---------------------------
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /approve <order_id>")
        return

    order_id = " ".join(context.args).strip()
    order = get_order(order_id)

    if not order:
        await update.message.reply_text("❌ Order not found.")
        return

    mark_approved(order_id)

    await bot.send_message(
        chat_id=order["telegram_id"],
        text="✅ Your payment has been approved! You are now registered for the workshop."
    )

    await update.message.reply_text(f"✅ Order {order_id} approved.")


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /reject <order_id>")
        return

    order_id = " ".join(context.args).strip()
    order = get_order(order_id)

    if not order:
        await update.message.reply_text("❌ Order not found.")
        return

    mark_rejected(order_id)

    await bot.send_message(
        chat_id=order["telegram_id"],
        text="❌ Your payment has been rejected. Please contact support."
    )

    await update.message.reply_text(f"❌ Order {order_id} rejected.")


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
app.add_handler(CommandHandler("pay", pay))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, proof_handler))

# ---------------------------
# Run bot
# ---------------------------
if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run_polling()
