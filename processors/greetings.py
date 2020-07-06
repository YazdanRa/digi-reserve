from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters


def say_hello(update: Update, context: CallbackContext):
    context.user_data.clear()

    chat_id = update.message.chat.id
    name = update.message.from_user.first_name

    context.bot.send_message(chat_id,
                             ('Hello {}!\n'.format(name) +
                              'Welcome to Digi-Reserve! you can use commands to navigate bot\n' +
                              'enjoy it :)\n'),
                             parse_mode='Markdown')


def home(update, context):
    context.user_data.clear()

    chat_id = update.message.chat.id
    name = update.message.from_user.first_name

    context.bot.send_message(chat_id, 'What can i do for you *{}*'.format(name),
                             parse_mode='Markdown')


HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler('start', say_hello),
        CommandHandler('home', home),
        MessageHandler(Filters.regex(r'(HOME)'), home),
    ],

    states={

    },

    fallbacks=[

    ],

    allow_reentry=True,
)
