import logging

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ADD_DEADLINE, ADD_NAME = range(2)


def start(update: Update, context: CallbackContext) -> int:

    update.message.reply_text("Hi, use /add to add a new deadline!")

    return ADD_DEADLINE


def add_deadline(update: Update, context: CallbackContext) -> int:

    update.message.reply_text("Hi, what would you like to call your deadline?")

    return ADD_NAME


def add_name(update: Update, context: CallbackContext) -> int:
    # TODO

    return None


def done(update: Update, context: CallbackContext) -> int:

    user_data = context.user_data

    user_data.clear()
    update.message.reply_text("Thanks for using our bot! See you next time!")
    return ConversationHandler.END


def main() -> None:
    updater = Updater("1408983446:AAEjq7jNHRBGQ3CM4cf5pO6hWvPQMw_NRlY", use_context=True)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ADD_DEADLINE: [
                CommandHandler('add', add_deadline)
            ],
            # ADD_NAME: [
            #   MessageHandler(Filters.text, add_name)
            # ],
        },
        fallbacks=[CommandHandler('done', done)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
