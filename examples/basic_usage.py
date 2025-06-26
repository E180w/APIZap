#!/usr/bin/env python3
"""Примеры программного использования APIZap."""

from apizap.parser import OpenAPIParser
from apizap.tester import APITester
from apizap.reporter import TestReporter


def example_basic_usage():
    """Базовый пример использования APIZap."""
    print("🚀 Запуск базового примера APIZap")
    
    # 1. Парсинг OpenAPI спецификации
    parser = OpenAPIParser()
    spec = parser.parse("https://httpbin.org/spec.json")
    
    if not spec:
        print("❌ Не удалось загрузить спецификацию")
        return
    
    print(f"✅ Загружена спецификация: {spec.info.title}")
    
    # 2. Получение всех операций
    operations = parser.get_all_operations(spec)
    print(f"📊 Найдено операций: {len(operations)}")
    
    # 3. Тестирование API
    tester = APITester(timeout=10)
    results = tester.test_all_endpoints(spec)
    
    # 4. Генерация отчета
    reporter = TestReporter()
    report = reporter.generate_text_report(results)
    
    print("\n" + "="*60)
    print("📋 ОТЧЕТ О ТЕСТИРОВАНИИ")
    print("="*60)
    print(report)


def example_with_authentication():
    """Пример с аутентификацией."""
    print("🔐 Пример с аутентификацией")
    
    # Конфигурация аутентификации
    auth_config = {
        'type': 'bearer',
        'token': 'your_jwt_token_here',
        'header': 'Authorization'
    }
    
    # Парсинг и тестирование
    parser = OpenAPIParser()
    spec = parser.parse("https://httpbin.org/spec.json")
    
    if spec:
        tester = APITester(timeout=15, auth_config=auth_config)
        results = tester.test_all_endpoints(spec)
        
        # JSON отчет
        reporter = TestReporter()
        json_report = reporter.generate_json_report(results)
        
        print("📄 JSON отчет сгенерирован")
        print("Длина отчета:", len(json_report), "символов")


def example_custom_testing():
    """Пример кастомного тестирования отдельных эндпоинтов."""
    print("🎯 Пример кастомного тестирования")
    
    # Создание тестера
    tester = APITester(timeout=5)
    
    # Простой тест одного эндпоинта
    import requests
    
    try:
        response = requests.get("https://httpbin.org/get", timeout=5)
        print(f"✅ GET /get → {response.status_code}")
        
        response = requests.get("https://httpbin.org/status/404", timeout=5)
        print(f"⚠️  GET /status/404 → {response.status_code}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")


def example_statistics():
    """Пример сбора статистики."""
    print("📈 Пример сбора статистики")
    
    # Симулируем результаты тестов
    mock_results = [
        {'status': 'PASS', 'method': 'GET', 'path': '/users', 'response_time': 120.5},
        {'status': 'PASS', 'method': 'POST', 'path': '/users', 'response_time': 245.8},
        {'status': 'WARN', 'method': 'GET', 'path': '/admin', 'response_time': 89.2},
        {'status': 'FAIL', 'method': 'DELETE', 'path': '/users/1', 'response_time': 0},
    ]
    
    # Генерация статистики
    reporter = TestReporter()
    stats = reporter.generate_summary_stats(mock_results)
    
    print("📊 Статистика:")
    print(f"  Всего тестов: {stats['total']}")
    print(f"  Успешных: {stats['passed']}")
    print(f"  Предупреждений: {stats['warnings']}")
    print(f"  Неудачных: {stats['failed']}")
    print(f"  Процент успеха: {stats['success_rate']}%")


if __name__ == "__main__":
    print("📚 Примеры использования APIZap\n")
    
    try:
        example_basic_usage()
        print("\n" + "-"*60 + "\n")
        
        example_with_authentication()
        print("\n" + "-"*60 + "\n")
        
        example_custom_testing()
        print("\n" + "-"*60 + "\n")
        
        example_statistics()
        
    except KeyboardInterrupt:
        print("\n⏹️  Примеры прерваны пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка в примере: {e}")
    
    print("\n✨ Примеры завершены!") 