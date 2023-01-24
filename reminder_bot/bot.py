import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telegram_bot_calendar.wyear import WYearTelegramCalendar

from key import *
import db

import schedule
from datetime import datetime
import time
import re

import threading

import sqlite3


bot = telebot.TeleBot(api_token)

#   Check commands
def check_comm(m):
    if m.text == "/start":
        send_welcome(m)
    elif m.text == "/view":
        reminders_view(m)
    elif m.text == "/new":
        new_reminder(m)
    elif m.text == "/remove":
        reminder_remove(m)
    else:
        help(m)

#   Commands handlers
@bot.message_handler(commands=['start'])
def send_welcome(m):
    chat_id = m.chat.id
    bot.send_message(m.chat.id,
    """<b>Hi! &#128513;</b>
For the new reminder send /new""", parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(commands=['help'])
def help(m):
    """Send message to user with all available commands"""

    bot.send_message(m.chat.id, """<b>&#128215; List of available commands:</b>
/new - create reminder
/view - all reminders""", parse_mode="HTML")


#   Create new reminder
@bot.message_handler(commands=['new'])
def new_reminder(m):
    """Creating a new reminder with 3 steps: chossing date, enter text and time"""

    calendar, step = WYearTelegramCalendar().build()
    bot.send_message(m.chat.id,
                     f"Select {LSTEP[step]} &#128197;", parse_mode="HTML",
                     reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    global result
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]} &#128197;",
                              c.message.chat.id,
                              c.message.message_id,
                              parse_mode="HTML",
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"""You selected <b>{result}</b> &#11088;
Enter message:""",
                              c.message.chat.id,
                              c.message.message_id,
                              parse_mode="HTML")

        bot.register_next_step_handler(c.message, text_reminder)

@bot.message_handler(content_types = ["text"])
def text_reminder(m):
    """Handle text message"""

    global text
    text = m.text

    if text.startswith("/"):
        check_comm(m)
        return

    bot.send_message(m.chat.id, "Enter the time in 30 minute step:")
    bot.register_next_step_handler(m, time_reminder)

def time_reminder(m):
    """Handle time"""

    regex = r"^[0-9]{1,2}:[0-9]{2}$"
    time = m.text

    if time.startswith("/"):
        check_comm(m)
        return

    if not re.search(regex, time):
        bot.send_message(m.chat.id, "You entered incorrect time, please try again:")
        bot.register_next_step_handler(m, time_reminder)
        return

    hour_str, minutes_str = time.split(":")
    hour = int(hour_str)
    minutes = int(minutes_str)
    if hour > 24 and hour < 0:
        bot.send_message(m.chat.id, "You entered incorrect hour, please try again:")
        bot.register_next_step_handler(m, time_reminder)

    elif minutes != 0 and minutes != 30:
        bot.send_message(m.chat.id, "You entered incorrect minutes, please try again:")
        bot.register_next_step_handler(m, time_reminder)

    else:
        bot.send_message(m.chat.id, f"""I saved your reminder!

&#128203; {result.strftime("%d.%m.%Y")}  <b>{time}</b>: {text}""", parse_mode="HTML")
        user_id = db.rem_count(m.chat.id) + 1
        db.insert_line(user_id, m.chat.id, result.strftime("%d-%m-%Y"), text, time)


@bot.message_handler(commands=['view'])
def reminders_view(m):
    """Send to user a list of all reminders"""

    reminders = db.select_user(m.chat.id)
    if db.rem_count(m.chat.id) == 0:
        bot.send_message(m.chat.id, "You have no reminders yet.")
    else:
        message = f"&#128203; <b>ID</b>    <b>DATE</b>          <b>REMINDER</b>\n"
        for line in reminders:
            message += f"&#128204; <b>{line[0]}</b>      {line[1]}:  {line[2]}\n"
        bot.send_message(m.chat.id, message, parse_mode="HTML")


