from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
TOKEN = "8410470590:AAFaHaUA2E6XrfwNxsCysP0McD4y3HRwyzs"
PRICE_SINGLE = 8
PRICE_DOUBLE = 9
SELECTING_PRINT_TYPE, ENTERING_PAGES = range(2)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['односторонняя', 'двусторонняя']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        'привет! ты в боте, который поможет мне с тобой связаться и распечатать любой файл! для личной консультации в тг @thiod \n'
        'примечание: в связи с очередью на печать я сделала бот, который поможет мне структурировать процесс и оптимизировать работу. бот умеет считать стоимость и позволит договориться о времени, когда файл будет передан в твои ручки. люблю, целую, Даша'
        'выбери тип печати:',
        reply_markup=reply_markup
    )
    return SELECTING_PRINT_TYPE

async def print_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    context.user_data['print_type'] = user_choice
    
    await update.message.reply_text(
        'супер!! сколько страниц нужно распечатать?:',
        reply_markup=ReplyKeyboardRemove()
    )
    return ENTERING_PAGES

async def calculate_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    try:
        num_pages = int(user_input)
        if num_pages <= 0:
            await update.message.reply_text('нужно ввести положительное число:()')
            return ENTERING_PAGES
        
        print_type = context.user_data.get('print_type')
        if print_type == 'односторонняя':
            total_cost = num_pages * PRICE_SINGLE
            cost_per_page = PRICE_SINGLE
        elif print_type == 'двусторонняя':
            total_cost = num_pages * PRICE_DOUBLE
            cost_per_page = PRICE_DOUBLE
        else:
            await update.message.reply_text('что-то пошло не так... давай попробуем сначала: /start.')
            return ConversationHandler.END
        # Формируем ответ
        message = (сформируйте месседж)


f"<b>Результат расчета:</b>\n"
            f"Тип печати: {print_ty
p
e}\n"
            f"Количество стра
н
иц: {num_pages}\n"
            f"Цена за страницу: {cost_
p
er_page} руб.\n"
            f"<b>Итоговая сто
и
мость: {total_cost} руб.</b>"
        )
        await update.message.reply_text(message, parse_mode='HTML')
        
    except ValueError:
        await
update.message.reply_text('Это не похоже на число. Введите количество страниц цифрами:')
        return ENTERING_PAGES
        
    return ConversationHandler.END

# --- Ком
а
нда /cancel для отмены диал
о
га ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Расчет отменен. Чтобы начать
зано
во
, отправьте /start.', reply_mar
k
up=ReplyKeyboardRemove())
return Conversation
H
andler.END

# --- Главная функция ---
def main():
    # Соз
д
аем приложение и передаем ему токен
    application = Application.builder().token(TOKEN).build()
    
    # Нас
тр
аиваем обработчик диалога (Conversation Handler)
c
onv_hand
le
r = ConversationHandler(
        entry_points=[CommandHandler('start', st
a
rt)],
        states={
            SELECTING_PRINT_TYPE: [
MessageHandler(filters.Regex('^(Односторонняя|Двусторонняя)$'), print_type_selected)
            ],
            ENTERING_PAGES: [
                MessageHandler(filters.TEXT & ~filters.C
OMM
AND, calculate_cost)
],
        },
        fallbacks=[CommandHandler('ca
n
cel', cancel)],
    )
    
    #
Добавляем обработчик в приложение
    application.add_handler(conv_handl
e
r)
    
    # Запускаем бота
print("Бот запущен...")
    applicat
i
on.run_polling()...