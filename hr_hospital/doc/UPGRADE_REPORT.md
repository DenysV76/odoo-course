# Звіт про оновлення hr_hospital 19.0.1.0.0 → 19.0.1.3.0

Стан «до» — тег `hr_hospital-block7-before`, стан «після» — тег `hr_hospital-block7-after` (гілка `feature/hr_hospital_block7`).

| Версія | Зміна схеми | Скрипт | Етап |
|---|---|---|---|
| 19.0.1.1.0 | `insurance_number` → `policy_number` | `pre-10-rename-policy-number.py` | pre |
| 19.0.1.2.0 | `policy_number`: Char → Integer, нове поле `policy_note` | `pre-10-normalize-policy-number.py` | pre |
| 19.0.1.3.0 | нове поле `first_visit_date` (Date) | `post-10-fill-first-visit-date.py` | post |

Чому кожен скрипт саме на цьому етапі — у docstring кожного скрипта.

## 1. База «до» і контрольні числа

База `hospital_upgrade`: `hr_hospital` 19.0.1.0.0 з демо + власні записи зі скрипта `doc/seed_before.py` (5 пацієнтів і 6 візитів). Скрипт замість ручного введення — щоб базу можна було відтворити точно.

| Контрольна величина | Значення |
|---|---|
| Пацієнтів | **8** (3 демо + 5 власних) |
| Візитів | **18** (12 демо + 6 власних) |
| Пацієнтів із полісом | **7** |
| Поліс нечислового пацієнта «Upgrade Test 3 (letters)» | **`AB-1234`** |

Поліси навмисно різні: `100200` (цифри), `" 300 400 "` (пробіли), `AB-1234` (літери), `98765432109` (не влазить в integer), `UA-0001-2026`…`UA-0003-2026` (демо), один пацієнт без поліса й без візитів.

Після кожного кроку з правильними скриптами — 8 пацієнтів і 18 візитів, жоден запис не втрачено.

## 2. Навмисні збої

**2.1. Перейменування без скрипта.** Оновлення пройшло «успішно», але в логу є `Deleting … (hr_hospital.field_hr_hospital_patient__insurance_number)`: Odoo прибрав запис про старе поле разом із колонкою. Після оновлення `policy_number` є, але заповнено **0 полісів із 7**. Зі скриптом — 7 із 7, `AB-1234` на місці.

**3.1. Зміна типу без скрипта.** Оновлення впало з помилкою PostgreSQL:

```
psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type integer: "UA-0002-2026"
```

Транзакція відкотилася вся: модуль лишився у 19.0.1.0.0, відкотилося навіть перейменування з кроку 1.1.0 (колонка знову `insurance_number`).

**4. Скрипт заповнення як `pre-`.** Оновлення впало:

```
ERROR: column "first_visit_date" of relation "hr_hospital_patient" does not exist
```

На етапі `pre-` Odoo ще не створив колонку нового поля. Як `post-` скрипт проходить.

## 3. Рішення

- **Нечислові поліси.** Беремо лише цифри; якщо в значенні було щось, крім цифр і пробілів, оригінал копіюється в `policy_note`. Число, більше за 2 147 483 647, обнуляється, а оригінал теж іде в `policy_note`. Нічого не зникає мовчки. Результат: `AB-1234` → `1234` + примітка `AB-1234`; `UA-0002-2026` → `22026` + примітка; `98765432109` → порожньо + примітка; `" 300 400 "` → `300400` без примітки (пробіли — лише форматування).
- **Перший візит** — найраніша фактична дата (`visit_date`) візиту в стані Done; заплановані й скасовані не враховуються. Пацієнт без таких візитів — порожньо. Дата береться з UTC, як вона зберігається. Звірено вручну: «Upgrade Test 1» має візити 2026-05-20 і 2026-03-10 → `2026-03-10`; «Upgrade Test 2» має скасований 2026-01-15 і завершений 2026-04-02 → `2026-04-02`; «Upgrade Test 3» має лише запланований → порожньо.
- **Демо-пацієнти `noupdate="1"`.** Інакше `-u` перезаписав би поліси демо-пацієнтів із XML, і втрату даних у кроці 2.1 частково приховало б.
- **Нумерація.** До блоку 7 у маніфесті вже стояло `19.0.1.1.0`; версію повернуто на `19.0.1.0.0`, щоб кроки збігалися із завданням.
- **Бонус `upgrade-util`** не робився.

