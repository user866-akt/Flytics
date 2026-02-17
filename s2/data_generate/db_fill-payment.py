import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime, timedelta

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

NUM_PAYMENTS = 250000

def payment_date(booking_date):
    # платеж обычно в течение пары дней после брони
    delay = random.choices([0,1,2,6,12,24,48,72], [0.1,0.2,0.2,0.15,0.1,0.1,0.05,0.05])[0]
    return booking_date + timedelta(hours=delay, minutes=random.randint(0,59))

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

# берем брони и их статусы
cur.execute("""
    SELECT b.id, b.booking_date, bs.description 
    FROM booking b
    JOIN booking_status bs ON b.status_id = bs.id
""")
bookings = cur.fetchall()

cur.execute("SELECT id FROM payment_method")
method_ids = [row[0] for row in cur.fetchall()]
# карты - 65%, остальное
method_weights = [0.65, 0.10, 0.08, 0.05, 0.03, 0.03, 0.02, 0.02, 0.02]

cur.execute("SELECT id, description FROM payment_status")
statuses = cur.fetchall()
status_ids = [s[0] for s in statuses]
status_desc = {s[0]:s[1] for s in statuses}

# какие брони уже оплачены
cur.execute("SELECT booking_id FROM payment")
paid = set(row[0] for row in cur.fetchall())

data = []
for booking_id, booking_date, booking_status in bookings:
    if len(data) >= NUM_PAYMENTS:
        break
    if booking_id in paid:
        continue
    if random.random() > 0.85:  # 15% без оплаты
        continue
    
    method = random.choices(method_ids, weights=method_weights)[0]
    
    # статус платежа зависит от статуса брони
    if booking_status in ['Cancelled', 'Expired']:
        w = [0,0,0,0.3,0.5,0.2]
    elif booking_status == 'Pending':
        w = [0.4,0.3,0.2,0.05,0,0.05]
    elif booking_status in ['Paid', 'Completed']:
        w = [0,0,0.95,0,0.05,0]
    else:
        w = [0.10,0.05,0.70,0.08,0.05,0.02]
    
    status = random.choices(status_ids, weights=[x/sum(w) for x in w])[0]
    data.append((booking_id, method, status, payment_date(booking_date)))
if data:
    execute_values(cur,
        "INSERT INTO payment (booking_id, payment_method_id, payment_status_id, payment_date) VALUES %s ON CONFLICT (booking_id, payment_date) DO NOTHING",
        data, page_size=1000)
    conn.commit()

cur.close()
conn.close()