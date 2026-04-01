Задание 1.
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, amount, created_at
FROM exam_events
WHERE user_id = 4242
  AND created_at >= TIMESTAMP '2025-03-10 00:00:00'
  AND created_at < TIMESTAMP '2025-03-11 00:00:00';
```
Seq scan (потому что нет подходящих индексов), cost=0..1617.07, execution time=10 ms
idx_exam_events_status и idx_exam_events_amount_hash не помогают потому что они работают по status и по amount соответственно, а поиск по created_at и user_id.
```sql
CREATE INDEX idx_exam_events_user_id_hash ON exam_events USING hash (user_id);
CREATE INDEX idx_exam_events_created_at_btree ON exam_events USING btree (created_at);
```
Bitmap Heap Scan on exam_events + Bitmap Index Scan on idx_exam_events_user_id_hash + Bitmap Index Scan on idx_exam_events_created_at_btree
cost=19.60..23.62, execution time=0.571
Индекс по хэшу на user_id (т.к. используем =) и btree для дат (т.к. сравниваем)
После создания индекса нужно выполнять ANALYZE для того чтобы планировщик пересчитал все и выбирал оптимальный вариант поиска.

Задание 2.
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT u.id, u.country, o.amount, o.created_at
FROM exam_users u
JOIN exam_orders o ON o.user_id = u.id
WHERE u.country = 'JP'
  AND o.created_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND o.created_at < TIMESTAMP '2025-03-08 00:00:00';
```
Hash Join (поскольку join по =), cost=559.81..1702.14, execution time=7.779
Индекс idx_exam_users_name не помогает потому что мы не ищем по имени.
Индекс idx_exam_orders_created_at для created_at ускоряет поиск по дате, но используется seq scan для поиска u.country = 'JP'.
Чтобы ускорить нужен хэш индекс по стране
```sql
CREATE INDEX idx_exam_users_country_hash ON exam_users USING hash (country);
```
Теперь idx_exam_users_country_hash ускоряет поиск по стране. cost=366.06..1508.39, execution time=3.514 - есть незначительный прирост производительности.
Shared hit - значит используется буфер, планировщик использует его.

Задание 3.
```sql
SELECT xmin, xmax, ctid, id, title, qty
FROM exam_mvcc_items
ORDER BY id;
```
xmin=740 на всех 3 записях, xmax=0 так же везде и ctid=(0, 1), (0, 2), (0, 3)
```sql
UPDATE exam_mvcc_items
SET qty = qty + 5
WHERE id = 1;
```
Теперь у 1 записи xmin=751, xmax без изменений, ctid=(0, 4) у измененной записи.
UPDATE не является простым "перезаписыванием" строки потому что для того чтобы не было блокирования между чтением и записью это DELETE+INSERT.
```sql
DELETE FROM exam_mvcc_items
WHERE id = 2;
```
После DELETE информация об этой записи удалена. Как правило в xmax записывается id транзакции, которая удалила запись.
VACUUM - очищает мертвые кортежи, но не отдает память в ОС.
autovacuum - фоновый процесс, который использует ANALYSE
VACUUM FULL - полная очистка и перекомпоновка бд, высвобождает память для ОС, требует блокировки.

Задание 5.
```sql
create table exam_measurements (
	city_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    peaktemp INTEGER,
    unitsales INTEGER
) partition by range (log_date);
CREATE TABLE booking_2025_01 PARTITION OF exam_measurements
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE booking_2025_02 PARTITION OF exam_measurements
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE booking_2025_03 PARTITION OF exam_measurements
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE exam_measurements_other PARTITION OF exam_measurements DEFAULT;
```
```sql
INSERT INTO exam_measurements
SELECT * FROM exam_measurements_src;
```
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT city_id, log_date, unitsales
FROM exam_measurements
WHERE log_date >= DATE '2025-02-01'
  AND log_date < DATE '2025-03-01';
```
Используется partition pruning тк поиск по диапазону 1 партиции
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT city_id, log_date, unitsales
FROM exam_measurements
WHERE city_id = 10;
```
Используются все партиции, потому что не ищем по диапазону разделения, а по другому полю.
DEFAULT для тех записей которые не входят в указанные диапазоны.
