import sqlite3 as sql

def build_schema(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PROMARY KEY AUDOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        star FLOAT,
        rank TEXT,
        address TEXT,
        url TEXT,
        phone TEXT,
        chechin TEXT,
        checkout TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PROMARY KEY AUDOINCREMENT,
        hotel_id INTEGER,
        review_id TEXT UNIQUE,
        score TEXT NOT NULL,
        duration INTEGER NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyzes (
        id INTEGER PROMARY KEY AUDOINCREMENT,
        hotel_id INTEGER,
        comment TEXT,
        positive_key TEXT,
        negative_key TEXT,
        positive_comment TEXT,
        negative_comment TEXT,
        summary TEXT,
        conclusion TEXT, 
        FOREIGN KEY (hotel_id) REFERENCES hotels
    )
    ''')

if __name__ == "__main__":
    conn = sql.connect('./hotel_reviews.db')
    cursor = conn.cursor()

    build_schema(cursor)

    conn.commit()
    print("資料庫已建立")