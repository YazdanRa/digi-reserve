import datetime
import re

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

from config import DEVELOPER_CHAT_ID
from models import User, CheckList
from .check import ok
from .greetings import keyboard

GET_TITLE, GET_URL, GET_PRICE_LIMIT, GET_TIME_LIMIT = range(4)


def start_add(update: Update, context: CallbackContext):
    context.user_data.clear()
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'Enter *title* of your target:', reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    return GET_TITLE


def get_title(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    title = update.message.text
    user = User.select().where(User.chat_id == chat_id)[0]
    if len(CheckList.select().where((CheckList.user == user) & (CheckList.title == title))):
        context.bot.send_message(chat_id, 'You already added this title to your list!\nplease enter another title:')
        return
    context.user_data['title'] = title
    context.bot.send_message(chat_id, 'Enter *link* of your target:', parse_mode='Markdown')
    return GET_URL


def get_url(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    url = update.message.text
    url = re.search('(https?://(www.)?digikala.com/product/dkp-\d+/)(.*)?', url).group(1)
    try:
        if ok(url):
            context.user_data['url'] = url
            context.bot.send_message(chat_id, 'How many *days* do you want we check this link?! (0 = ∞)', parse_mode='Markdown')
            return GET_TIME_LIMIT
        else:
            context.bot.send_message(chat_id, 'Oops! sth went wrong...\nEnter a *valid link* again:', parse_mode='Markdown')
            return
    except:
        context.bot.send_message(chat_id, 'Oops! sth went wrong...\nEnter a *valid link* again:', parse_mode='Markdown')
        return


def get_time_limit(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    duration = int(update.message.text)
    context.user_data['time_limit'] = datetime.datetime.now() + datetime.timedelta(days=duration)
    context.bot.send_message(chat_id, 'Enter the *maximum price* do you want: (toman & 0 = ∞)', parse_mode='Markdown')
    return GET_PRICE_LIMIT


def get_price_limit(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    user = User.select().where(chat_id == chat_id)
    try:
        CheckList.create(
            user=user,
            title=context.user_data['title'],
            url=context.user_data['url'],
            check_until=context.user_data['time_limit'],
            maximum_price=update.message.text
        )
        context.bot.send_message(chat_id, 'Mission completed =D', reply_markup=keyboard, parse_mode='Markdown')
    except ValueError as err:
        context.bot.send_message(DEVELOPER_CHAT_ID,
                                 ('ERROR from user *{user}* :\n' +
                                  '`{err}`').format(user=chat_id, err=err),
                                 parse_mode='Markdown')
        context.bot.send_message(chat_id,
                                 'sorry we have some issue!\nwe trying to fix it ASAP!\nget in touch @Yazdan\\_ra',
                                 parse_mode='Markdown')

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
        CommandHandler('add', start_add),
        MessageHandler(Filters.regex(r'(ADD)'), start_add),
    ],

    states={

        GET_TITLE: [MessageHandler(Filters.text, get_title)],

        GET_URL: [MessageHandler(Filters.regex(r'^(https?://(www.)?digikala.com/product/dkp-\d+/)(.*)?$'), get_url)],

        GET_TIME_LIMIT: [MessageHandler(Filters.regex(r'^[0-9]+$'), get_time_limit)],

        GET_PRICE_LIMIT: [MessageHandler(Filters.regex(r'^[0-9]+$'), get_price_limit)],

    },

    fallbacks=[
        MessageHandler(Filters.command, cancel),
        MessageHandler(Filters.all, error)
    ],

    allow_reentry=True,
)
