from telegram.ext import MessageHandler, Filters

from models import User, Message


def save_data(update, context):
    chat_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    is_bot = update.message.from_user.is_bot
    language_code = update.message.from_user.language_code
    text = update.message.text
    details = str(update)

    user = User.select().where(User.chat_id == chat_id)

    if not len(user):
        User.insert({
            User.first_name: first_name,
            User.last_name: last_name,
            User.username: username,
            User.chat_id: chat_id,
            User.is_bot: is_bot,
            User.language_code: language_code,
        }).execute()
    if len(user):
        User.update({
            User.first_name: first_name,
            User.last_name: last_name,
            User.username: username,
            User.chat_id: chat_id,
            User.is_bot: is_bot,
            User.language_code: language_code,
        }).where(User.chat_id == chat_id).execute()

    Message.insert({
        Message.chat_id: chat_id,
        Message.username: username,
        Message.text: text,
        Message.details: details,
    }).execute()


DATA = MessageHandler(Filters.all, save_data)
