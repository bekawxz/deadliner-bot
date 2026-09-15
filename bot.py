import os
import db
from pathlib import Path

import telebot

def load_bot_token():
    token = os.environ.get('BOT_TOKEN')
    if token:
        return token

    env_file = Path(__file__).with_name('api.env')
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            if line.startswith('export BOT_TOKEN='):
                return line.removeprefix('export BOT_TOKEN=').strip().strip("'\"")

    return None


BOT_TOKEN = load_bot_token()
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN is not set. Set it to your Telegram bot token before starting the bot.')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hi, it is your Deadliner bot! I will help you to manage your tasks and deadlines.")

@bot.message_handler(commands=['menu'])
def send_menu(message):
    bot.send_message(message.chat.id, "Here is the menu of available commands:\n"
                                            "/start - Start the bot and get a welcome message\n"
                                            "/menu - Show this menu of available commands\n"
                                            "/add_task - Add a new task with a deadline\n"
                                            "/list_tasks - List all your tasks with their deadlines\n"
                                            "/delete_task - Delete a task by its ID\n"
                                            "/edit_task - Edit a task by its ID\n")

@bot.message_handler(commands=['add_task'])
def add_task(message):
    bot.send_message(message.chat.id, "Send me a description and deadline of your task with this template:\n"
                                            "Description / date / time\n"
                                            "Example: Complete your HW / 10.10.2026 / 17:00\n"
                     )
    bot.register_next_step_handler(message,add_text)

def add_text(message):
    try:
        parts = []
        for part in message.text.split(' / '):
            parts.append(part)
        description, date, time = parts
        deadline = f"{date} {time}"
        db.add_task(message.from_user.id, description, deadline)

    except ValueError:
        bot.send_message(message.chat.id, "That didn't match the template. Please use: Description / date / time")
        return
    
    bot.send_message(message.chat.id, f"Task added!\nDescription: {description}\nDeadline: {date} {time}")

@bot.message_handler(commands=['list_tasks'])
def list_tasks(message):
    tasks = db.list_tasks(message.from_user.id)
    if not tasks:
        bot.send_message(message.chat.id, "There is no tasks yet.")
        return
    result = "Your tasks\n"
    for task in tasks:
        task_id, description, deadline = task
        result += f"#{task_id}: {description} - due {deadline}\n"

    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['delete_task'])
def delete_task(message):
    tasks = db.list_tasks(message.from_user.id)
    if not tasks:
        bot.send_message(message.chat.id, "There is no tasks to delete")
        return
    result = "Your tasks\n"
    for task in tasks:
        task_id, description, deadline = task
        result += f"#{task_id}: {description} - due {deadline}\n"
    bot.send_message(message.chat.id, result)
    bot.send_message(message.chat.id, "Send an ID of the task that you want to be deleted")

    bot.register_next_step_handler(message,delete_text)

def delete_text(message):
    try:
        task_id = int(message.text)
        count = db.delete_task(message.from_user.id,task_id)

        if not count:
            bot.send_message(message.chat.id, "That is not a number of ID listed")
            return
        
        bot.send_message(message.chat.id, "Your task has been deleted successfully")
    except ValueError:
        bot.send_message(message.chat.id, "That is not a number of ID listed")
        return

@bot.message_handler(commands=['edit_task'])
def edit_task(message):
    bot.send_message(message.chat.id, "Send a description of update and ID of task in this format\n"
                                        "ID / Description / Clean your room\n"
                                        "ID / Deadline / 15.09.2026 18:00")
    bot.register_next_step_handler(message, edit_text)
def edit_text(message):
    try:
        parts = []

        for part in message.text.split(" / "):
            parts.append(part)

        id, type, value = parts

        count = 1    
        if type == "Description":
            count = db.edit_description(value,int(id), message.from_user.id)    
        elif type == "Deadline":
            count = db.edit_deadline(value,int(id), message.from_user.id)
        else:
            bot.send_message(message.chat.id,"Invalid format")
            return
        if not count:
            bot.send_message(message.chat.id,"Invalid format")
            return
        bot.send_message(message.chat.id, "Task has been successfully edited!")

    except ValueError:
        bot.send_message(message.chat.id,"Invalid format")
db.init_db()
bot.infinity_polling()