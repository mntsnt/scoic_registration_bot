# bot.py

import logging
from pathlib import Path
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

import config
import database

# Enable logging
logging.basicConfig(level=logging.INFO)

# Conversation states
NAME, PHONE = range(2)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_image = Path("images") / "welcome.png"
    if welcome_image.exists():
        with welcome_image.open("rb") as img:
            await update.message.reply_photo(
                photo=img,
                caption="Welcome! 👋\nPlease enter your full name:"
            )
    else:
        logging.warning("Welcome image not found at %s", welcome_image)
        await update.message.reply_text(
            "Welcome! 👋\nPlease enter your full name:"
        )

    return NAME


# Get name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "Please enter your phone number:"
    )
    return PHONE


# Get phone number
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact

    if contact:
        phone = contact.phone_number
    else:
        phone = update.message.text

    name = context.user_data["name"]
    user_id = update.message.from_user.id
    username_value = update.message.from_user.username
    username_display = f"@{username_value}" if username_value else "(no username)"

    database.add_user(user_id, name, phone, username=username_value)

    # Send to admin
    for admin_id in config.ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"📥 New Registration\n\n"
                f"👤 Name: {name}\n"
                f"📞 Phone: {phone}\n"
                f"🆔 User ID: {user_id}\n"
                f"🆔 User Name: {username_display}\n\n"
                f"Approve with:\n/approve {user_id}"
            )
        )

    await update.message.reply_text(
        "✅ Your data has been submitted for approval.\nPlease wait..."
    )

    return ConversationHandler.END


# Admin approval command
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in config.ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve <user_id1> [user_id2 ...] or /approve all")
        return

    all_users = database.users
    approved_ids = []
    not_found_ids = []

    if context.args[0].lower() == "all":
        target_ids = [int(uid) for uid in all_users.keys() if not all_users[uid].get("approved")]
    else:
        target_ids = []
        for arg in context.args:
            try:
                target_ids.append(int(arg))
            except ValueError:
                continue

    for uid in target_ids:
        user = database.get_user(uid)
        if not user:
            not_found_ids.append(uid)
            continue
        if user.get("approved"):
            continue

        database.approve_user(uid)
        approved_ids.append(uid)

        # Notify user
        await context.bot.send_message(
            chat_id=uid,
            text=(
                "🎉 Your registration has been approved!\n\n"
                f"Join the workshop group here:\n{config.WORKSHOP_GROUP_LINK}"
            )
        )

    resp_parts = []
    if approved_ids:
        resp_parts.append(f"✅ Approved: {', '.join(str(i) for i in approved_ids)}")
    if not_found_ids:
        resp_parts.append(f"⚠️ Not found: {', '.join(str(i) for i in not_found_ids)}")
    if not resp_parts:
        resp_parts.append("ℹ️ No new users were approved (already approved or invalid IDs).")

    await update.message.reply_text("\n".join(resp_parts))


# Admin list users command
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in config.ADMIN_IDS:
        return

    all_users = database.users
    if not all_users:
        await update.message.reply_text("No users registered yet.")
        return

    approved = []
    pending = []
    for uid, info in all_users.items():
        username_value = info.get("username")
        if username_value:
            user_name_text = f"@{username_value}"
        else:
            user_name_text = "(no username)"
        line = f"{uid}: {info['name']} ({info['phone']}) {user_name_text}"
        if info.get("approved"):
            approved.append(line)
        else:
            pending.append(line)

    text_parts = []
    if approved:
        text_parts.append("✅ Approved users:")
        text_parts.extend(approved)
    else:
        text_parts.append("✅ Approved users: none")

    if pending:
        text_parts.append("\n🕒 Pending users:")
        text_parts.extend(pending)
    else:
        text_parts.append("\n🕒 Pending users: none")

    await update.message.reply_text("\n".join(text_parts))


# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process cancelled.")
    return ConversationHandler.END


def main():
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Set the BOT_TOKEN environment variable before starting the bot.")

    if not config.ADMIN_IDS:
        raise RuntimeError("ADMIN_IDS is not configured. Set ADMIN_ID or ADMIN_IDS environment variable.")

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("list_users", list_users))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()