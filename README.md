# APIZap 🚀

**Автоматический генератор тестов для API на основе OpenAPI спецификаций**

APIZap - это простой в использовании инструмент командной строки, который автоматически анализирует OpenAPI/Swagger спецификации и генерирует тесты для всех доступных эндпоинтов вашего API.

## ✨ Основные возможности

- 🔍 **Автоматический парсинг** OpenAPI 3.0 спецификаций
- 🧪 **Генерация тестов** для всех HTTP методов (GET, POST, PUT, DELETE, и др.)
- 🔐 **Поддержка аутентификации** (Bearer токены, API ключи)
- 📊 **Детальные отчеты** в текстовом и JSON формате
- ⚡ **Простота использования** - один CLI команда для запуска всех тестов
- 🛡️ **Обработка ошибок** с понятными сообщениями
- 📋 **Минимальные зависимости** - только необходимые пакеты

## 📦 Установка

### Вариант 1: Установка через pip (рекомендуется)

```bash
pip install apizap
```

### Вариант 2: Установка из исходного кода

```bash
git clone https://github.com/apizap/apizap.git
cd apizap
pip install -e .
```

## 🏃‍♂️ Быстрый старт

### Базовое использование

```bash
# Тестирование публичного API
apizap --url https://petstore.swagger.io/v2/swagger.json

# С аутентификацией Bearer токеном
apizap --url https://api.example.com/openapi.json --auth-type bearer --auth-token YOUR_TOKEN

# Сохранение результатов в файл
apizap --url https://api.example.com/swagger.json --output json --output-file results.json
```

### Примеры команд

```bash
# Простое тестирование без аутентификации
apizap -u https://httpbin.org/spec.json

# С API ключом в заголовке
apizap -u https://api.example.com/openapi.json -a apikey -t YOUR_API_KEY -h X-API-Key

# Подробный вывод с таймаутом 60 секунд
apizap -u https://api.example.com/swagger.json -v --timeout 60

# JSON отчет с сохранением в файл
apizap -u https://api.example.com/openapi.json -o json -f test_results.json
```

## 🔧 Параметры командной строки

| Параметр | Короткий | Описание | Пример |
|----------|----------|-----------|--------|
| `--url` | `-u` | URL OpenAPI спецификации (обязательный) | `-u https://api.example.com/swagger.json` |
| `--auth-type` | `-a` | Тип аутентификации: `bearer`, `apikey`, `none` | `-a bearer` |
| `--auth-token` | `-t` | Токен или API ключ | `-t your_secret_token` |
| `--auth-header` | `-h` | Заголовок для API ключа | `-h X-API-Key` |
| `--output` | `-o` | Формат вывода: `text`, `json` | `-o json` |
| `--output-file` | `-f` | Файл для сохранения результатов | `-f results.json` |
| `--timeout` | `-to` | Таймаут запросов в секундах | `--timeout 30` |
| `--verbose` | `-v` | Подробный вывод | `-v` |
| `--version` | | Показать версию | `--version` |
| `--help` | | Показать справку | `--help` |

## 📊 Форматы вывода

### Текстовый отчет (по умолчанию)

```
📊 СВОДНАЯ СТАТИСТИКА
==================================================
📈 Всего тестов: 15
✅ Успешных: 12 (80.0%)
⚠️  Предупреждений: 2 (13.3%)
❌ Неудачных: 1 (6.7%)
⏱️  Общее время: 2547.83ms
📊 Среднее время: 169.86ms

📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ
==================================================

✅ УСПЕШНЫЕ ТЕСТЫ (12)
----------------------------------------
  GET /api/users → 200 (145.23ms)
    📝 Get all users
  
  POST /api/users → 201 (234.56ms)
    📝 Create new user
```

### JSON отчет

```json
{
  "summary": {
    "total_tests": 15,
    "passed": 12,
    "warnings": 2,
    "failed": 1,
    "success_rate": 80.0,
    "total_time_ms": 2547.83,
    "average_time_ms": 169.86
  },
  "tests": [
    {
      "operation_id": "getUsers",
      "method": "GET",
      "path": "/api/users",
      "summary": "Get all users",
      "status": "PASS",
      "status_code": 200,
      "response_time_ms": 145.23,
      "response_size_bytes": 1024,
      "timestamp": "2024-01-15T10:30:45.123456"
    }
  ]
}
```

## 🆘 Пошаговая инструкция для новичков

### Шаг 1: Установка Python

#### Windows:
1. Перейдите на https://python.org/downloads/
2. Скачайте последнюю версию Python (3.7+)
3. Запустите установщик
4. ✅ **ВАЖНО**: Отметьте "Add Python to PATH" во время установки
5. Нажмите "Install Now"

