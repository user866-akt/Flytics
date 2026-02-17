import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime, timedelta
import numpy as np

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

NUM_FLIGHTS = 260000
START = datetime(2024, 1, 1)
END = datetime(2025, 1, 1)

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

# берем связанные данные
cur.execute("SELECT number FROM flight_number")
flight_numbers = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM aircraft")
aircraft_ids = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id, description FROM flight_status")
statuses = cur.fetchall()
status_ids = [s[0] for s in statuses]

# веса для статусов - большинство рейсов просто прилетают
weights = []
for _, desc in statuses:
    if desc in ['Landed', 'Arrived']:
        weights.append(0.425)  # 85% вместе
    elif desc == 'Delayed':
        weights.append(0.08)   # 8% задержки
    elif desc == 'Cancelled':
        weights.append(0.04)   # 4% отмены
    else:
        weights.append(0.01)   # остальное
weights = np.array(weights) / sum(weights)

# пиковые часы для рейсов
hour_weights = [0.02]*24
for h in range(6,11): hour_weights[h] = 0.08
for h in range(17,23): hour_weights[h] = 0.07
hour_weights = np.array(hour_weights) / sum(hour_weights)

data = []
for i in range(NUM_FLIGHTS):
    if i % 10000 == 0: print(f"{i} рейсов...")
    
    fn = random.choice(flight_numbers)
    aircraft = random.choice(aircraft_ids)
    
    # дата равномерно в течение года
    flight_date = START + timedelta(days=random.randint(0, (END-START).days-1))
    hour = np.random.choice(24, p=hour_weights)
    dep_time = flight_date.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
    
    # полет 1-6 часов
    arr_time = dep_time + timedelta(hours=random.randint(1,6), minutes=random.randint(0,59))
    
    status = int(np.random.choice(status_ids, p=weights))
    data.append((fn, aircraft, dep_time, arr_time, status))
batch_size = 10000
for i in range(0, len(data), batch_size):
    execute_values(cur,
        "INSERT INTO flight (flight_number, aircraft_id, departure_time, arrival_time, status_id) VALUES %s ON CONFLICT (flight_number, departure_time) DO NOTHING",
        data[i:i+batch_size], page_size=1000)
    conn.commit()
cur.close()
conn.close()