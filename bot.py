import logging
import os

from telegram.ext import CallbackContext, Updater, MessageHandler, Filters

from models import *
from processors import greetings
from processors.is_available import is_available
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


def check_list(context: CallbackContext):
    for item in CheckList.select().where(CheckList.is_active == True):
        if is_available(item.url):
            user = item.user
            context.bot.send_message(user.chat_id,
                                     ('One item is available now!\n' +
                                      '*URL:*\n{}\n\n'.format(item.url)),
                                     parse_mode='Markdown')
            setup(item.url)


def main():
    # Start bot
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    bot = updater.dispatcher

    job = updater.job_queue
    job_minute = job.run_repeating(check_list, interval=60, first=0)

    ### BOT HANDLERS

    # DATA
    bot.add_handler(DATA, group=0)

    # GREETINGS
    bot.add_handler(greetings.HANDLER, group=5)

    # Start polling
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
