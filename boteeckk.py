import os
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# === НАСТРОЙКИ ===
TOKEN = "8410470590:AAF_kCe9xBdtdggZ6Jz1I9UNPaLT0PnhKPY"
ADMIN_ID = 509466119

PRICE_SINGLE = 8   # цена за страницу
PRICE_DOUBLE = 9   # цена за лист (двусторонняя)

USERS_FILE = "users.txt"


# === ФУНКЦИИ ДЛЯ РАССЫЛКИ ===
def save_user(user_id):
    with open(USERS_FILE, "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        return []


# === СОСТОЯНИЯ ===
WAITING_FILE, SELECTING_MODE, ENTERING_RANGES, ENTERING_TOPICS, SELECTING_PRINT_TYPE, CONFIRMING = range(6)


# === ПАРСИНГ ДИАПАЗОНОВ ===
def parse_ranges(text):
    ranges = []
    total_pages = 0
    text = text.replace(" ", "")
    parts = text.split(",")
    for part in parts:
        if "-" in part:
            a, b = part.split("-")
            a, b = int(a), int(b)
            if a > b:
                a, b = b, a
            ranges.append(f"{a}-{b}")
            total_pages += b - a + 1
        else:
            page = int(part)
            ranges.append(f"{page}")
            total_pages += 1
    return ranges, total_pages


# === ХЕНДЛЕРЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    await update.message.reply_text(
        "Привет!!\n"
        "Я помогу рассчитать тебе стоимость печати, а Даше принять заказ и не запутаться💅\n\n"
        "〰️Если возникнет вопрос — напиши админке @thiod\n\n"
        "А сейчас прикрепи файлик сюда ⤵️"
    )
    return WAITING_FILE


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        await update.message.reply_text("Пожалуйста, прикрепи файл 📎")
        return WAITING_FILE

    context.user_data["file_id"] = document.file_id
    context.user_data["file_name"] = document.file_name

    keyboard = [["Страницы", "Главы/темы"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Принято! ✅\nЧто укажешь?",
        reply_markup=reply_markup
    )
    return SELECTING_MODE


async def mode_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip().lower()
    if choice == "страницы":
        await update.message.reply_text("Укажи диапазон страниц (например: 1-5, 7, 10-12)")
        return ENTERING_RANGES
    elif choice == "главы":
        await update.message.reply_text("Напиши какие главы/темы нужно распечатать")
        return ENTERING_TOPICS
    else:
        await update.message.reply_text("Выбери кнопкой: Страницы или Главы")
        return SELECTING_MODE


async def ranges_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    try:
        ranges, total_pages = parse_ranges(user_input)
    except Exception:
        await update.message.reply_text("Где-то опшипка( (примеры: 1-5, 7, 10-12")
        return ENTERING_RANGES

    context.user_data["ranges"] = ranges
    context.user_data["total_pages"] = total_pages

    await update.message.reply_text(
        "О как! Диапазоны:\n" + "\n".join([f"• {r}" for r in ranges])
    )

    keyboard = [["Односторонняя", "Двусторонняя"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Теперь выбери тип печати:", reply_markup=reply_markup)
    return SELECTING_PRINT_TYPE


async def enter_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = update.message.text.strip()
    context.user_data["topics"] = topics

    keyboard = [["Подтвердить", "Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        f"Ты указал(а): {topics}\n\nПодтвердить заказ?",
        reply_markup=reply_markup
    )
    return CONFIRMING


async def print_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text.lower()
    if user_choice not in ["односторонняя", "двусторонняя"]:
        await update.message.reply_text("Пожалуйста, выбери кнопочкой внизу")
        return SELECTING_PRINT_TYPE

    context.user_data["print_type"] = user_choice

    num_pages = context.user_data["total_pages"]
    if user_choice == "односторонняя":
        sheets = num_pages
        total_cost = sheets * PRICE_SINGLE
    else:
        sheets = (num_pages + 1) // 2
        total_cost = sheets * PRICE_DOUBLE

    context.user_data["sheets"] = sheets
    context.user_data["total_cost"] = total_cost

    details = (
        f"Файл: {context.user_data['file_name']}\n"
        f"Диапазоны: {', '.join(context.user_data['ranges'])}\n"
        f"Тип печати: {context.user_data['print_type']}\n"
        f"Количество страниц: {num_pages}\n"
        f"Итого: {total_cost}₽"
    )

    keyboard = [["Подтвердить", "Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(f"Итог:\n\n{details}\n\nПодтвердить заказ?", reply_markup=reply_markup)
    return CONFIRMING


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip().lower()
    file_id = context.user_data.get("file_id")
    file_name = context.user_data.get("file_name")

    if "подтвердить" in choice:
        if "ranges" in context.user_data:  # заказ по страницам
            print_type = context.user_data.get("print_type")
            num_pages = context.user_data.get("total_pages")
            total_cost = context.user_data.get("total_cost")
            ranges = context.user_data.get("ranges")

            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=file_id,
                filename=file_name,
                caption=(
                    f"📄 Стучится потенциальная денежка!\n"
                    f"Диапазоны: {', '.join(ranges)}\n"
                    f"Тип печати: {print_type}\n"
                    f"Количество страниц: {num_pages}\n"
                    f"Стоимость: {total_cost}₽\n"
                    f"От @{update.effective_user.username or update.effective_user.id}"
                )
            )

        elif "topics" in context.user_data:  # заказ по главам
            topics = context.user_data.get("topics")

            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=file_id,
                filename=file_name,
                caption=(
                    f"📄 Новый заказ!\n"
                    f"Темы/главы: {topics}\n"
                    f"От @{update.effective_user.username or update.effective_user.id}"
                )
            )

        await update.message.reply_text(
            "Понято и принято! ✅\nАдминка сообщит статус, когда будет свободна",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text("Блин( Буду ждать снова", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Галя отмена!!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# === РАССЫЛКА ===
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Это только для админки(( 🚫")
        return

    if not context.args:
        await update.message.reply_text("Используй так: /post текст_сообщения")
        return

    text = " ".join(context.args)
    users = load_users()
    sent, failed = 0, 0

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"Рассылка завершена ✅\nУспешно: {sent}\nНе доставлено: {failed}")


# === MAIN ===
def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FILE: [MessageHandler(filters.Document.ALL, handle_file)],
            SELECTING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mode_selected)],
            ENTERING_RANGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ranges_received)],
            ENTERING_TOPICS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_topics)],
            SELECTING_PRINT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, print_type_selected)],
            CONFIRMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("post", post))

    print("МАШИНА ЗАПУЩЕНА...")
    app.run_polling()


if __name__ == "__main__":
    main()
