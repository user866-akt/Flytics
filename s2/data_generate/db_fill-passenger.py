import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime, timedelta

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

NUM_PASSENGERS = 200000

FIRST_NAMES = ['Александр', 'Дмитрий', 'Максим', 'Сергей', 'Анна', 'Мария', 'Елена']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов']

def generate_passport():
    return f"{random.randint(10,99)}{random.randint(10,99)}", f"{random.randint(100000,999999)}"

def generate_birthdate():
    # от 18 до 80 лет
    days = random.randint(18*365, 80*365)
    return datetime.now() - timedelta(days=days)

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

data = []
used_passports = set()

for i in range(NUM_PASSENGERS):
    if i % 10000 == 0: print(f"{i} пассажиров...")
    
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    birth = generate_birthdate().date()
    
    while True:
        series, number = generate_passport()
        key = f"{series}{number}"
        if key not in used_passports:
            used_passports.add(key)
            break
    
    data.append((first, last, birth, series, number))

execute_values(cur,
    "INSERT INTO passenger (first_name, last_name, birthdate, passport_series, passport_number) VALUES %s ON CONFLICT (passport_series, passport_number) DO NOTHING",
    data, page_size=1000)
conn.commit()

cur.close()
conn.close()