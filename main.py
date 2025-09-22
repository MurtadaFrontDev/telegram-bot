import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest

# --- إعدادات الخادم لإبقاء البوت يعمل ---
app = Flask('')


@app.route('/')
def home():
    return "Bot is alive!"


def run_flask():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

CHANNEL_ID = "-1002986989173"

START_MESSAGE = """
ابصقوا ما في داخلكم
And be nice 😇
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة ترحيبية عند إرسال الأمر /start"""
    try:
        await update.message.reply_text(START_MESSAGE)
    except BadRequest as e:
        if "Message to be replied not found" in str(e):
            print("User deleted the /start message quickly. Ignoring.")
        else:
            raise e


async def handle_message(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> None:
    """التعامل مع الرسائل الواردة وإرسالها إلى القناة"""
    message = update.message

    # هذا هو السطر الجديد الذي يحل المشكلة
    if not message:
        return

    # هذا هو السطر الجديد الذي يحل المشكلة
    # ---------------------------------------------
    if message.chat.type != 'private':
        return  # تجاهل أي رسالة ليست في الخاص
    # ---------------------------------------------

    # التأكد من أن CHANNEL_ID تم تغييره
    if CHANNEL_ID == "YOUR_CHANNEL_ID":
        await message.reply_text(
            "⚠️ خطأ: أيها المطور، يرجى تحديد `CHANNEL_ID` في الكود أولاً.")
        return

    try:
        # التعامل مع الرسائل النصية
        if message.text:
            await context.bot.send_message(chat_id=CHANNEL_ID,
                                           text=message.text)

        # التعامل مع الصور
        elif message.photo:
            await context.bot.send_photo(chat_id=CHANNEL_ID,
                                         photo=message.photo[-1].file_id,
                                         caption=message.caption)

        # التعامل مع الفيديو
        elif message.video:
            await context.bot.send_video(chat_id=CHANNEL_ID,
                                         video=message.video.file_id,
                                         caption=message.caption)

        else:
            await message.reply_text(
                "عذراً، هذا النوع من الرسائل غير مدعوم حالياً.")
            return

        # إرسال رسالة تأكيد للمستخدم
        await message.reply_text("رسالتك وصلت بكل سرية 😏")

    except Exception as e:
        print(f"Error forwarding message: {e}")
        await message.reply_text(
            "حدث خطأ أثناء إرسال الرسالة. قد لا يملك البوت صلاحيات كافية في القناة."
        )


def main() -> None:
    """تشغيل البوت"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()application = Application.builder().token(TELEGRAM_BOT_TOKEN).connect_timeout(30).read_timeout(30).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO | filters.VIDEO | filters.FORWARDED,
            handle_message))

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    keep_alive()
    main()
