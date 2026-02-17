import psycopg2
from psycopg2.extras import execute_values
import random

DB_PARAMS = {
    'dbname': 'flytics', 'user': 'admin', 'password': 'admin_pass',
    'host': 'localhost', 'port': '5433'
}

# 100к клиентов
NUM_CLIENTS = 100000

FIRST_NAMES = ['Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей', 'Анна', 'Мария', 'Елена']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов']
EMAIL_DOMAINS = ['gmail.com', 'yandex.ru', 'mail.ru']

def translit(word):
    m = {'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E','Ж':'Zh','З':'Z',
         'И':'I','Й':'Y','К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R',
         'С':'S','Т':'T','У':'U','Ф':'F','Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh',
         'Щ':'Shch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu','Я':'Ya'}
    return ''.join(m.get(c.upper(), c) for c in word).lower()

def generate_email(first, last):
    first_lat = translit(first)
    last_lat = translit(last)
    name = random.choice([f"{first_lat}.{last_lat}", f"{first_lat}{last_lat}"])
    return f"{name}{random.randint(1,9999)}@{random.choice(EMAIL_DOMAINS)}"

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

data = []
for i in range(NUM_CLIENTS):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    data.append((first, last, generate_email(first, last), 'password123'))
execute_values(cur, 
    "INSERT INTO client (first_name, last_name, email, password_hash) VALUES %s ON CONFLICT (email) DO NOTHING",
    data, page_size=1000)
conn.commit()

cur.execute("SELECT COUNT(*) FROM client")
cur.close()
conn.close()