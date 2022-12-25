import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telegram_bot_calendar.wyear import WYearTelegramCalendar

from key import *
import db

import schedule
from datetime import datetime
import time

import threading

import sqlite3

bot = telebot.TeleBot(api_token)


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

    @bot.message_handler(content_types = ["text"])
    def text_reminder(m):
        text = m.text
        bot.send_message(m.chat.id, f"""I saved your reminder!

&#128203; {result.strftime("%d.%m.%Y")}: {text}""", parse_mode="HTML")
        user_id = db_rem_count(m.chat.id) + 1
        db.insert_line(user_id, m.chat.id, result.strftime("%d-%m-%Y"), text)


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

    for line in result:
        bot.send_message(line[0], f"&#128204; Reminder for today: <b>{line[2]}</b>", parse_mode="HTML")

schedule.every().minutes.do(reminder_check)

def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)

th = threading.Thread(target=schedule_run)
th.start()

bot.infinity_polling()
