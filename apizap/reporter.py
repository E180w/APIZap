"""Модуль для генерации отчетов о результатах тестирования."""

import json
from datetime import datetime
from typing import Any, Dict, List


class TestReporter:
    """Генератор отчетов о результатах тестирования API."""
    
    def generate_text_report(self, results: List[Dict[str, Any]]) -> str:
        """Генерирует текстовый отчет.
        
        Args:
            results: Список результатов тестирования
            
        Returns:
            Текстовый отчет
        """
        if not results:
            return "🤷 Нет результатов для отображения"
        
        # Сбор статистики
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['status'] == 'PASS')
        warning_tests = sum(1 for r in results if r['status'] == 'WARN')
        failed_tests = sum(1 for r in results if r['status'] == 'FAIL')
        
        # Расчет времени выполнения
        total_time = sum(r.get('response_time', 0) for r in results)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        # Заголовок отчета
        report_lines = [
            f"📊 СВОДНАЯ СТАТИСТИКА",
            f"{'='*50}",
            f"📈 Всего тестов: {total_tests}",
            f"✅ Успешных: {passed_tests} ({passed_tests/total_tests*100:.1f}%)",
            f"⚠️  Предупреждений: {warning_tests} ({warning_tests/total_tests*100:.1f}%)",
            f"❌ Неудачных: {failed_tests} ({failed_tests/total_tests*100:.1f}%)",
            f"⏱️  Общее время: {total_time:.2f}ms",
            f"📊 Среднее время: {avg_time:.2f}ms",
            "",
            f"📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ",
            f"{'='*50}"
        ]
        
        # Группировка по статусу
        status_groups = {
            'PASS': [],
            'WARN': [],
            'FAIL': []
        }
        
        for result in results:
            status_groups[result['status']].append(result)
        
        # Отображение результатов по группам
        status_icons = {
            'PASS': '✅',
            'WARN': '⚠️',
            'FAIL': '❌'
        }
        
        status_names = {
            'PASS': 'УСПЕШНЫЕ ТЕСТЫ',
            'WARN': 'ТЕСТЫ С ПРЕДУПРЕЖДЕНИЯМИ',
            'FAIL': 'НЕУДАЧНЫЕ ТЕСТЫ'
        }
        
        for status in ['PASS', 'WARN', 'FAIL']:
            tests = status_groups[status]
            if tests:
                report_lines.extend([
                    "",
                    f"{status_icons[status]} {status_names[status]} ({len(tests)})",
                    "-" * 40
                ])
                
                for test in tests:
                    response_time = test.get('response_time', 0)
                    status_code = test.get('status_code', 'N/A')
                    error = test.get('error', '')
                    
                    # Основная информация о тесте
                    test_line = f"{test['method']} {test['path']}"
                    if status_code != 'N/A':
                        test_line += f" → {status_code}"
                    if response_time:
                        test_line += f" ({response_time:.2f}ms)"
                    
                    report_lines.append(f"  {test_line}")
                    
                    # Описание теста
                    if test.get('summary'):
                        report_lines.append(f"    📝 {test['summary']}")
                    
                    # Ошибка (если есть)
                    if error:
                        report_lines.append(f"    💭 {error}")
                    
                    # Дополнительная информация для детального анализа
                    if test.get('response_size'):
                        report_lines.append(f"    📦 Размер ответа: {test['response_size']} байт")
                    
                    report_lines.append("")  # Пустая строка между тестами
        
        # Рекомендации
        report_lines.extend([
            "",
            f"💡 РЕКОМЕНДАЦИИ",
            f"{'='*50}"
        ])
        
        if failed_tests > 0:
            report_lines.append("🔴 Обратите внимание на неудачные тесты - возможны проблемы с API")
        
        if warning_tests > 0:
            report_lines.append("🟡 Проверьте тесты с предупреждениями - могут потребоваться дополнительные параметры")
        
        if passed_tests == total_tests:
            report_lines.append("🎉 Отлично! Все тесты прошли успешно")
        
        if avg_time > 5000:  # 5 секунд
            report_lines.append("⏰ Среднее время ответа довольно высокое - возможны проблемы с производительностью")
        
        # Временная метка
        report_lines.extend([
            "",
            f"🕐 Отчет сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(report_lines)
    
    def generate_json_report(self, results: List[Dict[str, Any]]) -> str:
        """Генерирует JSON отчет.
        
        Args:
            results: Список результатов тестирования
            
        Returns:
            JSON отчет в виде строки
        """
        if not results:
            return json.dumps({
                "summary": {
                    "total_tests": 0,
                    "passed": 0,
                    "warnings": 0,
                    "failed": 0,
                    "success_rate": 0.0,
                    "total_time_ms": 0.0,
                    "average_time_ms": 0.0
                },
                "tests": [],
                "generated_at": datetime.utcnow().isoformat()
            }, indent=2, ensure_ascii=False)
        
        # Сбор статистики
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['status'] == 'PASS')
        warning_tests = sum(1 for r in results if r['status'] == 'WARN')
        failed_tests = sum(1 for r in results if r['status'] == 'FAIL')
        total_time = sum(r.get('response_time', 0) for r in results)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Формирование JSON структуры
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "warnings": warning_tests,
                "failed": failed_tests,
                "success_rate": round(success_rate * 100, 2),
                "total_time_ms": round(total_time, 2),
                "average_time_ms": round(avg_time, 2)
            },
            "tests": []
        }
        
        # Добавление детальной информации о каждом тесте
        for result in results:
            test_info = {
                "operation_id": result.get('operation_id'),
                "method": result['method'],
                "path": result['path'],
                "summary": result.get('summary'),
                "status": result['status'],
                "status_code": result.get('status_code'),
                "response_time_ms": result.get('response_time'),
                "response_size_bytes": result.get('response_size', 0),
                "error": result.get('error'),
                "timestamp": result.get('timestamp')
            }
            
            # Добавляем информацию о заголовках ответа (только ключевые)
            response_headers = result.get('response_headers', {})
            if response_headers:
                key_headers = {}
                for header in ['content-type', 'content-length', 'server', 'x-ratelimit-remaining']:
                    if header in response_headers:
                        key_headers[header] = response_headers[header]
                
                if key_headers:
                    test_info['response_headers'] = key_headers
            
            report["tests"].append(test_info)
        
        # Добавление метаданных
        report["metadata"] = {
            "generator": "APIZap v1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "format_version": "1.0"
        }
        
        # Добавление статистики по статус-кодам
        status_codes = {}
        for result in results:
            code = result.get('status_code')
            if code:
                status_codes[str(code)] = status_codes.get(str(code), 0) + 1
        
        if status_codes:
            report["status_code_distribution"] = status_codes
        
        # Добавление статистики по времени ответа
        response_times = [r.get('response_time', 0) for r in results if r.get('response_time')]
        if response_times:
            report["response_time_stats"] = {
                "min_ms": round(min(response_times), 2),
                "max_ms": round(max(response_times), 2),
                "avg_ms": round(sum(response_times) / len(response_times), 2)
            }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def generate_summary_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерирует краткую статистику.
        
        Args:
            results: Список результатов тестирования
            
        Returns:
            Словарь со статистикой
        """
        if not results:
            return {
                "total": 0,
                "passed": 0,
                "warnings": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['status'] == 'PASS')
        warning_tests = sum(1 for r in results if r['status'] == 'WARN')
        failed_tests = sum(1 for r in results if r['status'] == 'FAIL')
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "warnings": warning_tests,
            "failed": failed_tests,
            "success_rate": round(passed_tests / total_tests * 100, 2) if total_tests > 0 else 0.0
        } 