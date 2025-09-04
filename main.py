import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

# Токен бота (берется из переменных окружения)
TOKEN = os.environ.get('TOKEN')

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
QUIZ_QUESTION = 0

# Данные для викторины (вопрос, варианты ответов, индекс правильного ответа)
quiz_data = [
    {"question": "В каком слове пропущена буква ЖИ?:\n1) пру..ина\n2) ланды..\n3) стри..", "correct": 0},
    {"question": "Выбери слово с разделительным мягким знаком (ь):\n1) вьюга\n2) пальто\n3) пьеса", "correct": 2},
    {"question": "Найди имя собственное:\n1) город\n2) река Волга\n3) ученик", "correct": 1}
]

# Словарь с правилами
rules = {
    "жи_ши": "Сочетания ЖИ-ШИ пиши с буквой И! Например: *жи*раф, *ши*на.",
    "ча_ща": "Сочетания ЧА-ЩА пиши с буквой А! Например: *ча*ша, *ща*вель.",
    "чу_щу": "Сочетания ЧУ-ЩУ пиши с буквой У! Например: *чу*до, *щу*ка.",
    "чк_чн": "Сочетания ЧК, ЧН пишутся без мягкого знака! Например: пе*чк*а, стра*чн*ый.",
    "ь_разделительный": "Разделительный мягкий знак (Ь) пишется в корне слова после согласных перед буквами Е, Ё, Ю, Я, И. Например: в*ь*юга, лист*ь*я, бел*ь*ё."
}

# Упражнения по учебнику Рамзаевой 3 класс
exercises = {
    "упр_1_часть1": 
        "**Упражнение 1 (Часть 1)**\nСпиши слова, вставляя пропущенные буквы:\n"
        "ж_вой, ш_на, ч_йка, щ_ка, ч_до, щ_пальцы\n\n"
        "*Сначала попробуй сделать самостоятельно, потом нажми 'Ответ 1 Часть1'*",
    
    "упр_2_часть1": 
        "**Упражнение 2 (Часть 1)**\nНайди и подчеркни имена собственные:\n"
        "город москва, река волга, ученик петя, собака жучка\n\n"
        "*Сначала попробуй сделать самостоятельно, потом нажми 'Ответ 2 Часть1'*",
    
    "упр_1_часть2": 
        "**Упражнение 1 (Часть 2)**\nВставь разделительный мягкий знак:\n"
        "в_юга, лист_я, бел_ё, об_явление\n\n"
        "*Сначала попробуй сделать самостоятельно, потом нажми 'Ответ 1 Часть2'*",
    
    "упр_2_часть2": 
        "**Упражнение 2 (Часть 2)**\nСоставь предложения со словами:\n"
        "пьеса, вьюга, пальто, пеньки\n\n"
        "*Сначала попробуй сделать самостоятельно, потом нажми 'Ответ 2 Часть2'*"
}

