import sqlite3 as sql
from seeds.schema_builder import *
import os

if not os.path.exists('seeds/db/hotel_reviews.db'):
    conn = sql.connect('seeds/db/hotel_reviews.db')
    cursor = conn.cursor()
    cursor.execute(HOTEL_SCHEMA)
    cursor.execute(REVIEWS_SCHEMA)
    cursor.execute(ANALYZE_SCHEMA)
    cursor.execute(KEYCOUNTS_SCHEMA)
    cursor.execute(FORMED_FILE_SCHEMA)

    conn.commit()