@bot.message_handler(commands=['remove'])
def reminder_remove(m):
    """Remove reminder by id_user"""

    bot.send_message(m.chat.id, """If you need to remove reminders please send me a list of ids separated by a comma.
<pre>
1 - remove one reminders with id 1
2,4,5 - remove reminders with id 2, 4, 5
all - remove all your reminders
</pre>""", parse_mode="HTML")
    bot.register_next_step_handler(m, remove_handle)

@bot.message_handler(content_types = ["text"])
def remove_handle(m):
    if m.text.startswith("/"):
        check_comm(m)
        return

    text = m.text.strip()
    id_list = []

    regex = r"^([0-9]*)+(,[0-9]+)+$"

    if text == "all":
        """Handle removing all reminders."""
        bot.send_message(m.chat.id, """Are you sure? Reminder that will be remove: all
yes / no""")
        bot.register_next_step_handler(m, remove_all_confirm)

    elif re.search(regex, text):
        """Handle removing some reminders."""
        id_list = text.split(",")
        reminders = db.select_by_id_user(id_list, m.chat.id)

        global count_non_existent
        count_non_existent = 0
        for idx, id in enumerate(id_list):
            if db.check_reminder(m.chat.id, id_list[idx]):
                continue
            else:
                count_non_existent += 1
                bot.send_message(m.chat.id, "Reminder with id<b> " + id + "</b> doesn't exist. Please try again.", parse_mode = "HTML")
        if count_non_existent > 0:
            bot.register_next_step_handler(m, remove_handle)
            return

        bot.send_message(m.chat.id, """Are you sure? Reminder that will be remove: """ + text + """
yes / no""")
        bot.register_next_step_handler(m, remove_some_confirm, id_list)

    elif re.search(r"^([0-9]*)+$", text):
        """Handle removing one reminder."""
        id_list = text
        if db.check_reminder(m.chat.id, text):
            bot.send_message(m.chat.id, """Are you sure? Reminder that will be remove: """ + text + """
yes / no""")
            bot.register_next_step_handler(m, remove_some_confirm, id_list)
        else:
            bot.send_message(m.chat.id, f"""Reminder with id<b>{text}</b> doesn't exist. Please try again.""", parse_mode = "HTML")
            bot.register_next_step_handler(m, remove_handle)

    else:
        bot.send_message(m.chat.id, """Incorect input. Please try again.""")
        bot.register_next_step_handler(m, remove_handle)


@bot.message_handler(content_types = ["text"])
def remove_some_confirm(m, id_list):
    if m.text.startswith("/"):
        check_comm(m)
        return

    confirm = m.text
    if confirm == "yes":
        for idx, id in enumerate(id_list):
            db.delete_reminder(m.chat.id, id_list[idx])
        bot.send_message(m.chat.id, "Removing access!")

    elif confirm == "no":
        bot.send_message(m.chat.id, "Okey, removing was canceled.")
    else:
        bot.send_message(m.chat.id, "Sorry, I can't understand. Please try again.")
        bot.register_next_step_handler(m, remove_all_confirm)

def remove_all_confirm(m):
    if m.text.startswith("/"):
        check_comm(m)
        return

    confirm = m.text
    if confirm == "yes":
        db.delete_all_reminders(m.chat.id)
        bot.send_message(m.chat.id, "Removing access!")
    elif confirm == "no":
        bot.send_message(m.chat.id, "Okey, removing was canceled.")
    else:
        bot.send_message(chat.id.m, "Sorry, I can't understand. Please try again.")
        bot.register_next_step_handler(m, remove_all_confirm)





#   Reminder handler
def reminder_check():
    result = db.select_today()
    if len(result) < 1:
        return
    current_time = datetime.now().strftime("%H:%M")
    print(current_time)
    for line in result:
        if line[4] == current_time:
            bot.send_message(line[1], f"&#128204; Reminder for today: <b>{line[3]}</b>", parse_mode="HTML")
            db.delete_reminder(line[0])
        else:
            continue

schedule.every().hour.at(":30").do(reminder_check)
schedule.every().hour.at(":00").do(reminder_check)


def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)

th = threading.Thread(target=schedule_run)
th.start()

bot.infinity_polling()
