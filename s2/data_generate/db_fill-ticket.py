import psycopg2
from psycopg2.extras import execute_values
import random

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

NUM_TICKETS = 260000

def seat():
    return f"{random.randint(1,40)}{random.choice(['A','B','C','D','E','F'])}"

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

cur.execute("SELECT id FROM booking ORDER BY id")
bookings = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM passenger")
passengers = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id, flight_id FROM fare")
fares = cur.fetchall()
# группируем тарифы по рейсам
fares_by_flight = {}
for fare_id, flight_id in fares:
    fares_by_flight.setdefault(flight_id, []).append(fare_id)

flights = list(fares_by_flight.keys())
print(f"рейсов с тарифами: {len(flights)}")

# сколько билетов на бронь (1-2 обычно, реже 3-4)
tickets_per_booking = [1,2,3,4]
weights = [0.6, 0.3, 0.07, 0.03]

data = []
seat_tracker = {}  # места на рейс
needed_bookings = int(NUM_TICKETS / 1.5)

for booking_id in bookings[:needed_bookings]:
    if len(data) >= NUM_TICKETS:
        break
    
    num = random.choices(tickets_per_booking, weights)[0]
    for _ in range(num):
        if len(data) >= NUM_TICKETS:
            break
        
        flight = random.choice(flights)
        fare = random.choice(fares_by_flight[flight])
        passenger = random.choice(passengers)
        
        # уникальное место на рейс
        if flight not in seat_tracker:
            seat_tracker[flight] = set()
        
        for _ in range(50):  # 50 попыток найти место
            s = seat()
            if s not in seat_tracker[flight]:
                seat_tracker[flight].add(s)
                data.append((s, booking_id, passenger, fare, flight))
                break

if data:
    execute_values(cur,
        "INSERT INTO ticket (seat_number, booking_id, passenger_id, fare_id, flight_id) VALUES %s ON CONFLICT (seat_number, flight_id) DO NOTHING",
        data, page_size=1000)
    conn.commit()

cur.close()
conn.close()