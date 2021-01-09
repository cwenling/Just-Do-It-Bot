import logging
import psycopg2
import os

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

PORT = int(os.environ.get('PORT', 5000))
TOKEN = "1408983446:AAEjq7jNHRBGQ3CM4cf5pO6hWvPQMw_NRlY"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_connection():
    connection = psycopg2.connect(user="nuryqcnukhhtay",
                                  password="f898e8d7ad3c53f29763b0758498d07923068b506522eb80096577ca0f53d2c4",
                                  host="ec2-52-44-166-58.compute-1.amazonaws.com",
                                  port="5432",
                                  database="d3t932c9q69007")
    return connection


CHOICES_MENU, ADD_TASK_NAME, ADD_TASK_DEADLINE, CONTINUE_OR_NOT, CHOOSE_EDIT_FIELDS, \
    CHOOSE_EDIT_TASK, EDIT_TASK_NAME, EDIT_TASK_DEADLINE, CHOOSE_DELETE_TASK, CONFIRM_DELETION = range(10)

choices_menu_keyboard = [['/list tasks', '/add tasks'],
                         ['/edit tasks', '/delete tasks'],
                         ['/exit']]
choices_menu_keyboard_markup = ReplyKeyboardMarkup(choices_menu_keyboard)

task_field_menu_keyboard = [['/name', '/deadline']]
task_field_menu_keyboard_markup = ReplyKeyboardMarkup(task_field_menu_keyboard)

confirmation_deletion_keyboard = [['/yes', '/no']]
confirmation_deletion_keyboard_markup = ReplyKeyboardMarkup(confirmation_deletion_keyboard)

continue_or_not_keyboard = [['/continue', '/end']]
continue_or_not_keyboard_markup = ReplyKeyboardMarkup(continue_or_not_keyboard)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! Welcome to JustDueet bot!\n\n You can look at the keyboard for the list of "
                              "commands we offer! Alternatively, you can use /help!",
                              reply_markup=choices_menu_keyboard_markup)
    context.user_data['userid'] = str(update.message.from_user.id)
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


def get_tasks_all(update: Update):
    connection = get_connection()
    cursor = connection.cursor()
    postgres_select_query = """select * from tasks where userid = %s"""

    user_id = str(update.message.from_user.id)
    cursor.execute(postgres_select_query, (user_id,))
    tasks = cursor.fetchall()

    return tasks


def get_tasks_name(update: Update):
    connection = get_connection()
    cursor = connection.cursor()
    postgres_select_query = """select name from tasks where userid = %s"""

    user_id = str(update.message.from_user.id)
    cursor.execute(postgres_select_query, (user_id,))
    tasks_names = cursor.fetchall()

    return tasks_names


def get_tasks_name_deadline(update: Update):
    connection = get_connection()
    cursor = connection.cursor()
    postgres_select_query = """select name, deadline from tasks where userid = %s"""

    user_id = str(update.message.from_user.id)
    cursor.execute(postgres_select_query, (user_id,))
    tasks_names_deadlines = cursor.fetchall()

    return tasks_names_deadlines


def get_tasks_in_string(update: Update) -> str:
    tasks = get_tasks_all(update)
    result = ""
    i = 1

    for task in tasks:
        task_name = task[1]
        task_deadline = task[2]
        result += str(i) + ". " + task_name + " - " + task_deadline + "\n"
        i += 1

    return result


