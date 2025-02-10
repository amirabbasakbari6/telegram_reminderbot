# bot.py: Telegram Bot Implementation
import telebot
import mysql.connector
from config import TOKEN
from config import DB_CONFIG
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from DML import insert_user, add_reminder, fetch_due_reminders, mark_reminder_notified
from datetime import datetime
import threading
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)


bot = telebot.TeleBot(TOKEN)

# Start command
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    chat_id = message.chat.id
  
    try:
        print(f"Attempting to insert user: {user_id}, {username}, {chat_id}")
        insert_user(user_id, username, chat_id)
        print("User inserted successfully")
        bot.send_message(chat_id, "Welcome! Use the buttons below to interact with the bot.", reply_markup=get_main_menu())
        logging.info(f"User registered: user_id={user_id}, username={username}, chat_id={chat_id}")
    except Exception as e:
        print(f"Error in start_command: {e}")
        logging.error(f"Error registering user: {e}")

# Main menu keyboard
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("Add Reminder"), KeyboardButton("Add Weekly Schedule"), KeyboardButton("View Schedule"))
    return markup

# Handle main menu choices
@bot.message_handler(func=lambda message: message.text in ["Add Reminder", "Add Weekly Schedule", "View Schedule"])
def handle_menu_choice(message):
    if message.text == "Add Reminder":
        set_reminder(message)
    elif message.text == "Add Weekly Schedule":
        add_weekly_schedule(message)
    elif message.text == "View Schedule":
        view_schedule(message)

# Set reminder command
def set_reminder(message):
    msg = bot.send_message(message.chat.id, "Please send your reminder in the format: Reminder Text | YYYY-MM-DD HH:MM")
    bot.register_next_step_handler(msg, process_reminder)

def process_reminder(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        reminder_text, reminder_time_str = message.text.split('|')
        reminder_time = datetime.strptime(reminder_time_str.strip(), "%Y-%m-%d %H:%M")

        add_reminder(user_id, reminder_text.strip(), reminder_time)
        bot.send_message(chat_id, f"Reminder set for {reminder_time}.")
        logging.info(f"Reminder added: user_id={user_id}, text={reminder_text.strip()}, time={reminder_time}")
    except Exception as e:
        bot.send_message(message.chat.id, "Error setting reminder. Please use the correct format.")
        logging.error(f"Error setting reminder: {e}")

# Add weekly schedule
def add_weekly_schedule(message):
    msg = bot.send_message(message.chat.id, "Please send your weekly schedule in the format: Day | Task (e.g., Monday | Gym at 6 PM)")
    bot.register_next_step_handler(msg, process_weekly_schedule)

def process_weekly_schedule(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day, task = message.text.split('|')
        day = day.strip().capitalize()
        task = task.strip()

        if day not in valid_days:
            bot.send_message(chat_id, f"Invalid day: {day}. Please use a valid day (e.g., Monday, Tuesday, etc.).")
            return

        if not task:
            bot.send_message(chat_id, "The task cannot be empty. Please provide a valid task.")
            return

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "INSERT INTO WeeklySchedule (user_id, day, task) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, day, task))
        conn.commit()
        conn.close()

        bot.send_message(chat_id, f"Weekly schedule updated: {day} | {task}")
        logging.info(f"Weekly schedule added: user_id={user_id}, day={day}, task={task}")
    except ValueError:
        bot.send_message(message.chat.id, "Error: Please use the format 'Day | Task' (e.g., Wednesday | Gym at 20:53).")
        logging.error(f"ValueError: Invalid format in message: {message.text}")
    except Exception as e:
        bot.send_message(message.chat.id, "Error adding weekly schedule. Please try again later.")
        logging.error(f"Error adding weekly schedule: {e}")


# View weekly schedule
def view_schedule(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "SELECT day, task FROM WeeklySchedule WHERE user_id = %s ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        conn.close()

        if results:
            schedule = "Your weekly schedule:\n"
            for day, task in results:
                schedule += f"- {day}: {task}\n"
            bot.send_message(chat_id, schedule)
            logging.info(f"Weekly schedule sent: user_id={user_id}")
        else:
            bot.send_message(chat_id, "Your weekly schedule is empty.")
            logging.info(f"No weekly schedule for user_id={user_id}")
    except Exception as e:
        bot.send_message(chat_id, "Error retrieving weekly schedule.")
        logging.error(f"Error retrieving weekly schedule: {e}")

# Background thread for sending reminders
def notify_users():
    while True:
        try:
            due_reminders = fetch_due_reminders()
            for reminder_id, user_id, reminder_text, reminder_time in due_reminders:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                query = "SELECT chat_id FROM Users WHERE user_id = %s;"
                cursor.execute(query, (user_id,))
                chat_id = cursor.fetchone()[0]

                bot.send_message(chat_id, f"Reminder: {reminder_text}")
                mark_reminder_notified(reminder_id)
                logging.info(f"Reminder notified: reminder_id={reminder_id}, user_id={user_id}")

                conn.close()
        except Exception as e:
            logging.error(f"Error in notification thread: {e}")
        time.sleep(60)

# Start the bot and background thread
if __name__ == "__main__":
    logging.info("Bot started.")
    threading.Thread(target=notify_users, daemon=True).start()
    bot.polling(none_stop=True)




 