import telebot
from datetime import datetime
import psycopg2
import os

# Telegram bot token
API_TOKEN = os.getenv('TELEBOT_API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

""" Commands to paste in BotFather:

# run - records the distance of a run.
# meditate - logs the event of meditating.
# arrived_at_library - Logs the event of arriving at a library.
# left_library - Records the departure from a library.
# fluoxetine - Records the intake of fluoxetine.
# journal - Records the event of journaling.
# na_meeting - Records the event of attending an NA meeting.

"""


conn = psycopg2.connect(
    user= os.getenv('DB_USER'),
    password= os.getenv('DB_PASSWORD'),
    host= os.getenv('DB_HOST'),
    port="13645",
    database="postgres")

cursor = conn.cursor()

# Handle slash commands

# Handle running distance
@bot.message_handler(commands=['run'])
def ask_distance(message):
    msg = bot.reply_to(message, "How far did you run?")
    bot.register_next_step_handler(msg, process_distance)


# Function to handle boolean logs
def log_habit(command, habit_type):
    @bot.message_handler(commands=[command])
    def log(message):
        try:
            cursor.execute(f"INSERT INTO Habits (habit_type, boolean_value) VALUES ('{habit_type}', TRUE);")
            conn.commit()
            bot.send_message(message.chat.id, f'You logged your {habit_type}.')
        except ValueError:
            bot.send_message(message.chat.id, f'An error occurred while logging your {habit_type}.')

# Boolean logs
log_habit('meditate', 'Meditation')
log_habit('fluoxetine', 'Fluoxetine')
log_habit('journal', 'Journal')
log_habit('na_meeting', 'NA Meeting')

# Handle library arrival and departure

@bot.message_handler(commands=['arrived_at_library'])
def arrived_at_library(message):
    cursor.execute("INSERT INTO Habits (habit_type) VALUES ('Arrived at Library');")
    conn.commit()
    bot.send_message(message.chat.id, "You arrived at the library at " + str(datetime.now().strftime("%H:%M:%S")) + ".")


@bot.message_handler(commands=['left_library'])
def left_library(message):
    cursor.execute("INSERT INTO Habits (habit_type) VALUES ('Left Library');")
    conn.commit()
    bot.send_message(message.chat.id, "You left the library at " + str(datetime.now().strftime("%H:%M:%S")) + ".")

    # Fetch the last arrival and departure times
    cursor.execute("SELECT date_time FROM Habits WHERE habit_type = 'Arrived at Library' ORDER BY date_time DESC LIMIT 1")
    arrival_time = cursor.fetchone()[0]

    cursor.execute("SELECT date_time FROM Habits WHERE habit_type = 'Left Library' ORDER BY date_time DESC LIMIT 1")
    departure_time = cursor.fetchone()[0]

    # Calculate duration
    duration = departure_time - arrival_time

    # Insert the new record
    cursor.execute("INSERT INTO Habits (habit_type, value) VALUES (%s, %s)", ('Time at Library', duration.total_seconds()))
    conn.commit()

    formatted_duration = str(duration.seconds // 3600) + 'h' + str((duration.seconds % 3600) // 60) + 'm'
    bot.send_message(message.chat.id, "You spent " + formatted_duration + " at the library.")


# Handle running distance
def process_distance(message):
    try:
        distance = float(message.text)
        chat_id = message.chat.id
        bot.send_message(chat_id, 'You ran for ' + str(distance) + ' km.')

        # Insert the new record
        cursor.execute("INSERT INTO Habits (habit_type, value) VALUES (%s, %s)", ('Running', distance))
        conn.commit()
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()
