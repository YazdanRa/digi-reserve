import logging
import os

from telegram.ext import CallbackContext, Updater, DispatcherHandlerStop, MessageHandler, Filters

from config import ADMINS_CHAT_ID
from models import *
from processors import greetings, add, remove, set_digikala, contact_us, support_us
from processors.check import is_available, price
from processors.reserve import setup
from processors.save_data import DATA

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def load_environment():
    from dotenv import load_dotenv
    load_dotenv()

    # OR, the same with increased verbosity:
    load_dotenv(verbose=True)

    # OR, explicitly providing path to '.env'
    from pathlib import Path  # python3 only
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)


load_environment()

database.init(os.getenv("DATABASE"))
database.connect()
database.create_tables([
    User,
    Message,
    CheckList,
])


def limit(update, context):
    user_id = update.message.from_user.id

    if user_id not in ADMINS_CHAT_ID:
        context.bot.send_message(user_id, 'You are not a member! :)\n@Yazdan_ra')
        raise DispatcherHandlerStop


UPDATE_PROCESS_HANDLER = MessageHandler(Filters.all, limit)


def check_list(context: CallbackContext):
    for item in CheckList.select().where(CheckList.is_active == True):
        user = User.select().where(User.id == item.user.id)[0]
        if item.check_until > datetime.now() and item.check_until != 0:
            CheckList.update(is_active=False).where(id == item.id).execute()
            context.bot.send_message(user.chat_id, '{title}\'s time finished!'.format(title=item.title))
            continue
        if is_available(item.url):
            fee = price(item.url)
            if fee <= item.maximum_price or item.maximum_price == 0:
                context.bot.send_message(user.chat_id,
                                         ('*{}* available now!\n'.format(item.title) +
                                          '*Price:*\n{}\n\n'.format(fee) +
                                          '{}'.format(item.url)),
                                         parse_mode='Markdown')
                if setup(item.url, user.digikala_username, user.digikala_password):
                    context.bot.send_message(user.chat_id, '{title} has reserved!'.format(title=item.title))
                    CheckList.update(is_active=False).where(CheckList.id == item.id).execute()
                else:
                    context.bot.send_message(user.chat_id, 'failed!')
            else:
                context.bot.send_message(user.chat_id,
                                         '{} is now available!\nPrice: {}\nUrl: {}'.format(item.title, fee, item.url)
                                         )


def main():
    # Start bot
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    bot = updater.dispatcher

    job = updater.job_queue
    job_minute = job.run_repeating(check_list, interval=60, first=0)

    ### BOT HANDLERS

    # DATA
    bot.add_handler(DATA, group=0)
    bot.add_handler(UPDATE_PROCESS_HANDLER, group=0)

    # GENERAL
    bot.add_handler(greetings.HANDLER, group=1)
    bot.add_handler(contact_us.HANDLER, group=1)
    bot.add_handler(support_us.HANDLER, group=1)

    # Operations
    bot.add_handler(add.HANDLER, group=2)
    bot.add_handler(remove.HANDLER, group=3)
    bot.add_handler(set_digikala.HANDLER, group=4)

    # Start polling
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
