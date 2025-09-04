import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

# Вставьте сюда токен, который вы получили от @BotFather
TOKEN = "8407138634:AAHF7EcnFxNK5CHfq3o7GXNU0A8eRzb3c7o"

# Включаем логирование для отслеживания ошибок
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler (для викторины)
QUIZ_QUESTION = 0

# Данные для викторины (вопрос, варианты ответов, индекс правильного ответа)
quiz_data = [
    {"question": "В каком слове пропущена буква ЖИ?:\n1) пру..ина\n2) ланды..\n3) стри..", "correct": 1},
    {"question": "Выбери слово с разделительным мягким знаком (ь):\n1) вьюга\n2) пальто\n3) пьеса", "correct": 1},
    {"question": "Найди имя собственное:\n1) город\n2) река Волга\n3) ученик", "correct": 2}
]

# Словарь с правилами (можно расширять)
rules = {
    "жи_ши": "Сочетания ЖИ-ШИ пиши с буквой И! Например: *жи*раф, *ши*на.",
    "ча_ща": "Сочетания ЧА-ЩА пиши с буквой А! Например: *ча*ша, *ща*вель.",
    "чу_щу": "Сочетания ЧУ-ЩУ пиши с буквой У! Например: *чу*до, *щу*ка.",
    "чк_чн": "Сочетания ЧК, ЧН пишутся без мягкого знака! Например: пе*чк*а, стра*чн*ый.",
    "ь_разделительный": "Разделительный мягкий знак (Ь) пишется в корне слова после согласных перед буквами Е, Ё, Ю, Я, И. Например: в*ь*юга, лист*ь*я, бел*ь*ё."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение и показывает меню при команде /start"""
    keyboard = [['📚 Правила', '🎯 Викторина']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder='Выбери действие...')
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Привет, {user_name}! Я бот-помощник по русскому языку для 3 класса.\n"
        "Я могу:\n"
        "• 📚 Показать важные правила\n"
        "• 🎯 Провести небольшую викторину\n"
        "Выбери, что хочешь сделать:",
        reply_markup=reply_markup
    )

async def show_rules_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню с доступными правилами"""
    keyboard = [[rule] for rule in rules.keys()] + [['↩️ Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выбери правило, которое хочешь повторить:", reply_markup=reply_markup)

async def send_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет конкретное правило"""
    user_choice = update.message.text
    if user_choice in rules:
        # Отправляем правило с форматированием (parse_mode='Markdown')
        await update.message.reply_text(rules[user_choice], parse_mode='Markdown')
    else:
        await update.message.reply_text("Пока такого правила нет в списке.")

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает викторину"""
    context.user_data['quiz_score'] = 0
    context.user_data['current_question'] = 0
    keyboard = [['1', '2', '3'], ['❌ Выйти из викторины']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Задаем первый вопрос
    first_question = quiz_data[0]["question"]
    await update.message.reply_text(
        f"Викторина начинается! Отвечай, выбирая цифру ответа.\n\n{first_question}",
        reply_markup=reply_markup
    )
    return QUIZ_QUESTION

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ пользователя в викторине"""
    user_answer = update.message.text
    current_index = context.user_data['current_question']

    if user_answer == '❌ Выйти из викторины':
        await end_quiz(update, context)
        return ConversationHandler.END

    try:
        chosen_answer = int(user_answer) - 1  # Приводим к индексу (0, 1, 2)
        correct_index = quiz_data[current_index]["correct"]

        if chosen_answer == correct_index:
            context.user_data['quiz_score'] += 1
            message = "✅ Верно!"
        else:
            message = f"❌ Неверно. Правильный ответ: {correct_index + 1}"

        # Задаем следующий вопрос или завершаем
        context.user_data['current_question'] += 1
        next_index = context.user_data['current_question']

        if next_index < len(quiz_data):
            next_question = quiz_data[next_index]["question"]
            await update.message.reply_text(f"{message}\n\nСледующий вопрос:\n{next_question}")
            return QUIZ_QUESTION
        else:
            await end_quiz(update, context)
            return ConversationHandler.END

    except (ValueError, IndexError):
        await update.message.reply_text("Пожалуйста, выбери ответ 1, 2 или 3.")

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершает викторину и показывает результат"""
    score = context.user_data['quiz_score']
    total = len(quiz_data)
    keyboard = [['📚 Правила', '🎯 Викторина']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Викторина окончена!\nТвой результат: {score} из {total}.",
        reply_markup=reply_markup
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет любое состояние и возвращает в главное меню"""
    await update.message.reply_text("Возвращаемся в главное меню.", reply_markup=ReplyKeyboardRemove())
    await start(update, context)
    return ConversationHandler.END

def main():
    """Основная функция, запускающая бота"""
    # Создаем Application и передаем ему токен бота
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))

    # Обработчик для кнопки "Правила"
    application.add_handler(MessageHandler(filters.Regex('^📚 Правила$'), show_rules_menu))
    # Обработчик для отправки самого правила
    application.add_handler(MessageHandler(filters.Regex('^(жи_ши|ча_ща|чу_щу|чк_чн|ь_разделительный)$'), send_rule))

    # Обработчик для кнопки "Назад"
    application.add_handler(MessageHandler(filters.Regex('^↩️ Назад$'), start))

    # ConversationHandler для викторины
    quiz_conversation = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🎯 Викторина$'), start_quiz)],
        states={
            QUIZ_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.Regex('^❌ Выйти из викторины$'), cancel)]
    )
    application.add_handler(quiz_conversation)

    # Запускаем бота в режиме опроса (polling)
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()"# ��� ࠡ�⠥� ��ࠢ��" 
