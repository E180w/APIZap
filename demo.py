#!/usr/bin/env python3
"""Демонстрационный скрипт для APIZap."""

import json
import subprocess
import sys
from pathlib import Path

def print_header():
    """Печатает заголовок программы."""
    print("="*60)
    print("🚀 ДЕМОНСТРАЦИЯ APIZap - Автоматический тестер API")
    print("="*60)
    print()

def print_menu():
    """Печатает меню опций."""
    print("📋 МЕНЮ ДЕМОНСТРАЦИИ:")
    print("1. 🧪 Простое тестирование Swagger Petstore (текстовый отчет)")
    print("2. 📊 Тестирование с JSON отчетом")
    print("3. 🔍 Подробный режим с логированием")
    print("4. 📄 Показать готовый JSON отчет")
    print("5. ❓ Показать справку APIZap")
    print("6. 📖 Информация о проекте")
    print("0. 🚪 Выход")
    print()

def run_basic_test():
    """Запускает базовое тестирование."""
    print("🧪 Запуск базового тестирования Swagger Petstore...")
    print("Команда: apizap --url https://petstore.swagger.io/v2/swagger.json")
    print("-" * 60)
    
    try:
        result = subprocess.run([
            "apizap", 
            "--url", "https://petstore.swagger.io/v2/swagger.json"
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Предупреждения/ошибки:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения команды")
    except FileNotFoundError:
        print("❌ APIZap не найден. Убедитесь, что он установлен: pip install -e .")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

def run_json_test():
    """Запускает тестирование с JSON выводом."""
    print("📊 Запуск тестирования с JSON отчетом...")
    print("Команда: apizap --url https://petstore.swagger.io/v2/swagger.json --output json --output-file demo_results.json")
    print("-" * 60)
    
    try:
        result = subprocess.run([
            "apizap", 
            "--url", "https://petstore.swagger.io/v2/swagger.json",
            "--output", "json",
            "--output-file", "demo_results.json"
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Логи:")
            print(result.stderr)
            
        # Показать начало JSON файла
        json_file = Path("demo_results.json")
        if json_file.exists():
            print("\n📄 Содержимое JSON отчета (первые 20 строк):")
            with open(json_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:20]):
                    print(f"{i+1:2d}: {line.rstrip()}")
                if len(lines) > 20:
                    print(f"... и еще {len(lines) - 20} строк")
                    
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения команды")
    except FileNotFoundError:
        print("❌ APIZap не найден. Убедитесь, что он установлен: pip install -e .")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

def run_verbose_test():
    """Запускает подробное тестирование."""
    print("🔍 Запуск тестирования в подробном режиме...")
    print("Команда: apizap --url https://petstore.swagger.io/v2/swagger.json --verbose")
    print("-" * 60)
    
    try:
        result = subprocess.run([
            "apizap", 
            "--url", "https://petstore.swagger.io/v2/swagger.json",
            "--verbose"
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Подробные логи:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения команды")
    except FileNotFoundError:
        print("❌ APIZap не найден. Убедитесь, что он установлен: pip install -e .")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

def show_existing_report():
    """Показывает существующий JSON отчет."""
    json_files = ["petstore_results.json", "demo_results.json", "demo_results_swagger_petstore.json"]
    
    for json_file in json_files:
        json_path = Path(json_file)
        if json_path.exists():
            print(f"📄 Показ существующего JSON отчета: {json_file}")
            print("-" * 60)
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Показать сводную статистику
                print("📊 СВОДНАЯ СТАТИСТИКА:")
                summary = data.get('summary', {})
                print(f"  Всего тестов: {summary.get('total_tests', 'N/A')}")
                print(f"  Успешных: {summary.get('passed', 'N/A')} ({summary.get('success_rate', 0):.1f}%)")
                print(f"  Предупреждений: {summary.get('warnings', 'N/A')}")
                print(f"  Неудачных: {summary.get('failed', 'N/A')}")
                print(f"  Общее время: {summary.get('total_time_ms', 0):.2f}ms")
                print(f"  Среднее время: {summary.get('average_time_ms', 0):.2f}ms")
                
                # Показать несколько тестов
                print("\n📋 ПРИМЕРЫ ТЕСТОВ:")
                tests = data.get('tests', [])
                for i, test in enumerate(tests[:5]):
                    status_emoji = "✅" if test['status'] == 'PASS' else "⚠️" if test['status'] == 'WARN' else "❌"
                    print(f"  {status_emoji} {test['method']} {test['path']} → {test['status_code']} ({test['response_time_ms']:.1f}ms)")
                
                if len(tests) > 5:
                    print(f"  ... и еще {len(tests) - 5} тестов")
                    
                return
                
            except json.JSONDecodeError:
                print("❌ Ошибка чтения JSON файла")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    print("📄 JSON отчеты не найдены. Сначала запустите тестирование (опция 2).")

def show_help():
    """Показывает справку APIZap."""
    print("❓ Справка APIZap:")
    print("-" * 60)
    
    try:
        result = subprocess.run(["apizap", "--help"], capture_output=True, text=True)
        print(result.stdout)
    except FileNotFoundError:
        print("❌ APIZap не найден. Убедитесь, что он установлен: pip install -e .")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_project_info():
    """Показывает информацию о проекте."""
    print("📖 ИНФОРМАЦИЯ О ПРОЕКТЕ APIZap")
    print("="*60)
    print()
    print("🎯 НАЗНАЧЕНИЕ:")
    print("   APIZap - это инструмент командной строки для автоматического")
    print("   тестирования API на основе OpenAPI/Swagger спецификаций.")
    print()
    print("⚡ ОСНОВНЫЕ ВОЗМОЖНОСТИ:")
    print("   • Автоматический парсинг OpenAPI 3.0 и Swagger 2.0")
    print("   • Генерация тестов для всех HTTP методов")
    print("   • Поддержка аутентификации (Bearer, API ключи)")
    print("   • Текстовые и JSON отчеты")
    print("   • Обработка ошибок и валидация")
    print("   • Минимальные зависимости")
    print()
    print("📦 ЗАВИСИМОСТИ:")
    print("   • click >= 8.0.0 (CLI интерфейс)")
    print("   • requests >= 2.28.0 (HTTP запросы)")
    print("   • pydantic >= 2.0.0 (валидация данных)")
    print("   • loguru >= 0.6.0 (логирование)")
    print()
    print("🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:")
    print("   apizap --url https://api.example.com/swagger.json")
    print("   apizap --url https://api.example.com/openapi.json --auth-type bearer --auth-token TOKEN")
    print("   apizap --url https://api.example.com/spec.json --output json --output-file results.json")
    print()
    print("🔗 РЕПОЗИТОРИЙ: https://github.com/apizap/apizap")
    print("📧 ПОДДЕРЖКА: info@apizap.dev")

def main():
    """Главная функция демонстрации."""
    print_header()
    
    while True:
        print_menu()
        try:
            choice = input("Выберите опцию (0-6): ").strip()
            print()
            
            if choice == '0':
                print("👋 До свидания!")
                break
            elif choice == '1':
                run_basic_test()
            elif choice == '2':
                run_json_test()
            elif choice == '3':
                run_verbose_test()
            elif choice == '4':
                show_existing_report()
            elif choice == '5':
                show_help()
            elif choice == '6':
                show_project_info()
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\nНажмите Enter для продолжения...")
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main() 