import mysql.connector
from config import DDL_CONFIG
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(**DDL_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS ReminderBot")
            cursor.execute("USE ReminderBot")
            
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    chat_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Reminders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Reminders (
                    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    reminder_text TEXT NOT NULL,
                    reminder_time DATETIME NOT NULL,
                    is_notified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                )
            """)
            
            # Create WeeklySchedule table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS WeeklySchedule (
                    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    day VARCHAR(10) NOT NULL,
                    task TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id),
                    CONSTRAINT valid_day CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
                )
            """)
            
            print("Database and tables created successfully!")
            
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_database()