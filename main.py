import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Google Sheets setup ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
# Replace with your sheet URL and gid
SHEET = client.open_by_url("https://docs.google.com/spreadsheets/d/1nFHYQKEmC5m88nb9p5kSs_cbFQ9tbsQx9PtSmktiRiM/edit?gid=0#gid=0").get_worksheet(0)

# --- Telegram Bot setup ---
BOT_TOKEN = "8410780178:AAFC0sJX0C6KMr65Q0y7xJMdTzokXcfBTXw"
ADMIN_CHAT_ID = 1276776109  # Replace with your admin chat id

# --- Conversation states ---
ASK_PHONE, ASK_QUESTION = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu aleykum, telefon raqamingizni qoldiring masalan (+998971234567)"
    )
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user = update.message.from_user

    # Save username + phone to sheet
    SHEET.append_row([str(user.id), user.username or "N/A", phone])

    await update.message.reply_text("Savolingizni yuborishingiz mumkun ✅")
    return ASK_QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.strip()
    user = update.message.from_user
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save question to sheet
    SHEET.append_row([str(user.id), user.username or "N/A", question, date_str])

    # Forward to admin chat
    msg = f"Sana: {date_str}\nUser: @{user.username or 'N/A'}\nSavol: {question}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

    await update.message.reply_text("Savolingiz yuborildi ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi ❌")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
