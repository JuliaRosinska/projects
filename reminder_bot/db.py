import sqlite3
from datetime import date

#   Database connection
db = sqlite3.connect('reminders.db', check_same_thread=False)
cursor = db.cursor()


#   Work with database
def insert_line(id_user: int, chat_id: int, rem_date: str, rem_text: str, rem_time: str = None):
    """Insert line to reminders table"""

    cursor.execute(f'INSERT INTO reminders (id_user, chat_id, rem_date, rem_text, rem_time) VALUES (?, ?, ?, ?, ?)', (id_user, chat_id, rem_date, rem_text, rem_time))
    db.commit()


def select_today():
    """Select all lines where date == today"""

    today = date.today().strftime("%d-%m-%Y")
    cursor.execute(f"""SELECT id, chat_id, rem_date, rem_text, rem_time FROM reminders WHERE rem_date = "{today}";""")
    result = cursor.fetchall()
    return result


def rem_count(chat_id):
    """Return count of lines by chat_id. This is used to determine user_id."""

    cursor.execute(f"SELECT COUNT(*) FROM reminders WHERE chat_id = '{chat_id}'")
    result = cursor.fetchall()
    return result[0][0]


def select_user(chat_id):
    """Select all user reminderds."""

    cursor.execute(f"""SELECT id_user, rem_date, rem_text FROM reminders WHERE chat_id ="{chat_id}";""")
    result = cursor.fetchall()
    return result

def select_by_id_user(id_list, chat_id):
    """Select reminders by id_user"""

    id_str = ", ".join(id_list)
    cursor.execute(f"""SELECT * FROM reminders WHERE chat_id = {chat_id} AND id_user IN ({id_str})""")
    result = cursor.fetchall()
    return result

def check_reminder(chat_id, id_user):
    """Check if reminder exist in table. Return boolean."""

    cursor.execute(f"""SELECT * FROM reminders WHERE chat_id = {chat_id} AND id_user = {id_user}""")
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return True

def update_id(chat_id):
    """Rewrite all id_user after removin. Renumbers the list of reminders."""
    cursor.execute(f"""UPDATE reminders SET id_user = (SELECT new_id FROM (SELECT id, ROW_NUMBER () OVER() as new_id FROM reminders WHERE chat_id = 371971695)) WHERE chat_id = 371971695;""")


def delete_reminder(chat_id, id_user):
    """Delet reminder by id."""

    cursor.execute(f"""DELETE FROM reminders WHERE chat_id = {chat_id} AND id_user = {id_user}""")
    db.commit()

def delete_all_reminders(chat_id):
    """Delete all users reminders"""

    cursor.execute(f"""DELETE FROM reminders WHERE chat_id = {chat_id}""")
    db.commit()