def add_tasks(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What is the name of the task?")
    return ADD_TASK_NAME


def add_task_name(update: Update, context: CallbackContext) -> int:
    task_name = update.message.text
    update.message.reply_text("When is it due?")
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
    logger.info("Task was inserted successfully into database")

    update.message.reply_text("Do you want to continue using JustDueet bot?",
                              reply_markup=continue_or_not_keyboard_markup)

    # Fetch result
    cursor.execute("SELECT * from tasks")
    print("Result ", cursor.fetchall())

    return CONTINUE_OR_NOT


def edit_tasks(update: Update, context: CallbackContext) -> int:

    tasks = get_tasks_name_deadline(update)
    my_tasks = []
    for task in tasks:
        my_tasks.append(task[0] + " - " + task[1])
    keyboard = [[task] for task in my_tasks]
    reply_markup_edit = {"keyboard": keyboard, "one_time_keyboard": True}
    update.message.reply_text("Which task to edit?", reply_markup=reply_markup_edit)

    return CHOOSE_EDIT_TASK


task_to_be_edited = ""


def edit_task_confirmation(update: Update, context: CallbackContext) -> int:
    full_task = update.message.text
    is_inside = False
    for task in get_tasks_name_deadline(update):
        if full_task.split(' - ')[0] == task[0]:
            is_inside = True
            global task_to_be_edited
            task_to_be_edited = full_task
            break

    if not is_inside:
        update.message.reply_text("Task does not exist!")
        return abort_editing(update, context)
    else:
        return choose_edit_fields(update, context)


def choose_edit_fields(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What would you like to edit? The task name or the task deadline?",
                              reply_markup=task_field_menu_keyboard_markup)
    return CHOOSE_EDIT_FIELDS


def ask_edited_name(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What is the edited task name?", reply_markup=ReplyKeyboardRemove())
    return EDIT_TASK_NAME


def ask_edited_deadline(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What is the edited task deadline?", reply_markup=ReplyKeyboardRemove())
    return EDIT_TASK_DEADLINE


def edit_task_name(update: Update, context: CallbackContext) -> int:
    edited_task_name = update.message.text
    checker = task_to_be_edited.split(' - ')[0]

    connection = get_connection()
    cursor = connection.cursor()
    sql_update_query = """Update tasks set name = %s where name = %s"""
    cursor.execute(sql_update_query, (edited_task_name, checker),)
    connection.commit()
    count = cursor.rowcount
    print(count, "Record Updated successfully ")

    update.message.reply_text("Okay, edited your task name.", reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def edit_task_deadline(update: Update, context: CallbackContext) -> int:
    edited_task_deadline = update.message.text
    checker = task_to_be_edited.split(' - ')[1]

    connection = get_connection()
    cursor = connection.cursor()
    sql_update_query = """Update tasks set deadline = %s where deadline = %s"""
    cursor.execute(sql_update_query, (edited_task_deadline, checker), )
    connection.commit()
    count = cursor.rowcount
    print(count, "Record Updated successfully ")

    update.message.reply_text("Okay, edited your task deadline.", reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def abort_editing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Editing aborted.", reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def delete_tasks(update: Update, context: CallbackContext) -> int:
    tasks = get_tasks_name(update)
    keyboard = [[str(task)[2:-3]] for task in tasks]
    reply_markup_delete = {"keyboard": keyboard, "one_time_keyboard": True}
    update.message.reply_text("Which task to delete?", reply_markup=reply_markup_delete)
    return CHOOSE_DELETE_TASK


task_to_be_deleted = None


def delete_task_confirmation(update: Update, context: CallbackContext) -> int:
    task_name = update.message.text
    is_inside = False
    for task in get_tasks_name(update):
        if task_name == str(task)[2:-3]:
            is_inside = True
            global task_to_be_deleted
            task_to_be_deleted = task_name
            break

    if not is_inside:
        update.message.reply_text("Task does not exist!")
        return abort_deletion(update, context)
    else:
        update.message.reply_text("Are you sure you want to delete this task?",
                                  reply_markup=confirmation_deletion_keyboard_markup)
        return CONFIRM_DELETION


def confirm_deletion(update: Update, context: CallbackContext) -> int:
    # TODO get the task
    # Update single record w
    try:
        sql_delete_query = """Delete from tasks where NAME = %s"""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql_delete_query, (task_to_be_deleted,))
        connection.commit()
        update.message.reply_text("You deleted this task.", reply_markup=continue_or_not_keyboard_markup)
        return CONTINUE_OR_NOT
    except (Exception, psycopg2.Error) as error:
        print("Error in Delete operation", error)


def abort_deletion(update: Update, context: CallbackContext) -> int:
    # TODO get the task
    update.message.reply_text("Deletion aborted.", reply_markup=continue_or_not_keyboard_markup)
    return CONTINUE_OR_NOT


def help_message(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Here are a list of commands you can use:\n"
                              "/list - View your tasks\n"
                              "/add - Add your tasks\n"
                              "/edit - Edit your tasks\n"
                              "/delete - Delete your tasks\n"
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
                CommandHandler('exit', cancel)
            ],
            ADD_TASK_NAME: [
                MessageHandler(Filters.text, add_task_name)
            ],
            ADD_TASK_DEADLINE: [
                MessageHandler(Filters.text, add_task_deadline)
            ],
            CHOOSE_EDIT_TASK: [
                MessageHandler(Filters.text, edit_task_confirmation)
            ],
            CHOOSE_EDIT_FIELDS: [
                CommandHandler('name', ask_edited_name),
                CommandHandler('deadline', ask_edited_deadline)
            ],
            EDIT_TASK_NAME: [
                MessageHandler(Filters.text, edit_task_name)
            ],
            EDIT_TASK_DEADLINE: [
                MessageHandler(Filters.text, edit_task_deadline)
            ],
            CHOOSE_DELETE_TASK: [
                MessageHandler(Filters.text, delete_task_confirmation)
            ],
            CONFIRM_DELETION: [
                CommandHandler('yes', confirm_deletion),
                CommandHandler('no', abort_deletion)
            ],
            CONTINUE_OR_NOT: [
                CommandHandler('continue', continue_using),
                CommandHandler('end', cancel)
            ]

        },
        fallbacks=[CommandHandler('help', help_message), CommandHandler('exit', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://just-do-it-bot.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
