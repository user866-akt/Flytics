import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime, timedelta
import numpy as np

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

NUM_BOOKINGS = 260000

# сезонность - летом больше
MONTH_WEIGHTS = {1:0.03,2:0.03,3:0.05,4:0.06,5:0.08,6:0.12,7:0.15,8:0.15,9:0.10,10:0.08,11:0.07,12:0.08}

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

cur.execute("SELECT id FROM client")
clients = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id, description FROM booking_status")
statuses = cur.fetchall()
status_ids = [s[0] for s in statuses]

# веса статусов - большинство подтверждены или выполнены
status_weights = []
for _, desc in statuses:
    if desc in ['Confirmed', 'Completed']:
        status_weights.append(0.35)
    elif desc == 'Pending':
        status_weights.append(0.15)
    elif desc == 'Paid':
        status_weights.append(0.10)
    elif desc == 'Cancelled':
        status_weights.append(0.03)
    else:
        status_weights.append(0.01)
status_weights = np.array(status_weights) / sum(status_weights)

# часы бронирования - днем чаще
hour_weights = [0.02]*24
for h in range(9,21): hour_weights[h] = 0.06
hour_weights = np.array(hour_weights) / sum(hour_weights)

def get_booking_date():
    month = np.random.choice(list(MONTH_WEIGHTS.keys()), p=list(MONTH_WEIGHTS.values()))
    if month in [1,3,5,7,8,10,12]: day = random.randint(1,31)
    elif month in [4,6,9,11]: day = random.randint(1,30)
    else: day = random.randint(1,28)
    
    hour = np.random.choice(24, p=hour_weights)
    return datetime(2024, month, day, hour, random.randint(0,59), random.randint(0,59))

def get_cost():
    # логнормальное - много дешевых, есть дорогие
    cost = int(np.random.lognormal(mean=10, sigma=1.0))
    cost = max(3000, min(150000, cost))
    return round(cost/100)*100

data = []
used = set()

for i in range(NUM_BOOKINGS):
    if i % 10000 == 0: print(f"{i} бронирований...")
    
    client = random.choice(clients)
    date = get_booking_date()

    key = (client, date)
    while key in used:
        date = date + timedelta(seconds=1)
        key = (client, date)
    used.add(key)
    
    status = int(np.random.choice(status_ids, p=status_weights))
    data.append((client, date, get_cost(), status))

batch_size = 10000
for i in range(0, len(data), batch_size):
    execute_values(cur,
        "INSERT INTO booking (client_id, booking_date, total_cost, status_id) VALUES %s ON CONFLICT (client_id, booking_date) DO NOTHING",
        data[i:i+batch_size], page_size=1000)
    conn.commit()

cur.close()
conn.close()