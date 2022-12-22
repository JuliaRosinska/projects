import telebot


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

bot.infinity_polling()
