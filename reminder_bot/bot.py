import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telegram_bot_calendar.wyear import WYearTelegramCalendar

bot = telebot.TeleBot("5989197400:AAG_4BtZN5I9aCHTJWD3jNFTB1nJpyuv_AE")


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

bot.infinity_polling()
