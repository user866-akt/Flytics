import psycopg2
from psycopg2.extras import execute_values
import random
import json
from datetime import datetime

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'postgres', 'password': '7777',
    'host': 'localhost', 'port': '5433'
}

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

cur.execute("SELECT id FROM client")
clients = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM booking")
bookings = [row[0] for row in cur.fetchall()]

cur.execute("ALTER TABLE client ADD COLUMN IF NOT EXISTS loyalty_level VARCHAR(20)")
cur.execute("ALTER TABLE client ADD COLUMN IF NOT EXISTS preferences JSONB")

cur.execute("ALTER TABLE booking ADD COLUMN IF NOT EXISTS notes TEXT")
cur.execute("ALTER TABLE booking ADD COLUMN IF NOT EXISTS baggage_info JSONB")
conn.commit()

client_updates = []
loyalty_levels = ['BASE', 'SILVER', 'GOLD', 'PLATINUM']
loyalty_weights = [0.7, 0.15, 0.1, 0.05]

for client_id in clients:
    loyalty = random.choices(loyalty_levels, weights=loyalty_weights)[0]
    preferences = json.dumps({
        'meal': random.choice(['standard', 'vegetarian', None]),
        'notifications': random.choice([True, False, None]),
        'language': random.choice(['ru', 'en', None])
    })
    client_updates.append((loyalty, preferences, client_id))

execute_values(cur, """
    UPDATE client SET 
        loyalty_level = data.loyalty_level,
        preferences = data.preferences::jsonb
    FROM (VALUES %s) AS data(loyalty_level, preferences, id)
    WHERE client.id = data.id
""", client_updates, page_size=1000)

booking_updates = []
uniform_prices = [random.randint(5000, 50000) for _ in range(100)]
skewed_prices = [int(100000 / (i+1)) for i in range(1, 101)]
low_card_prices = [9990, 19990, 29990, 49990, 99990]

for booking_id in bookings[:50000]:
    if random.random() > 0.15:
        note_templates = [
            "Просьба позвонить за 3 часа до вылета",
            "Пассажир с ограниченными возможностями",
            "Особое питание: без глютена",
            "VIP клиент, встреча в аэропорту",
            "Стыковочный рейс через 2 часа",
        ]
        notes = random.choice(note_templates)
    else:
        notes = None
    
    if random.random() > 0.2:
        baggage = {
            'bags': random.randint(0, 3),
            'weight': random.choice([None, 10, 15, 20, 23, 30]),
            'sport_equipment': random.random() < 0.05
        }
        baggage_info = json.dumps(baggage)
    else:
        baggage_info = None
    
    dist_type = random.choices(['uniform', 'skewed', 'low_card'], weights=[0.4, 0.4, 0.2])[0]
    if dist_type == 'uniform':
        demo_price = random.choice(uniform_prices)
    elif dist_type == 'skewed':
        demo_price = random.choice(skewed_prices)
    else:
        demo_price = random.choice(low_card_prices)
    
    booking_updates.append((notes, baggage_info, demo_price, booking_id))

for i in range(0, len(booking_updates), 1000):
    batch = booking_updates[i:i+1000]
    execute_values(cur, """
        UPDATE booking SET 
            notes = data.notes,
            baggage_info = data.baggage_info::jsonb,
            total_cost = data.demo_price
        FROM (VALUES %s) AS data(notes, baggage_info, demo_price, id)
        WHERE booking.id = data.id
    """, batch, page_size=100)
    conn.commit()

conn.commit()
cur.close()
conn.close()