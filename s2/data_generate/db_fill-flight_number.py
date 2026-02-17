import psycopg2
from psycopg2.extras import execute_values
import random

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

# берем аэропорты из базы
cur.execute("SELECT iata_code FROM airport")
airports = [row[0] for row in cur.fetchall()]

airlines = ['SU', 'S7', 'UT', 'U6', 'DP', 'N4', 'TK', 'EK', 'QR']
hubs = ['SVO', 'DME', 'VKO', 'LED', 'OVB', 'KZN', 'AER']  # основные хабы

data = []
used = set()
target = random.randint(200, 300)  # 200-300 рейсов

while len(data) < target:
    airline = random.choice(airlines)
    num = f"{airline}{random.randint(100, 999)}"
    if num in used:
        continue
    
    # чаще из хабов, но бывает и из других
    if random.random() < 0.7 and hubs:
        dep = random.choice([h for h in hubs if h in airports])
    else:
        dep = random.choice(airports)
    
    arr = random.choice([a for a in airports if a != dep])
    
    used.add(num)
    data.append((num, dep, arr))
execute_values(cur,
    "INSERT INTO flight_number (number, departure_airport_id, arrival_airport_id) VALUES %s ON CONFLICT (number) DO NOTHING",
    data, page_size=1000)
conn.commit()
cur.close()
conn.close()