# Ответы на упражнения
answers = {
    "ответ_1_часть1": 
        "**Ответ к упр. 1 (Часть 1):**\n"
        "живой, шина, чайка, щука, чудо, щупальцы\n\n"
        "**Правило:** ЖИ-ШИ пиши с И, ЧА-ЩА пиши с А, ЧУ-ЩУ пиши с У",
    
    "ответ_2_часть1": 
        "**Ответ к упр. 2 (Часть 1):**\n"
        "город *Москва*, река *Волга*, ученик *Петя*, собака *Жучка*\n\n"
        "**Правило:** Имена собственные пишутся с большой буквы",
    
    "ответ_1_часть2": 
        "**Ответ к упр. 1 (Часть 2):**\n"
        "в*ь*юга, лист*ь*я, бел*ь*ё, объявление\n\n"
        "**Правило:** Разделительный Ь пишется после согласных перед Е, Ё, Ю, Я, И",
    
    "ответ_2_часть2": 
        "**Ответ к упр. 2 (Часть 2):**\n"
        "1. Мы смотрели интересную *пьесу* в театре.\n"
        "2. Сильная *вьюга* замела все дороги.\n" 
        "3. Тёплое *пальто* висело в шкафу.\n"
        "4. В лесу мы нашли старые *пеньки*."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение и показывает меню"""
    keyboard = [['📚 Правила', '🎯 Викторина', '📖 Упражнения']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Привет, {user_name}! Я бот-помощник по русскому языку для 3 класса.\n"
        "Я могу:\n• 📚 Показать правила\n• 🎯 Провести викторину\n• 📖 Дать упражнения\n"
        "Выбери, что хочешь сделать:",
        reply_markup=reply_markup
    )

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню"""
    keyboard = [['📚 Правила', '🎯 Викторина', '📖 Упражнения']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)

async def show_rules_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню правил"""
    keyboard = [[rule] for rule in rules.keys()] + [['↩️ Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выбери правило:", reply_markup=reply_markup)

async def send_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет правило"""
    user_choice = update.message.text
    if user_choice in rules:
        await update.message.reply_text(rules[user_choice], parse_mode='Markdown')
    else:
        await update.message.reply_text("Пока такого правила нет в списке.")

async def show_exercises_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню упражнений"""
    keyboard = [
        ['Упр 1 Часть1', 'Упр 2 Часть1'],
        ['Упр 1 Часть2', 'Упр 2 Часть2'],
        ['Ответ 1 Часть1', 'Ответ 2 Часть1'],
        ['Ответ 1 Часть2', 'Ответ 2 Часть2'],
        ['↩️ Назад']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выбери упражнение или ответ:", reply_markup=reply_markup)

async def send_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет упражнение"""
    exercise_map = {
        'Упр 1 Часть1': 'упр_1_часть1',
        'Упр 2 Часть1': 'упр_2_часть1',
        'Упр 1 Часть2': 'упр_1_часть2',
        'Упр 2 Часть2': 'упр_2_часть2'
    }
    
    user_choice = update.message.text
    if user_choice in exercise_map:
        await update.message.reply_text(exercises[exercise_map[user_choice]], parse_mode='Markdown')
    else:
        await update.message.reply_text("Упражнение не найдено.")

async def send_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ответ на упражнение"""
    answer_map = {
        'Ответ 1 Часть1': 'ответ_1_часть1',
        'Ответ 2 Часть1': 'ответ_2_часть1', 
        'Ответ 1 Часть2': 'ответ_1_часть2',
        'Ответ 2 Часть2': 'ответ_2_часть2'
    }
    
    user_choice = update.message.text
    if user_choice in answer_map:
        await update.message.reply_text(answers[answer_map[user_choice]], parse_mode='Markdown')
    else:
        await update.message.reply_text("Ответ не найден.")

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает викторину"""
    context.user_data['quiz_score'] = 0
    context.user_data['current_question'] = 0
    keyboard = [['1', '2', '3'], ['❌ Выйти из викторины']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    first_question = quiz_data[0]["question"]
    await update.message.reply_text(
        f"Викторина начинается! Отвечай, выбирая цифру ответа.\n\n{first_question}",
        reply_markup=reply_markup
    )
    return QUIZ_QUESTION

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ в викторине"""
    user_answer = update.message.text
    current_index = context.user_data['current_question']

    if user_answer == '❌ Выйти из викторины':
        await end_quiz(update, context)
        return ConversationHandler.END

    try:
        chosen_answer = int(user_answer) - 1
        correct_index = quiz_data[current_index]["correct"]

        if chosen_answer == correct_index:
            context.user_data['quiz_score'] += 1
            message = "✅ Верно!"
        else:
            message = f"❌ Неверно. Правильный ответ: {correct_index + 1}"

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
    """Завершает викторину"""
    score = context.user_data['quiz_score']
    total = len(quiz_data)
    await update.message.reply_text(
        f"Викторина окончена!\nТвой результат: {score} из {total}.",
        reply_markup=ReplyKeyboardRemove()
    )
    await show_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет операцию"""
    await update.message.reply_text("Возвращаемся в главное меню.", reply_markup=ReplyKeyboardRemove())
    await show_menu(update, context)
    return ConversationHandler.END

def main():
    """Запускает бота"""
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.Regex('^📚 Правила$'), show_rules_menu))
    application.add_handler(MessageHandler(filters.Regex('^(жи_ши|ча_ща|чу_щу|чк_чн|ь_разделительный)$'), send_rule))
    application.add_handler(MessageHandler(filters.Regex('^📖 Упражнения$'), show_exercises_menu))
    application.add_handler(MessageHandler(filters.Regex('^(Упр 1 Часть1|Упр 2 Часть1|Упр 1 Часть2|Упр 2 Часть2)$'), send_exercise))
    application.add_handler(MessageHandler(filters.Regex('^(Ответ 1 Часть1|Ответ 2 Часть1|Ответ 1 Часть2|Ответ 2 Часть2)$'), send_answer))
    application.add_handler(MessageHandler(filters.Regex('^↩️ Назад$'), show_menu))

    # Викторина
    quiz_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🎯 Викторина$'), start_quiz)],
        states={
            QUIZ_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(quiz_conv)

    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
    # ==================================================
# ВНИМАНИЕ: ЭТОТ КОД ЗАЩИЩЕН ОТ ИЗМЕНЕНИЙ
# 
# Чтобы предложить улучшения:
# 1. Создайте новую ветку (fork)
# 2. Внесите изменения
# 3. Создайте pull request
# 4. Ждите одобрения автора
#
# Несанкционированные изменения запрещены!
# ==================================================
