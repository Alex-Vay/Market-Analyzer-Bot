import asyncio
import concurrent.futures
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from dotenv import load_dotenv
import os
from parsers.ozon import ozon_parser
from parsers.wb import wb_parser
from parsers.yandex import ya_parser
from parsers.mvideo import mvideo
from parsers.dns import dns_parser

# from parsers.aliexpress import ali_parser

# Загрузка переменных окружения из .env файла
load_dotenv()

# Access environment variables as if they came from the actual environment
TOKEN = os.getenv('TOKEN')

STORES = ['Ozon', 'Wildberries', 'Яндекс Маркет', 'Mvideo', 'DNS']  # 'AliExpress'
PARSERS = {'Ozon': ozon_parser.get_product,
           'Wildberries': wb_parser.get_product,
           'Яндекс Маркет': ya_parser.get_product,
           'Mvideo': mvideo.get_data_mvideo,
           'DNS': dns_parser.get_product,
           # 'AliExpress': ali_parser.get_product
           }


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Сохраняем ссылки на update и context
    global current_update, current_context
    current_update = update
    current_context = context
    welcome_message = (
        "Привет! 👋🎉 Я ваш личный бот, готовый помочь Вам с поиском и анализом товаров с маркетплейсов🛒.\n\n"
        " \tПорядок действий:\n"
        "Нажмите Найти Товар\n"
        "Выберите один или несколько маркетплейсов\n"
        "Введите название, модель, цену товара и нажмите Найти\n\n"
        "Как только запрос выполнится, бот отправит Вам уведомление о товаре!🚀"
    )
    keyboard = [
        [InlineKeyboardButton("Найти Товар", callback_data='choose_stores')],
        [InlineKeyboardButton("Информация о боте", callback_data='info')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=welcome_message, reply_markup=reply_markup)


# Функция для создания клавиатуры с магазинами
def create_store_keyboard(selected_stores):
    store_keyboard = []
    for i in range(len(STORES)):
        store_name = STORES[i]
        button_text = f"✅ {store_name}" if store_name in selected_stores else store_name
        store_keyboard.append([InlineKeyboardButton(button_text, callback_data=f'store{i}')])

    store_keyboard.append([InlineKeyboardButton("Завершить выбор", callback_data='finish_selection')])
    return InlineKeyboardMarkup(store_keyboard)


# Функция для обработки выбора магазинов
async def choose_stores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['selected_stores'] = set()
    store_reply_markup = create_store_keyboard(context.user_data['selected_stores'])
    await update.callback_query.edit_message_text(text="Вы на этапе выбора магазинов", reply_markup=store_reply_markup)


# Функция для обработки выбора магазина
async def select_store(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    store_name = STORES[int(query.data[-1])]
    selected_stores = context.user_data['selected_stores']
    # Добавляем или удаляем магазин из выбранных
    if store_name in selected_stores:
        selected_stores.remove(store_name)
    else:
        selected_stores.add(store_name)

    # Обновляем клавиатуру с изменёнными кнопками
    store_reply_markup = create_store_keyboard(selected_stores)
    await query.edit_message_text(text="Вы на этапе выбора магазинов", reply_markup=store_reply_markup)


# Функция для завершения выбора
async def finish_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_stores = context.user_data.get('selected_stores', list())

    if selected_stores:
        stores_list = ', '.join(selected_stores)
        await update.callback_query.edit_message_text(
            text=f"Вы выбрали следующие магазины: {stores_list}\n"
                 f"Пожалуйста, укажите товар в формате:\nТовар (тип, бренд, модель, цвет и др.)")
        # Устанавливаем состояние ожидания названия товара и сохраняем список магазинов
        context.user_data['awaiting_product_name'] = True
        context.user_data['stores_list'] = selected_stores
    else:
        await update.message.reply_text(text="Вы не выбрали ни одного магазина./start")


async def handle_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_product_name'):
        product_info = update.message.text
        stores_list = context.user_data.get('stores_list', '')
        stores_str = ', '.join(stores_list)
        product_text = f"<b>Товар</b>: {product_info}\n"
        keyboard = [
            [InlineKeyboardButton("Да, начать поиск!", callback_data='start_search')],
            [InlineKeyboardButton("Нет, указать информацию заново", callback_data='enter_again')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text=f"Вы указали следующую информацию о товаре:\n"
                                             f"{product_text}\n"
                                             f"<b>Магазины:</b> {stores_str}\n"
                                             f"<b>Вы уверены, что хотите начать поиск?</b>",
                                        reply_markup=reply_markup,
                                        parse_mode='html')
        # Сбрасываем состояние ожидания
        context.user_data['awaiting_product_name'] = False
        # сохраняем информацию о товаре
        context.user_data['product_info'] = product_info

    else:
        await update.message.reply_text("Пожалуйста, сначала выберите магазины.")


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    product_search = context.user_data.pop('product_info', '')
    stores_list = context.user_data.get('stores_list', [])
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        # Создаем задачи для каждого парсера
        future_to_store = {executor.submit(PARSERS.get(store),
                                           product_search): store
                           for store in stores_list}

        # Обрабатываем результаты по мере их завершения
        for future in concurrent.futures.as_completed(future_to_store):
            store = future_to_store[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'{store} generated an exception: {exc}')

        # Отправка результатов пользователю
        text = ""
        results = filter(lambda x: x is not None, results)
        for product in sorted(results, key=lambda x: int(x[1])):
            subtext = f'<a href="{product[3]}">{product[0]}</a>\n' \
                      f'<b>Цена (₽)</b>: {product[1]}\n' \
                      f'<b>Отзывы и рейтинг</b>: {product[2]}\n\n'

            text += subtext
        keyboard = [
            [InlineKeyboardButton("Вернуться в меню", callback_data='start')],
            [InlineKeyboardButton("Найти другой товар", callback_data='finish_selection')],
            [InlineKeyboardButton("Выбрать другой маркетплейс(ы) и товар", callback_data='enter_again')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text=text,
                                                      reply_markup=reply_markup,
                                                      parse_mode='html')


# Основная функция для обработки нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждение нажатия кнопки

    if query.data == 'choose_stores':
        await choose_stores(update, context)
    elif query.data.startswith('store'):
        await select_store(update, context)
    elif query.data == 'finish_selection':
        await finish_selection(update, context)
    elif query.data == 'info':
        await query.edit_message_text(text="Я бот, созданный для помощи пользователям!\nНажмите /start")
    elif query.data == 'start_search':
        await start_search(update, context)
    elif query.data == 'enter_again':
        await choose_stores(update, context)  # Перенаправляем на выбор магазинов
    elif query.data == 'start':
        await start(current_update, current_context)


def main() -> None:
    # Создаем приложение и регистрируем обработчики
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_product_name))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
