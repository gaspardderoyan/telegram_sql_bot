import telebot
from datetime import datetime
import psycopg2

# Telegram bot token
# API_TOKEN = os.getenv('TELEBOT_API_TOKEN')
API_TOKEN = '6815815949:AAGyoSzN104foY5ZTCRNAS7Brt1L7BpyOhg'
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
    user="super",
    password="dopamine",
    host="gasparddjivan-3645.postgres.pythonanywhere-services.com",
    port="13645",
    database="postgres")

# def create_connection(db_url):
#     # Parse database URL
#     result = urlparse(db_url)
#     username = result.username
#     password = result.password
#     database = result.path[1:]  # Exclude the leading '/'
#     hostname = result.hostname
#     port = result.port

#     # Connect to the database
#     conn = psycopg2.connect(
#         database=database,
#         user=username,
#         password=password,
#         host=hostname,
#         port=port
#     )
#     print("Connection to PostgreSQL DB successful")
#     return conn


# Database URL
# db_url = os.getenv('DB_URL')

# Connect to the database
# conn = create_connection(db_url)

# Remember to close the connection when done
# connection.close()




# Connect to your postgres DB
# DB_NAME = os.getenv('DB_NAME')
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')

# conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cursor = conn.cursor()

""" 2 actions boolean logs
def process_habit(habit_type, message):
    chat_id = message.chat.id
    try:
        if message.text == 'Yes':
            bot.send_message(chat_id, f'Good job on your {habit_type}!')
            cursor.execute(f"INSERT INTO Habits (habit_type, boolean_value) VALUES ('{habit_type}', TRUE);")
            conn.commit()
        elif message.text == 'No':
            bot.send_message(chat_id, f'You should keep up with your {habit_type}.')
            cursor.execute(f"INSERT INTO Habits (habit_type, boolean_value) VALUES ('{habit_type}', FALSE);")
            conn.commit()
    except ValueError:
        bot.reply_to(message, 'Please enter a valid answer.')

def process_meditate(message):
    process_habit('Meditation', message)

def process_fluoxetine(message):
    process_habit('Fluoxetine', message)

def process_journal(message):
    process_habit('Journal', message)

def process_na_meeting(message):
    process_habit('NA Meeting', message)
 """


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

""" 2 actions boolean logs
def ask_habit(command, question, next_step_handler):
    @bot.message_handler(commands=[command])
    def ask(message):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Yes')
        itembtn2 = types.KeyboardButton('No')
        markup.add(itembtn1, itembtn2)
        msg = bot.reply_to(message, question, reply_markup=markup)
        bot.register_next_step_handler(msg, next_step_handler)

ask_habit('meditate', "Did you meditate?", process_meditate)
ask_habit('fluoxetine', "Did you take your fluoxetine?", process_fluoxetine)
ask_habit('journal', "Did you journal?", process_journal)
ask_habit('na_meeting', "Did you attend an NA meeting?", process_na_meeting)
 """

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
