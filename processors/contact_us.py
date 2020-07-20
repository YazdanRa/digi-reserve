from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

from .greetings import keyboard

inline_keyboard = [
    [
        InlineKeyboardButton(text='Yazdan', url='https://t.me/yazdan_ra'),
    ],
    [
        InlineKeyboardButton(text='Siamak', url='https://t.me/Bon_mook'),
    ],
]


def support(update: Update, context: CallbackContext):
    context.user_data.clear()
    chat_id = update.message.from_user.id

    markup = InlineKeyboardMarkup(inline_keyboard)

    context.bot.send_message(chat_id, ('First Thank you!\n' +
                                       'have you any idea? please share with us!\n' +
                                       'just click and contact us! ^__-'),
                             reply_markup=markup)

    context.bot.send_message(chat_id, 'Choose one!', reply_markup=keyboard)

    return ConversationHandler.END


HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler('contact', support),
        MessageHandler(Filters.text('CONTACT US'), support),
    ],

    states={

    },

    fallbacks=[

    ],

    allow_reentry=True,
)
