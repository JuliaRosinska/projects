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
    bot.send_message(m.chat.id, """<b>&#128215; List of available commands:</b>
/new - create reminder
/view - all reminders""", parse_mode="HTML")


#   Create new reminder
@bot.message_handler(commands=['new'])
def new_reminder(m):
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
    global text
    text = m.text
    if text.startswith("/"):
        check_comm(m)
        return

    bot.send_message(m.chat.id, "Enter the time in 30 minute step:")
    bot.register_next_step_handler(m, time_reminder)

def time_reminder(m):
    regex = r"^[0-9]{1,2}:[0-9]{2}$"
    time = m.text

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
    reminders = db.select_user(m.chat.id)
    message = f"&#128203; <b>ID</b>    <b>DATE</b>          <b>REMINDER</b>\n"
    for line in reminders:
        message += f"&#128204; <b>{line[0]}</b>      {line[1]}:  {line[2]}\n"
    bot.send_message(m.chat.id, message, parse_mode="HTML")



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
