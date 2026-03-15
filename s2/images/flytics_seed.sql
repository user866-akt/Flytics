TRUNCATE public.booking_status CASCADE;
TRUNCATE public.flight_status CASCADE;
TRUNCATE public.fare_class CASCADE;
TRUNCATE public.payment_method CASCADE;
TRUNCATE public.payment_status CASCADE;
TRUNCATE public.city CASCADE;
TRUNCATE public.airline CASCADE;

ALTER SEQUENCE public.booking_status_id_seq RESTART WITH 1;
ALTER SEQUENCE public.flight_status_id_seq RESTART WITH 1;
ALTER SEQUENCE public.fare_class_id_seq RESTART WITH 1;
ALTER SEQUENCE public.payment_method_id_seq RESTART WITH 1;
ALTER SEQUENCE public.payment_status_id_seq RESTART WITH 1;
ALTER SEQUENCE public.city_id_seq RESTART WITH 1;

INSERT INTO public.booking_status (description) VALUES 
    ('Новое'),
    ('Подтверждено'),
    ('Оплачено'),
    ('Отменено'),
    ('Завершено')
ON CONFLICT (description) DO NOTHING;

INSERT INTO public.flight_status (description) VALUES 
    ('По расписанию'),
    ('Задерживается'),
    ('Отменен'),
    ('Вылетел'),
    ('Прибыл')
ON CONFLICT (description) DO NOTHING;

INSERT INTO public.fare_class (description) VALUES 
    ('Эконом'),
    ('Комфорт'),
    ('Бизнес'),
    ('Первый')
ON CONFLICT (description) DO NOTHING;

INSERT INTO public.payment_method (name) VALUES 
    ('Банковская карта'),
    ('Наличные'),
    ('Электронные деньги'),
    ('Банковский перевод')
ON CONFLICT (name) DO NOTHING;

INSERT INTO public.payment_status (description) VALUES 
    ('Ожидает'),
    ('Выполнен'),
    ('Отменен'),
    ('Возврат')
ON CONFLICT (description) DO NOTHING;

INSERT INTO public.city (name)
SELECT name
FROM (VALUES 
    ('Москва'),
    ('Санкт-Петербург'),
    ('Казань'),
    ('Новосибирск'),
    ('Екатеринбург'),
    ('Сидней'),
    ('Мельбурн'),
    ('Перт'),
    ('Брисбен'),
    ('Аделаида'),
    ('Лондон'),
    ('Париж'),
    ('Берлин'),
    ('Рим'),
    ('Мадрид')
) AS new_cities(name)
WHERE NOT EXISTS (
    SELECT 1 FROM public.city c WHERE c.name = new_cities.name
);

INSERT INTO public.airline (iata_code, name) VALUES 
    ('SU', 'Аэрофлот'),
    ('S7', 'S7 Airlines'),
    ('UT', 'ЮТэйр'),
    ('U6', 'Уральские авиалинии'),
    ('DP', 'Победа'),
    ('N4', 'Nordwind Airlines'),
    ('FZ', 'Flydubai'),
    ('EK', 'Emirates'),
    ('TK', 'Turkish Airlines'),
    ('LH', 'Lufthansa')
ON CONFLICT (iata_code) DO UPDATE SET 
    name = EXCLUDED.name;

SELECT 'booking_status' as table_name, COUNT(*) as rows FROM public.booking_status
UNION ALL
SELECT 'flight_status', COUNT(*) FROM public.flight_status
UNION ALL
SELECT 'fare_class', COUNT(*) FROM public.fare_class
UNION ALL
SELECT 'payment_method', COUNT(*) FROM public.payment_method
UNION ALL
SELECT 'payment_status', COUNT(*) FROM public.payment_status
UNION ALL
SELECT 'city', COUNT(*) FROM public.city
UNION ALL
SELECT 'airline', COUNT(*) FROM public.airline
ORDER BY table_name;

SELECT 'Дубликаты в booking_status:' as check, description, COUNT(*) 
FROM public.booking_status 
GROUP BY description 
HAVING COUNT(*) > 1;

SELECT 'Дубликаты в airline:' as check, iata_code, COUNT(*) 
FROM public.airline 
GROUP BY iata_code 
HAVING COUNT(*) > 1;