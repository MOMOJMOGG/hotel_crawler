import os
import sqlite3 as sql

from modules.settings.config_manager import config
from seeds.schema_builder import *

class DBManager:
    
    def __init__(self):
        
        self.conn = None
        self.cursor = None
    
    def init_settings(self):
        self.conn = sql.connect(config.dir.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    # === hotel exist check ===
    def check_hotel_exist(self, hotel_name):
        self.cursor.execute("SELECT * FROM hotels WHERE search_name = ?", (hotel_name,))
        hotel = self.cursor.fetchone()
        
        return self.parse_hotel(hotel) if hotel else {}

    def parse_hotel(self, data):
        hotel_id, search_name, name, star, rank, address, url, phone, checkin, checkout = data
        return {
            'id': hotel_id,
            'search_name': search_name,
            'name': name,
            'star': star,
            'rank': rank,
            'information': {
                'address': address,
                'url': url,
                'phone': phone,
                'time': {
                    'start': checkin,
                    'end': checkout
                }
            }
        }
    
    # === fetch data ===
    def get_hotel_reviews(self, hotel_id):
        self.cursor.execute("SELECT * FROM reviews WHERE hotel_id = ?", (hotel_id,))
        reviews = self.cursor.fetchall()
        
        return self.parse_reviews(reviews) if reviews else []

    def parse_reviews(self, reviews):
        result = []
        for data in reviews:
            table_id, hotel_id, review_id, score, duration, comment = data
            result.append({
                'id': table_id,
                'review_id': review_id,
                'score': score,
                'duration': duration,
                'comment': comment
            })
        
        return result
    
    def get_hotel_analyzes(self, hotel_id):
        self.cursor.execute("SELECT * FROM analyzes WHERE hotel_id = ?", (hotel_id,))
        analyzes = self.cursor.fetchall()
        
        return self.parse_analyzes(analyzes) if analyzes else []

    def parse_analyzes(self, analyzes):
        result = []
        
        for data in analyzes:
            table_id, hotel_id, comment, positive_key, negative_key, score, conclusion = data
            
            result.append({
                'ID': table_id,
                'review': comment,
                'positive': positive_key.split(','),
                'negative': negative_key.split(','),
                'star': score,
                'recommand': conclusion
            })
        return result
    
    def get_keycounts(self, hotel_id):
        self.cursor.execute("SELECT * FROM keycounts WHERE hotel_id = ?", (hotel_id,))
        keycounts = self.cursor.fetchall()
        
        return self.parse_keycounts(keycounts) if keycounts else []

    def parse_keycounts(self, keycounts):
        results = {
            'positive': {},
            'negative': {},
            'summary' : {}
        }
        for data in keycounts:
            table_id, analyze_id, key, count, key_type = data
            results[key_type][key] = int(count)
        
        return results

    def get_formed_file(self, hotel_id):
        self.cursor.execute("SELECT file FROM formed WHERE hotel_id = ?", (hotel_id,))
        file = self.cursor.fetchone()
        
        return file[0] if file else ""
        

    # === storage data ===
    def insert_hotel(self, search_name, data):
        name = data['name']
        star = data['star']
        rank = data['rank']
        address = data['information'].get('address', '')
        url = data['information'].get('url', '')
        phone = data['information'].get('phone', '')
        checkin  = ''
        checkout = ''
        if data['information'].get('time'):
            checkin = data['information']['time'].get('start', '')
            checkout = data['information']['time'].get('end', '')

        self.cursor.execute("INSERT INTO hotels (search_name, name, star, rank, address, url, phone, checkin, checkout) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (search_name, name, star, rank, address, url, phone, checkin, checkout))
        self.conn.commit()
        return self.cursor.lastrowid    #? hotel id

    def insert_reviews(self, hotel_id, data):
        review_id = data['review_id']
        score = data['score']
        duration = data['duration']
        comment = data['comment']
        
        self.cursor.execute("INSERT INTO reviews (hotel_id, review_id, score, duration, comment) VALUES (?, ?, ?, ?, ?)",
                            (hotel_id, review_id, score, duration, comment))
        self.conn.commit()
        return True

    def insert_analyzes(self, hotel_id, data):
        review = data['review']
        positive_key = ",".join(data['positive'])
        negative_key = ",".join(data['negative'])
        star = data['star']
        recommand = data['recommand']
        
        self.cursor.execute("INSERT INTO analyzes (hotel_id, review, positive_key, negative_key, star, recommand) VALUES (?, ?, ?, ?, ?, ?)",
                            (hotel_id, review, positive_key, negative_key, star, recommand))
        self.conn.commit()
        return True
    
    def insert_keycounts(self, hotel_id, counters):
        positive_counter = counters.get('positive')
        negative_counter = counters.get('negative')
        summary_counter  = counters.get('summary')
        
        for key, val in positive_counter.items():
            self.cursor.execute("INSERT INTO keycounts (hotel_id, key, count, type) VALUES (?, ?, ?, ?)",
                                (hotel_id, key, val, 'positive'))
        
        
        for key, val in negative_counter.items():
            self.cursor.execute("INSERT INTO keycounts (hotel_id, key, count, type) VALUES (?, ?, ?, ?)",
                                (hotel_id, key, val, 'negative'))
        
        for key, val in summary_counter.items():
            self.cursor.execute("INSERT INTO keycounts (hotel_id, key, count, type) VALUES (?, ?, ?, ?)",
                                (hotel_id, key, val, 'summary'))
        
        self.conn.commit()
        return True

    def insert_formed_record(self, hotel_id, file):
        self.cursor.execute("INSERT INTO formed (hotel_id, file) VALUES (?, ?)",
                            (hotel_id, file))
        self.conn.commit()
        return True

db = DBManager()
db.init_settings()