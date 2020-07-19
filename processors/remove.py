from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

from models import User, CheckList
from .greetings import keyboard

GET_TITLE = range(1)


def start_remove(update: Update, context: CallbackContext):
    context.user_data.clear()
    chat_id = update.message.from_user.id
    user = User.select().where(User.chat_id == chat_id)[0]
    items = CheckList.select().where((CheckList.user == user) & (CheckList.is_active == True))
    if not len(items):
        context.bot.send_message(chat_id, 'There is nothing to remove!')
        return ConversationHandler.END
    titles = ReplyKeyboardMarkup([[item.title] for item in items], resize_keyboard=True)
    context.bot.send_message(chat_id, 'Choose *title* of your target:', reply_markup=titles, parse_mode='Markdown')
    return GET_TITLE


def get_title(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    title = update.message.text
    # TODO: if not exists ask again!
    user = User.select().where(User.chat_id == chat_id)[0]
    CheckList.delete().where((CheckList.user == user) & (CheckList.title == title)).execute()
    context.bot.send_message(chat_id, 'Successfully Removed!', reply_markup=keyboard)
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
        CommandHandler('remove', start_remove),
        MessageHandler(Filters.regex(r'(REMOVE)'), start_remove),
    ],

    states={

        GET_TITLE: [MessageHandler(Filters.text, get_title)],

    },

    fallbacks=[
        MessageHandler(Filters.command, cancel),
        MessageHandler(Filters.all, error)
    ],

    allow_reentry=True,
)
