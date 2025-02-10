import mysql.connector
from config import DB_CONFIG
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def insert_user(user_id, username, chat_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO Users (user_id, username, chat_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        username = VALUES(username),
        chat_id = VALUES(chat_id)
        """
        cursor.execute(query, (user_id, username, chat_id))
        conn.commit()
        
    except Error as e:
        print(f"Error inserting user: {e}")
        raise
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def add_reminder(user_id, reminder_text, reminder_time):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO Reminders (user_id, reminder_text, reminder_time)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, reminder_text, reminder_time))
        conn.commit()
        
    except Error as e:
        print(f"Error adding reminder: {e}")
        raise
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def fetch_due_reminders():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT reminder_id, user_id, reminder_text, reminder_time
        FROM Reminders
        WHERE reminder_time <= NOW()
        AND is_notified = FALSE
        """
        cursor.execute(query)
        reminders = cursor.fetchall()
        return reminders
        
    except Error as e:
        print(f"Error fetching due reminders: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def mark_reminder_notified(reminder_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE Reminders
        SET is_notified = TRUE
        WHERE reminder_id = %s
        """
        cursor.execute(query, (reminder_id,))
        conn.commit()
        
    except Error as e:
        print(f"Error marking reminder as notified: {e}")
        raise
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def get_weekly_schedule(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT day, task
        FROM WeeklySchedule
        WHERE user_id = %s
        ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
        """
        cursor.execute(query, (user_id,))
        schedule = cursor.fetchall()
        return schedule
        
    except Error as e:
        print(f"Error fetching weekly schedule: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()