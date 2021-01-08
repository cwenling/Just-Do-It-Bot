import logging

from telegram import Update, ReplyKeyboardMarkup
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

CHOICES_MENU, ADD_DEADLINE, ADD_NAME = range(3)

choices_menu_keyboard = [['/list tasks', '/add tasks'],
                         ['/edit tasks', '/delete tasks'],
                         ['/done tasks', '/exit']]
choices_menu_keyboard_markup = ReplyKeyboardMarkup(choices_menu_keyboard)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! Welcome to JustDueet bot!\n\n You can look at the keyboard for the list of "
                              "commands we offer! Alternatively, you can use /help!",
                              reply_markup=choices_menu_keyboard_markup)
    return CHOICES_MENU


# def choices_menu(update: Update, context: CallbackContext) -> int:
#
#
#
# def add_deadline(update: Update, context: CallbackContext) -> int:
#
#     update.message.reply_text("Hi, what would you like to call your deadline?")
#
#     return ADD_NAME

# def add_name(update: Update, context: CallbackContext) -> int:
#     # TODO
#
#     return None

def list_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Here are the list of tasks:")
    return CHOICES_MENU


def add_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("I am adding your tasks now!")
    return CHOICES_MENU


def edit_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("I am editing tasks now.")
    return CHOICES_MENU


def delete_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("I am deleting tasks now.")
    return CHOICES_MENU


def mark_done_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("I am marking done tasks now.")
    return CHOICES_MENU


def help_message(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Here are a list of commands you can use:\n"
                              "/list - View your tasks\n"
                              "/add - Add your tasks\n"
                              "/edit - Edit your tasks\n"
                              "/delete - Delete your tasks\n"
                              "/done - Mark done your tasks\n"
                              "/cancel - Say bye bye to me!")
    return CHOICES_MENU


def cancel(update: Update, context: CallbackContext) -> int:
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
            CHOICES_MENU: [
                CommandHandler('list', list_tasks),
                CommandHandler('add', add_tasks),
                CommandHandler('edit', edit_tasks),
                CommandHandler('delete', delete_tasks),
                CommandHandler('done', mark_done_tasks)
            ],
            # ADD_NAME: [
            #   MessageHandler(Filters.text, add_name)
            # ],
        },
        fallbacks=[CommandHandler('help', help_message), CommandHandler('exit', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
