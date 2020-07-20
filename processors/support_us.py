from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

from .greetings import keyboard

inline_keyboard = [
    [
        InlineKeyboardButton(text='PayPal!', url='https://paypal.me/SepMas'),
    ],
    [
        InlineKeyboardButton(text='ZarinPal!', url='https://zarinp.al/yazdanra'),
    ],
]


def support(update: Update, context: CallbackContext):
    context.user_data.clear()
    chat_id = update.message.from_user.id

    markup = InlineKeyboardMarkup(inline_keyboard)

    context.bot.send_message(chat_id, ('First Thank you!\n' +
                                       'Have you any idea? Please share with us!\n' +
                                       'Plus can pay as much as you want for helping us! ^__-'),
                             reply_markup=markup)

    context.bot.send_message(chat_id, 'Choose one!', reply_markup=keyboard)

    return ConversationHandler.END


HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler('support', support),
        MessageHandler(Filters.text('SUPPORT US'), support),
    ],

    states={

    },

    fallbacks=[

    ],

    allow_reentry=True,
)
