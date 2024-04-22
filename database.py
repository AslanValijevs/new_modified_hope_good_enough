import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from settings import EMAIL_PROVIDERS, db_Host, db_Password, db_Name, db_User, mn_Host, mn_Name, mn_Collection

def create_table_if_not_exists(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_tab_2 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            received_date DATETIME,
            sender_email VARCHAR(255),
            subject TEXT,
            has_attachments BOOLEAN,
            attachment_count INT,
            recipient_email VARCHAR(255),
            message_id VARCHAR(255)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """)


def open_db_connection():
    db_connection = mysql.connector.connect(host=db_Host, database=db_Name, user=db_User, password=db_Password,
                                            charset='utf8mb4')
    db_cursor = db_connection.cursor()
    db_cursor.execute('SET NAMES utf8mb4')
    db_cursor.execute('SET CHARACTER SET utf8mb4')
    db_cursor.execute('SET character_set_connection=utf8mb4')
    create_table_if_not_exists(db_cursor)

    print("Connected to MySQL Database")
    return db_connection, db_cursor


def open_mongo_connection():
    client = MongoClient(mn_Host)
    db = client[mn_Name]
    print("Connected to MongoDB")
    return db


def close_db_connection(db_connection, db_cursor):
    db_cursor.close()
    db_connection.close()


def insert_into_db(db_cursor, db_connection, mongo_db, email_data):
    try:
        db_cursor.execute("SELECT * FROM email_tab_2 WHERE message_id = %s ", (email_data[6],))
        if db_cursor.fetchone() is None:
            insert_sql = """
                INSERT INTO email_tab_2(received_date, sender_email, subject, has_attachments, attachment_count, recipient_email, message_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            db_cursor.execute(insert_sql, email_data[:7])
            mysql_id = db_cursor.lastrowid
            db_connection.commit()
            print("Inserted into MySQL Database")

            # Insert into MongoDB
            collection = mongo_db[mn_Collection]
            mongo_data = {"_id": mysql_id, "body": email_data[7], "attachments": email_data[8]}
            collection.insert_one(mongo_data)
            print("Inserted into MongoDB")
    except Error as e:
        print("Error while inserting into MySQL:", e)