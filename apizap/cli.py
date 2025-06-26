#!/usr/bin/env python3
"""Главный CLI интерфейс для APIZap."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from .parser import OpenAPIParser
from .tester import APITester
from .reporter import TestReporter


@click.command()
@click.option(
    '--url', '-u',
    required=True,
    help='URL OpenAPI/Swagger спецификации (например: https://api.example.com/swagger.json)'
)
@click.option(
    '--auth-type', '-a',
    type=click.Choice(['bearer', 'apikey', 'none']),
    default='none',
    help='Тип аутентификации: bearer, apikey или none'
)
@click.option(
    '--auth-token', '-t',
    help='Bearer токен или API ключ для аутентификации'
)
@click.option(
    '--auth-header', '-h',
    default='Authorization',
    help='Название заголовка для API ключа (по умолчанию: Authorization)'
)
@click.option(
    '--output', '-o',
    type=click.Choice(['text', 'json']),
    default='text',
    help='Формат вывода результатов: text или json'
)
@click.option(
    '--output-file', '-f',
    help='Файл для сохранения результатов (по умолчанию: вывод в консоль)'
)
@click.option(
    '--timeout', '-to',
    default=30,
    help='Таймаут для HTTP запросов в секундах (по умолчанию: 30)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Подробный вывод с дополнительной информацией'
)
@click.version_option(version='1.0.0', prog_name='APIZap')
def main(
    url: str,
    auth_type: str,
    auth_token: Optional[str],
    auth_header: str,
    output: str,
    output_file: Optional[str],
    timeout: int,
    verbose: bool
):
    """APIZap - Автоматический генератор тестов для API.
    
    Этот инструмент автоматически парсит OpenAPI спецификацию и генерирует
    тесты для всех доступных эндпоинтов API.
    
    Примеры использования:
    
        apizap --url https://petstore.swagger.io/v2/swagger.json
        
        apizap --url https://api.example.com/openapi.json --auth-type bearer --auth-token your_token
        
        apizap --url https://api.example.com/swagger.json --output json --output-file results.json
    """
    # Настройка логирования
    if verbose:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")
    
    try:
        # Валидация параметров аутентификации
        if auth_type != 'none' and not auth_token:
            click.echo("❌ Ошибка: Для типа аутентификации '{}' необходимо указать токен с помощью --auth-token".format(auth_type), err=True)
            sys.exit(1)
        
        click.echo("🚀 Запуск APIZap...")
        click.echo(f"📡 Загрузка OpenAPI спецификации: {url}")
        
        # Парсинг OpenAPI спецификации
        parser = OpenAPIParser()
        spec = parser.parse(url)
        
        if not spec:
            click.echo("❌ Не удалось загрузить или распарсить OpenAPI спецификацию", err=True)
            sys.exit(1)
        
        click.echo(f"✅ Спецификация успешно загружена: {spec.info.title} v{spec.info.version}")
        click.echo(f"📊 Найдено эндпоинтов: {len(spec.paths)}")
        
        # Настройка аутентификации
        auth_config = None
        if auth_type != 'none' and auth_token:
            auth_config = {
                'type': auth_type,
                'token': auth_token,
                'header': auth_header
            }
            click.echo(f"🔐 Аутентификация: {auth_type}")
        
        # Запуск тестов
        click.echo("🧪 Запуск тестов...")
        tester = APITester(timeout=timeout, auth_config=auth_config)
        results = tester.test_all_endpoints(spec)
        
        # Генерация отчета
        reporter = TestReporter()
        if output == 'json':
            report = reporter.generate_json_report(results)
        else:
            report = reporter.generate_text_report(results)
        
        # Вывод или сохранение результатов
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(report, encoding='utf-8')
            click.echo(f"📄 Результаты сохранены в: {output_path.absolute()}")
        else:
            click.echo("\n" + "="*60)
            click.echo("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
            click.echo("="*60)
            click.echo(report)
        
        # Подсчет статистики
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['status'] == 'PASS')
        failed_tests = total_tests - passed_tests
        
        click.echo(f"\n📈 Итого: {total_tests} тестов, {passed_tests} успешных, {failed_tests} неудачных")
        
        if failed_tests > 0:
            sys.exit(1)
    
    except KeyboardInterrupt:
        click.echo("\n⏹️  Тестирование прервано пользователем", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Неожиданная ошибка")
        click.echo(f"❌ Критическая ошибка: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 