#### macOS:
```bash
# Установка через Homebrew (рекомендуется)
brew install python

# Или скачайте с python.org
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Шаг 2: Проверка установки Python

Откройте терминал (командную строку) и выполните:

```bash
python --version
# или
python3 --version
```

Должна отобразиться версия Python 3.7 или выше.

### Шаг 3: Установка APIZap

```bash
pip install apizap
# или
pip3 install apizap
```

### Шаг 4: Проверка установки APIZap

```bash
apizap --version
```

### Шаг 5: Первый тест

Попробуйте протестировать публичный API:

```bash
apizap --url https://httpbin.org/spec.json
```

### Шаг 6: Тестирование вашего API

```bash
# Замените URL на ваш OpenAPI endpoint
apizap --url https://your-api.com/swagger.json

# С аутентификацией
apizap --url https://your-api.com/openapi.json --auth-type bearer --auth-token YOUR_TOKEN
```

## 🛠️ Поиск OpenAPI спецификации

### Типичные пути к OpenAPI спецификации:

- `https://api.example.com/swagger.json`
- `https://api.example.com/openapi.json`
- `https://api.example.com/v1/swagger.json`
- `https://api.example.com/docs/swagger.json`
- `https://api.example.com/api-docs`

### Как найти OpenAPI спецификацию:

1. **Документация API** - проверьте документацию вашего API
2. **Swagger UI** - если есть интерфейс Swagger, URL спецификации обычно в адресной строке
3. **Разработчики** - спросите у команды разработки API
4. **Типичные эндпоинты** - попробуйте стандартные пути выше

## 🔐 Настройка аутентификации

### Bearer токен (JWT)

```bash
apizap --url https://api.example.com/openapi.json \
       --auth-type bearer \
       --auth-token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API ключ в заголовке

```bash
apizap --url https://api.example.com/openapi.json \
       --auth-type apikey \
       --auth-token your_api_key_here \
       --auth-header X-API-Key
```

### API ключ в Authorization заголовке

```bash
apizap --url https://api.example.com/openapi.json \
       --auth-type apikey \
       --auth-token your_api_key_here
```

## 📁 Сохранение результатов

### Сохранение в JSON файл

```bash
apizap --url https://api.example.com/openapi.json \
       --output json \
       --output-file my_api_test_results.json
```

### Сохранение текстового отчета

```bash
apizap --url https://api.example.com/openapi.json \
       --output text \
       --output-file my_api_test_results.txt
```

## 🚨 Решение проблем

### Ошибка: "command not found: apizap"

**Решение:**
```bash
# Попробуйте:
python -m apizap.cli --help

# Или переустановите:
pip uninstall apizap
pip install apizap
```

### Ошибка: "SSL certificate verify failed"

**Решение:**
```bash
# Обновите pip и сертификаты:
pip install --upgrade pip
pip install --upgrade certifi
```

### Ошибка: "Permission denied"

**Решение (Linux/macOS):**
```bash
# Установка для пользователя:
pip install --user apizap

# Или с sudo (не рекомендуется):
sudo pip install apizap
```

### Ошибка: "Timeout"

**Решение:**
```bash
# Увеличьте таймаут:
apizap --url https://slow-api.com/openapi.json --timeout 60
```

## 🎯 Примеры использования

### Тестирование REST API интернет-магазина

```bash
apizap --url https://api.shop.com/v1/openapi.json \
       --auth-type bearer \
       --auth-token $SHOP_API_TOKEN \
       --output json \
       --output-file shop_api_tests.json
```

### Тестирование микросервиса с API ключом

```bash
apizap --url https://microservice.company.com/swagger.json \
       --auth-type apikey \
       --auth-token $API_KEY \
       --auth-header X-API-KEY \
       --verbose
```

### Автоматизация в CI/CD

```bash
#!/bin/bash
# Скрипт для CI/CD

apizap --url $API_SPEC_URL \
       --auth-type bearer \
       --auth-token $CI_API_TOKEN \
       --output json \
       --output-file test_results_$(date +%Y%m%d_%H%M%S).json

# Проверка результата
if [ $? -eq 0 ]; then
    echo "✅ API тесты прошли успешно"
else
    echo "❌ Обнаружены проблемы в API"
    exit 1
fi
```

## 🤝 Вклад в развитие

Приветствуем ваш вклад! Пожалуйста:

1. Сделайте Fork репозитория
2. Создайте ветку для функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект лицензируется под MIT License - см. файл [LICENSE](LICENSE) для подробностей.

## 📞 Поддержка

- 🐛 **Баги**: [GitHub Issues](https://github.com/E180w/APIZap/issues)

## 🏆 Альтернативы

Если APIZap не подходит для ваших нужд, рассмотрите:

- **Postman** - GUI инструмент для тестирования API
- **Insomnia** - Еще один GUI клиент
- **curl** - Командная строка для HTTP запросов
- **HTTPie** - Человеко-дружественный HTTP клиент
- **Newman** - Командная строка для Postman коллекций

---

**APIZap** - делает тестирование API простым и автоматическим! 🚀 