## 4. Повторний прогін і пропуск версій

- Друге `-u` на оновленій базі: помилок немає, рядків `Running upgrade` — 0 (встановлена версія вже 19.0.1.3.0, каталоги не потрапляють у проміжок «встановлена < каталог ≤ маніфест»).
- Усі три скрипти викликано вдруге напряму (`migrate(cr, "19.0.1.0.0")`) на вже оновленій базі: без помилок, дані ті самі. Захист: перейменування — лише якщо стара колонка є, а нової немає; нормалізація — лише поки колонка `varchar`; заповнення — ідемпотентний `UPDATE`.
- Оновлення з `before.dump` одразу до 19.0.1.3.0 виконало всі три скрипти по черзі, результат збігся з покроковим (порівняно `diff` вивід `check_upgrade.sh`).
- Свіже встановлення 19.0.1.3.0 з демо: скрипти не запускаються, 0 WARNING/ERROR, тести 11/11.

⚠️ В Odoo 19 рядок логу — `Running upgrade`, а не `Running migration`:

```
module hr_hospital: Running upgrade [>19.0.1.1.0] pre-10-rename-policy-number
module hr_hospital: Running upgrade [>19.0.1.2.0] pre-10-normalize-policy-number
module hr_hospital: Running upgrade [19.0.1.3.0>] post-10-fill-first-visit-date
```

## 5. Як відтворити

З каталогу Odoo, `config/odoo.conf` вказує на репозиторій в `addons_path`; користувач БД `odoo`, пароль — у `PGPASSWORD`.

```bash
# 1. База «до»
git checkout hr_hospital-block7-before
createdb -U odoo -h localhost hospital_upgrade
./odoo-bin -c config/odoo.conf -d hospital_upgrade -i hr_hospital --with-demo --stop-after-init
./odoo-bin shell -c config/odoo.conf -d hospital_upgrade < <repo>/hr_hospital/doc/seed_before.py
pg_dump -U odoo -h localhost -Fc hospital_upgrade > before.dump
<repo>/hr_hospital/doc/check_upgrade.sh hospital_upgrade      # контрольні числа

# Відновлення з дампа (перед кожним експериментом)
dropdb -U odoo -h localhost hospital_upgrade && createdb -U odoo -h localhost hospital_upgrade \
  && pg_restore -U odoo -h localhost -d hospital_upgrade --no-owner before.dump

# 2-4. Оновлення (покроково: checkout комітів 19.0.1.1.0, 19.0.1.2.0, потім тег after;
#      або одразу тег after)
git checkout hr_hospital-block7-after
./odoo-bin -c config/odoo.conf -d hospital_upgrade -u hr_hospital --stop-after-init --logfile=upgrade.log
grep "Running upgrade" upgrade.log                            # має бути 3 рядки
<repo>/hr_hospital/doc/check_upgrade.sh hospital_upgrade

# 5. Повторний прогін
./odoo-bin -c config/odoo.conf -d hospital_upgrade -u hr_hospital --stop-after-init --logfile=rerun.log
grep -c "Running upgrade" rerun.log                           # 0

# Проблемні поліси до кроку 1.2.0
psql -U odoo -h localhost -d hospital_upgrade \
  -c "select id, policy_number from hr_hospital_patient where policy_number !~ '^[0-9]+$'"
```

Навмисні збої: 2.1 — на коміті 19.0.1.1.0 видалити `migrations/19.0.1.1.0`; 3.1 — на коміті 19.0.1.2.0 видалити `migrations/19.0.1.2.0`; 4 — перейменувати `post-10-fill-first-visit-date.py` на `pre-10-…`. Кожен раз — відновити базу з дампа й запустити `-u`.
