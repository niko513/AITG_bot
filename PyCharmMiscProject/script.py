import telebot
from g4f.client import Client
from telebot import types

API_TOKEN = '7790950479:AAFhCtg0dbDhTEYEnwpGeSHvOd-xVZl8tmo'
bot = telebot.TeleBot(API_TOKEN)

client = Client()

conversation_history = {}


def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Старт"),
        types.KeyboardButton("Очистить историю"),
        types.KeyboardButton("Статистика чата"),
        types.KeyboardButton("Помощь")
    )
    return markup


@bot.message_handler(commands=['start'])
def process_start_command(message):
    bot.reply_to(message, "Привет! Я бот с поддержкой GPT-4. Задай мне любой вопрос.", reply_markup=create_main_menu())


@bot.message_handler(commands=['help'])
def process_help_command(message):
    help_text = (
        "/start - Начать новый диалог.\n"
        "/clear - Очистить историю диалога.\n"
        "/stata - Показать статистику чата.\n"
        "Текстовые сообщения, длина которых превышает 500 символов, не будут обработаны. "
        "Просто отправь текст, и я постараюсь помочь!"
    )
    bot.reply_to(message, help_text, reply_markup=create_main_menu())


@bot.message_handler(commands=['clear'])
def process_clear_command(message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    bot.reply_to(message, "История диалога очищена.", reply_markup=create_main_menu())


@bot.message_handler(commands=['stata'])
def process_stata_command(message):
    user_id = message.from_user.id
    num_messages = len(conversation_history.get(user_id, []))
    bot.reply_to(message, f"Количество сообщений в чате: {num_messages}", reply_markup=create_main_menu())


@bot.message_handler(content_types=['text'])
def send_gpt_response(message):
    user_id = message.from_user.id
    user_input = message.text

    # Проверка на превышение длины сообщения
    if len(user_input) > 500:
        bot.reply_to(message, "Текст более 500 символов", reply_markup=create_main_menu())
        return

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history[user_id],
        )
        chat_gpt_response = response.choices[0].message.content  # Исправлено здесь

        # Добавляем ответ бота в историю
        conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})

        # Отправляем ответ пользователю
        bot.reply_to(message, chat_gpt_response, reply_markup=create_main_menu())
    except Exception as e:
        print(f"Error while processing GPT request: {e}")
        bot.reply_to(message, "Извините, произошла ошибка. Попробуйте снова.", reply_markup=create_main_menu())

    # Запуск бота


if __name__ == "__main__":
    bot.polling(none_stop=True)
