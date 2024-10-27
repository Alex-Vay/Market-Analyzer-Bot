from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# Import the necessary module
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Access environment variables as if they came from the actual environment
TOKEN = os.getenv('TOKEN')

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "Привет! 👋🎉 Я ваш личный бот, готовый помочь Вам с поиском и анализом товаров с маркетплейсов🛒.\n\n"
        " \tПорядок действий:\n"
        "Нажмите Найти Товар\n"
        "Выберите один или несколько маркетплейсов\n"
        "Введите название, модель, цену товара и нажмите Найти\n\n"
        "Как только запрос выполнится, бот отправит Вам уведомление о товаре!🚀"
    )
    # Создание кнопок
    keyboard = [
        [InlineKeyboardButton("Найти Товар", callback_data='search')],
        [
            InlineKeyboardButton("Помощь", callback_data='help'),
            InlineKeyboardButton("Информация о боте", callback_data='info')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


def main():
    """Запуск бота"""
    # Создание приложения и передача ему токен.

    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчика команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
