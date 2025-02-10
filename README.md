# Telegram Reminder Bot

This is a Telegram bot that allows users to set reminders and manage a weekly schedule. The bot interacts with a MySQL database to store user data and scheduled tasks.

## Features 
- **Set Reminders**: Users can set reminders in a specific format.
- **Weekly Schedule**: Users can add and view their weekly schedules.
- **Automated Notifications**: Sends reminders to users at the scheduled time.
- **User Registration**: Automatically registers users when they start interacting with the bot.
- **Logging**: Logs all activities for debugging and tracking purposes.

## Technologies Used
- **Python**
- **Telegram Bot API** (with `telebot`)
- **MySQL Database**
- **Logging**
- **Multithreading for background notifications**

## Code Explanation

### Bot Initialization
```python
bot = telebot.TeleBot(TOKEN)
```
> This line initializes the bot using the token provided in `config.py`.

### Handling the `/start` Command
```python
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    chat_id = message.chat.id
```
> When a user sends `/start`, the bot extracts their user ID, username, and chat ID, then attempts to store them in the database.

### Creating the Main Menu
```python
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("Add Reminder"), KeyboardButton("Add Weekly Schedule"), KeyboardButton("View Schedule"))
    return markup
```
> This function generates a keyboard markup with buttons for main menu options.

### Setting Reminders
```python
def set_reminder(message):
    msg = bot.send_message(message.chat.id, "Please send your reminder in the format: Reminder Text | YYYY-MM-DD HH:MM")
    bot.register_next_step_handler(msg, process_reminder)
```
> This function prompts the user to input a reminder in the correct format and registers the next step to process the input.

### Processing Reminders
```python
def process_reminder(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        reminder_text, reminder_time_str = message.text.split('|')
        reminder_time = datetime.strptime(reminder_time_str.strip(), "%Y-%m-%d %H:%M")

        add_reminder(user_id, reminder_text.strip(), reminder_time)
        bot.send_message(chat_id, f"Reminder set for {reminder_time}.")
    except Exception as e:
        bot.send_message(message.chat.id, "Error setting reminder. Please use the correct format.")
```
> This function extracts the reminder text and time, stores it in the database, and notifies the user of the successful creation.

### Background Reminder Notification Thread
```python
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
                conn.close()
        except Exception as e:
            logging.error(f"Error in notification thread: {e}")
        time.sleep(60)
```
> This function runs in the background, continuously checking for due reminders and sending notifications to users.

## Logging
- Logs are saved in `bot.log` for debugging and tracking activities.





