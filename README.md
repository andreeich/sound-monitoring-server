# Sound Monitoring Server

Це серверна частина системи моніторингу звукового забруднення, розроблена для обробки даних від первинних пристроїв (телефонів із веб-додатком), аналізу звукових сигналів, збереження інформації та прогнозування руху джерел звуку. Система побудована з використанням **Python**, **FastAPI**, **MQTT** та **MongoDB**, а для розгортання використовується **Docker**.

## Особливості
- Приймання повідомлень від первинних пристроїв через MQTT (протокол із QoS 1).
- Збереження даних про сповіщення, сенсори та відстеження в MongoDB.
- Аналіз звукових сигналів, включаючи категоризацію та розрахунок інтенсивності.
- Прогнозування траєкторії руху джерел звуку на основі географічних координат.
- REST API для доступу до даних (сповіщення, сенсори, відстеження).
- Контейнеризація за допомогою Docker для легкого розгортання.

## Технології
- **FastAPI**: Для створення REST API.
- **Paho-MQTT**: Для взаємодії з MQTT-брокером.
- **MongoDB**: Для зберігання даних.
- **Docker**: Для контейнеризації сервера, MQTT-брокера та бази даних.
- **Python 3.11**: Основна мова програмування.

## Вимоги
- Docker та Docker Compose
- Python 3.11 (якщо запускаєте без Docker)
- Доступ до мережі для MQTT-брокера та MongoDB

## Структура проєкту

```
sound-monitoring-server/
├── src/
│   ├── api/
│   │   └── main.py              # Основний файл FastAPI
│   ├── services/
│   │   ├── mqtt_service.py      # Логіка роботи з MQTT
│   │   └── analysis_service.py  # Аналіз і прогнозування
│   ├── models/
│   │   └── alert.py             # Моделі даних (Pydantic)
│   ├── config/
│   │   └── database.py          # Налаштування підключення до MongoDB
├── requirements.txt              # Залежності Python
├── Dockerfile                   # Конфігурація Docker для сервера
├── docker-compose.yml           # Конфігурація Docker Compose
├── mosquitto.conf               # Конфігурація MQTT-брокера
├── .env                         # Змінні оточення
└── README.md                    # Цей файл
```

## Встановлення

1. **Клонуйте репозиторій**:
   ```bash
   git clone <repository-url>
   cd sound-monitoring-server
   ```
2. Створіть файл .env у корені проєкту:
```env
MONGODB_URL=mongodb://mongo:27017/
MQTT_BROKER=mqtt://mosquitto:1883
```
3. Переконайтеся, що Docker і Docker Compose встановлені:
```bash
docker --version
docker-compose --version
```

## Запуск
1. Запустіть систему за допомогою Docker Compose:
```bash
docker-compose up --build
```
2. Доступ до сервісів:
  - FastAPI: http://localhost:8000/docs (Swagger UI для тестування API)
  - MongoDB: mongodb://localhost:27017
  - Mosquitto (MQTT): mqtt://localhost:1883
3. Зупинка системи:
```bash
docker-compose down
```

## Використання

### API Ендпоінти
- GET /alerts: Отримати список усіх сповіщень.
- GET /sensors: Отримати список усіх сенсорів.
- GET /trackings: Отримати дані про відстеження джерел звуку.
- POST /sensors/register: Зареєструвати новий сенсор. Приклад тіла запиту:
```json
{
  "sensor_id": "sensor_1",
  "location": {
    "latitude": 50.45,
    "longitude": 30.52
  }
}
```

### MQTT Топіки
- Вхідні повідомлення: sound_monitoring/sensor/{sensor_id}/alert
  - Формат повідомлення (JSON):
```json
{
  "message_id": "msg_1",
  "sensor_id": "sensor_1",
  "location": {
    "latitude": 50.45,
    "longitude": 30.52
  },
  "timestamp": 1697059200000,
  "sound_type": "drone",
  "confidence": 90.5
}
```
- Підтвердження: sound_monitoring/sensor/{sensor_id}/ack
  - Формат відповіді:
```json
{
  "message_id": "msg_1",
  "status": "received"
}
```

## Тестування
Відправка тестового MQTT-повідомлення:
- Використовуйте mosquitto_pub:
```bash
mosquitto_pub -h localhost -t "sound_monitoring/sensor/sensor_1/alert" -m '{"message_id": "msg_1", "sensor_id": "sensor_1", "location": {"latitude": 50.45, "longitude": 30.52}, "timestamp": 1697059200000, "sound_type": "drone", "confidence": 90.5}'
```
- Перевірка API:
  - Список сповіщень: curl http://localhost:8000/alerts
  - Список сенсорів: curl http://localhost:8000/sensors
  - Дані трекінгу: curl http://localhost:8000/trackings
- Перевірка бази даних:
  - Підключіться до MongoDB (наприклад, через MongoDB Compass) і перевірте колекції alerts, sensors, trackings.

## Структура бази даних

### Колекції MongoDB
- alerts:
  - Схема:
```json
{
  "message_id": "string",
  "sensor_id": "string",
  "location": { "latitude": float, "longitude": float },
  "timestamp": int,
  "sound_type": "string",
  "confidence": float,
  "first_timestamp": int,
  "processed_at": int,
  "category": "string",
  "intensity": float
}
sensors:
Схема:
json
{
  "sensor_id": "string",
  "location": { "latitude": float, "longitude": float },
  "last_seen": int,
  "status": "string"
}
```
- trackings:
  - Схема:
```json
{
  "sound_type": "string",
  "locations": [
    { "latitude": float, "longitude": float, "timestamp": int }
  ],
  "speed": float,
  "direction": float,
  "predictions": [
    { "sensor_id": "string", "estimated_arrival_time": int }
  ]
}
```

## Розробка та внесок
- Для локальної розробки без Docker:
```bash
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```
- Внесок:
  - Створюйте pull requests із чітким описом змін.
  - Дотримуйтесь стилю коду PEP 8.

## Вирішення проблем
- Сервер не запускається:
  - Перевірте, чи доступні порти 8000, 1883, 27017.
  - Переконайтеся, що файл .env створено.
- MQTT не працює:
  - Перевірте, чи запущений Mosquitto (docker ps).
  - Перегляньте логи: docker logs sound-monitoring-server-mosquitto-1.
- MongoDB не підключається:
  - Перевірте підключення: docker exec -it sound-monitoring-server-mongo-1 mongosh.

## Ліцензія
Цей проєкт ліцензований за MIT License.
