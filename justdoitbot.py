import json
import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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

CHOICES_MENU, ADD_TASK_NAME, ADD_TASK_DEADLINE, CONTINUE_OR_NOT, CHOOSE_EDIT_FIELDS = range(5)

choices_menu_keyboard = [['/list tasks', '/add tasks'],
                         ['/edit tasks', '/delete tasks'],
                         ['/done tasks', '/exit']]
choices_menu_keyboard_markup = ReplyKeyboardMarkup(choices_menu_keyboard)

task_field_menu_keyboard = ['task /name', 'task /deadline']
task_field_menu_keyboard_markup = ReplyKeyboardMarkup(task_field_menu_keyboard)

continue_or_not_keyboard = [['/yes', '/no']]
continue_or_not_keyboard_markup = ReplyKeyboardMarkup(continue_or_not_keyboard)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! Welcome to JustDueet bot!\n\n You can look at the keyboard for the list of "
                              "commands we offer! Alternatively, you can use /help!",
                              reply_markup=choices_menu_keyboard_markup)
    return CHOICES_MENU


def list_tasks(update: Update, context: CallbackContext) -> int:
    tasks_to_be_printed = get_tasks_in_string()
    update.message.reply_text("Here are the list of tasks:\n" + tasks_to_be_printed)
    return CHOICES_MENU


def get_tasks_in_string() -> str:
    # TODO getting tasks from db
    # tasks =
    tasks_to_be_printed = ""
    # for task in tasks:
    #     tasks_to_be_printed += task + "\n"
    return tasks_to_be_printed


def add_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Okay so you want to add a task!\n"
                              "What is the name of your task?")
    return ADD_TASK_NAME


def add_task_name(update: Update, context: CallbackContext) -> int:
    task_name = update.message.text
    update.message.reply_text("Noted! Your task name is " + task_name + "\n"
                              "What about the deadline of the task?")
    # TODO insert task name into db

    return ADD_TASK_DEADLINE


def add_task_deadline(update: Update, context: CallbackContext) -> int:
    task_deadline = update.message.text
    # TODO get task name from db
    task = "FULL TASK"
    update.message.reply_text("Okay! Your task's deadline is " + task_deadline + "\n"
                              + "This task has been added into your task list: " + task)
    update.message.reply_text("Do you want to continue using JustDueet bot?",
                              reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def edit_tasks(update: Update, context: CallbackContext) -> int:
    tasks_to_be_printed = get_tasks_in_string()
    # keyboard = build_keyboard(tasks)
    # TODO add keyboard of tasks here
    update.message.reply_text("Here are the list of tasks:\n" + tasks_to_be_printed + "Which task do you want to edit?")
    return CHOOSE_EDIT_FIELDS


def choose_edit_fields(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What would you like to edit? The task name or the task deadline?",
                              task_field_menu_keyboard_markup)
    return CHOOSE_EDIT_FIELDS


def edit_task_name(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What is the edited task name?", reply_markup=ReplyKeyboardRemove())
    edited_name = update.message.text
    # TODO update edited name in db
    return CONTINUE_OR_NOT


def edit_task_deadline(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What is the edited task deadline?", reply_markup=ReplyKeyboardRemove())
    edited_deadline = update.message.text
    # TODO update edited deadline in db
    return CONTINUE_OR_NOT


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


def continue_using(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("You are going to continue using this bot.", reply_markup=choices_menu_keyboard_markup)
    return CHOICES_MENU


def cancel(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text("Thanks for using our bot! See you next time!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


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
            ADD_TASK_NAME: [
                MessageHandler(Filters.text, add_task_name)
            ],
            ADD_TASK_DEADLINE: [
                MessageHandler(Filters.text, add_task_deadline)
            ],
            CHOOSE_EDIT_FIELDS: [
                CommandHandler('name', edit_task_name),
                CommandHandler('deadline', edit_task_deadline)
            ],
            CONTINUE_OR_NOT: [
                CommandHandler('yes', continue_using),
                CommandHandler('no', cancel)
            ]

        },
        fallbacks=[CommandHandler('help', help_message), CommandHandler('exit', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
