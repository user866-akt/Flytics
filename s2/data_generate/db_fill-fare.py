import psycopg2
from psycopg2.extras import execute_values
import random

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

cur.execute("SELECT id FROM flight")
flights = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id, description FROM fare_class")
classes = cur.fetchall()

cur.execute("SELECT flight_id, fare_class_id FROM fare")
existing = set((row[0], row[1]) for row in cur.fetchall())

data = []
for flight in flights:
    for class_id, desc in classes:
        if (flight, class_id) in existing:
            continue
        
        # цены по классам
        if 'Economy' in desc:
            price = random.randint(3000, 15000)
            seats = random.randint(50, 150)
        elif 'Premium' in desc:
            price = random.randint(15000, 30000)
            seats = random.randint(20, 50)
        elif 'Business' in desc:
            price = random.randint(30000, 80000)
            seats = random.randint(5, 20)
        else:  # First
            price = random.randint(80000, 200000)
            seats = random.randint(1, 10)
        
        price = round(price/100)*100
        data.append((flight, class_id, price, seats))

if data:
    execute_values(cur,
        "INSERT INTO fare (flight_id, fare_class_id, price, available_seats) VALUES %s ON CONFLICT (flight_id, fare_class_id) DO NOTHING",
        data, page_size=1000)
    conn.commit()

cur.close()
conn.close()
