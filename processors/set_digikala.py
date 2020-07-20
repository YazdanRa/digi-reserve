from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

from models import User
from .greetings import keyboard

GET_USER, GET_PASS = range(2)


def start_set(update: Update, context: CallbackContext):
    context.user_data.clear()
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'Send your Digikala Username\nit could be an email or a phone number!',
                             reply_markup=ReplyKeyboardRemove())
    return GET_USER


def get_user(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    context.user_data['username'] = update.message.text
    context.bot.delete_message(chat_id, update.message.id)
    context.bot.send_message(chat_id, 'Send your Digikala Password\nfor sure your password will save on database!')
    return GET_PASS


def get_pass(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    username = context.user_data['username']
    password = update.message.text
    User.update(digikala_username=username, digikala_password=password).where(User.chat_id == chat_id).execute()
    context.bot.delete_message(chat_id, update.message.id)
    context.bot.send_message(chat_id, 'Your data successfully updated! =D',  reply_markup=keyboard)
    context.user_data.clear()
    return ConversationHandler.END


def error(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'Oops...\nSomething went wrong!\nTry again:')
    return


def cancel(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'The process has canceled!')
    context.user_data.clear()
    return ConversationHandler.END


HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler('set', start_set),
        MessageHandler(Filters.text('UPDATE DIGIKALA ACCOUNT'), start_set),
    ],

    states={

        GET_USER: [MessageHandler(Filters.text, get_user)],

        GET_PASS: [MessageHandler(Filters.text, get_pass)],

    },

    fallbacks=[
        MessageHandler(Filters.command, cancel),
        MessageHandler(Filters.all, error)
    ],

    allow_reentry=True,
)
