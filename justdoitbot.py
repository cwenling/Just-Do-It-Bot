import json
import logging
import psycopg2

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


def get_connection():
    connection = psycopg2.connect(user="postgres2",
                                  password="botbotbot",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="botdb")
    return connection


CHOICES_MENU, ADD_TASK_NAME, ADD_TASK_DEADLINE, CONTINUE_OR_NOT, CHOOSE_EDIT_FIELDS, \
    CHOOSE_DELETE_TASK, CONFIRM_DELETION, MARK_TASK_DONE = range(8)

choices_menu_keyboard = [['/list tasks', '/add tasks'],
                         ['/edit tasks', '/delete tasks'],
                         ['/done tasks', '/exit']]
choices_menu_keyboard_markup = ReplyKeyboardMarkup(choices_menu_keyboard)

task_field_menu_keyboard = [['task /name', 'task /deadline']]
task_field_menu_keyboard_markup = ReplyKeyboardMarkup(task_field_menu_keyboard)

confirmation_deletion_keyboard = [['/yes', '/no']]
confirmation_deletion_keyboard_markup = ReplyKeyboardMarkup(confirmation_deletion_keyboard)

continue_or_not_keyboard = [['/continue', '/end']]
continue_or_not_keyboard_markup = ReplyKeyboardMarkup(continue_or_not_keyboard)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! Welcome to JustDueet bot!\n\n You can look at the keyboard for the list of "
                              "commands we offer! Alternatively, you can use /help!",
                              reply_markup=choices_menu_keyboard_markup)
    context.user_data['userid'] = update.message.chat_id
    # Fetch result
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * from tasks")
    print("Result ", cursor.fetchall())
    return CHOICES_MENU


def list_tasks(update: Update, context: CallbackContext) -> int:
    tasks_to_be_printed = get_tasks_in_string(update)
    update.message.reply_text("Here are your tasks:\n" + tasks_to_be_printed)
    return CHOICES_MENU


def get_tasks_in_string(update: Update) -> str:
    connection = get_connection()
    cursor = connection.cursor()
    postgres_select_query = """select * from tasks where userid = %s"""

    user_id = str(update.message.from_user.id)
    cursor.execute(postgres_select_query, (user_id,))
    tasks = cursor.fetchall()

    result = ""
    i = 1
    for task in tasks:
        task_name = task[1]
        task_deadline = task[2]
        result += str(i) + ". " + "\"" + task_name + "\"" + ", due by: " + task_deadline + "\n"
        i += 1

    return result


def add_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Okay so you want to add a task!\n"
                              "What is the name of your task?")
    return ADD_TASK_NAME


def add_task_name(update: Update, context: CallbackContext) -> int:
    task_name = update.message.text
    update.message.reply_text("Noted! Your task name is " + task_name + "\n"
                                                                        "What about the deadline of the task?")
    context.user_data['name'] = task_name
    logger.info("Deadline name:")
    logger.info(context.user_data)
    # TODO insert task name into db

    return ADD_TASK_DEADLINE


def add_task_deadline(update: Update, context: CallbackContext) -> int:
    task_deadline = update.message.text
    context.user_data['deadline'] = task_deadline
    # TODO get task name from db
    logger.info("Task:")
    logger.info(context.user_data)
    task = context.user_data['name'] + task_deadline
    update.message.reply_text("Okay! Your task's deadline is " + task_deadline + "\n"
                              + "This task has been added into your task list: " + task)

    connection = get_connection()
    cursor = connection.cursor()

    postgres_insert_query = """ INSERT INTO tasks (USERID, NAME, DEADLINE) VALUES (%s,%s,%s)"""
    record_to_insert = (context.user_data['userid'], context.user_data['name'], context.user_data['deadline'])
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into mobile table")

    update.message.reply_text("Do you want to continue using JustDueet bot?",
                              reply_markup=continue_or_not_keyboard_markup)

    # Fetch result
    cursor.execute("SELECT * from tasks")
    print("Result ", cursor.fetchall())

    return CONTINUE_OR_NOT


def edit_tasks(update: Update, context: CallbackContext) -> int:
    tasks_to_be_printed = get_tasks_in_string(update)
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
    tasks_to_be_printed = get_tasks_in_string(update)
    # keyboard = build_keyboard(tasks)
    # TODO add keyboard of tasks here
    update.message.reply_text(
        "Here are the list of tasks:\n" + tasks_to_be_printed + "Which task do you want to delete?")
    return CHOOSE_DELETE_TASK


def delete_task_confirmation(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Are you sure you want to delete this task?",
                              reply_markup=confirmation_deletion_keyboard_markup)
    return CONFIRM_DELETION


def confirm_deletion(update: Update, context: CallbackContext) -> int:
    # TODO get the task
    update.message.reply_text("You deleted this task.", reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def abort_deletion(update: Update, context: CallbackContext) -> int:
    # TODO get the task
    update.message.reply_text("You did not delete this task.", reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def mark_done_tasks(update: Update, context: CallbackContext) -> int:
    tasks_to_be_printed = get_tasks_in_string(update)
    # keyboard = build_keyboard(tasks)
    # TODO add keyboard of tasks here
    update.message.reply_text(
        "Here are the list of tasks:\n" + tasks_to_be_printed + "Which task do you want to mark done?")
    return MARK_TASK_DONE


def confirm_done(update: Update, context: CallbackContext) -> int:
    # TODO get the task
    update.message.reply_text("This task has been marked done!")
    return CONTINUE_OR_NOT


def help_message(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Here are a list of commands you can use:\n"
                              "/list - View your tasks\n"
                              "/add - Add your tasks\n"
                              "/edit - Edit your tasks\n"
                              "/delete - Delete your tasks\n"
                              "/done - Mark done your tasks\n"
                              "/exit - Say bye bye to me!")
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
                CommandHandler('done', mark_done_tasks),
                CommandHandler('exit', cancel)
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
            CHOOSE_DELETE_TASK: [

            ],
            CONFIRM_DELETION: [
                CommandHandler('yes', confirm_deletion),
                CommandHandler('no', abort_deletion)
            ],
            MARK_TASK_DONE: [

            ],
            CONTINUE_OR_NOT: [
                CommandHandler('continue', continue_using),
                CommandHandler('end', cancel)
            ]

        },
        fallbacks=[CommandHandler('help', help_message), CommandHandler('exit', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
