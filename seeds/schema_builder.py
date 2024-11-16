
HOTEL_SCHEMA =  '''
                CREATE TABLE IF NOT EXISTS hotels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_name TEXT NOT NULL UNIQUE,
                    name TEXT,
                    star TEXT,
                    rank TEXT,
                    address TEXT,
                    url TEXT,
                    phone TEXT,
                    checkin TEXT,
                    checkout TEXT
                )
                '''

REVIEWS_SCHEMA = '''
                 CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hotel_id INTEGER,
                    review_id TEXT UNIQUE,
                    score TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    FOREIGN KEY (hotel_id) REFERENCES hotels
                 )
                 '''

ANALYZE_SCHEMA = '''
                 CREATE TABLE IF NOT EXISTS analyzes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hotel_id INTEGER,
                    review TEXT,
                    positive_key TEXT,
                    negative_key TEXT,
                    star TEXT,
                    recommand TEXT,
                    FOREIGN KEY (hotel_id) REFERENCES hotels
                )
                '''
    
KEYCOUNTS_SCHEMA = '''
                    CREATE TABLE IF NOT EXISTS keycounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hotel_id INTEGER,
                        key TEXT,
                        count TEXT,
                        type TEXT,
                        FOREIGN KEY (hotel_id) REFERENCES hotels
                    )
                    '''
FORMED_FILE_SCHEMA = '''
                     CREATE TABLE IF NOT EXISTS formed (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hotel_id INTEGER,
                        file TEXT,
                        FOREIGN KEY (hotel_id) REFERENCES hotels
                     )
                     '''