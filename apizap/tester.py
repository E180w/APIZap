"""Модуль для тестирования API эндпоинтов."""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from loguru import logger

from .parser import OpenAPISpec, Parameter


class APITester:
    """Тестер API эндпоинтов."""
    
    def __init__(self, timeout: int = 30, auth_config: Optional[Dict[str, str]] = None):
        """Инициализация тестера.
        
        Args:
            timeout: Таймаут для HTTP запросов в секундах
            auth_config: Конфигурация аутентификации
        """
        self.timeout = timeout
        self.auth_config = auth_config
        self.session = requests.Session()
        
        # Настройка аутентификации
        if auth_config:
            self._setup_auth()
        
        # Базовые заголовки
        self.session.headers.update({
            'User-Agent': 'APIZap/1.0.0 (API Tester)',
            'Accept': 'application/json, */*'
        })
    
    def _setup_auth(self):
        """Настраивает аутентификацию для сессии."""
        if not self.auth_config:
            return
        
        auth_type = self.auth_config.get('type')
        token = self.auth_config.get('token')
        header = self.auth_config.get('header', 'Authorization')
        
        if auth_type == 'bearer':
            self.session.headers[header] = f"Bearer {token}"
        elif auth_type == 'apikey':
            self.session.headers[header] = token
        
        logger.debug(f"Настроена аутентификация: {auth_type}")
    
    def test_all_endpoints(self, spec: OpenAPISpec) -> List[Dict[str, Any]]:
        """Тестирует все эндпоинты API.
        
        Args:
            spec: OpenAPI спецификация
            
        Returns:
            Список результатов тестов
        """
        from .parser import OpenAPIParser
        
        parser = OpenAPIParser()
        base_url = parser.get_base_url(spec)
        operations = parser.get_all_operations(spec)
        
        results = []
        total_operations = len(operations)
        
        logger.info(f"Начинаем тестирование {total_operations} операций...")
        
        for i, operation_info in enumerate(operations, 1):
            logger.info(f"[{i}/{total_operations}] Тестируем: {operation_info['method']} {operation_info['path']}")
            
            result = self._test_single_endpoint(
                base_url=base_url,
                method=operation_info['method'],
                path=operation_info['path'],
                operation=operation_info['operation'],
                parameters=operation_info['parameters'],
                operation_id=operation_info['operation_id'],
                summary=operation_info['summary']
            )
            
            results.append(result)
            
            # Небольшая задержка между запросами
            time.sleep(0.1)
        
        logger.info(f"Тестирование завершено. Обработано операций: {len(results)}")
        return results
    
    def _test_single_endpoint(
        self,
        base_url: str,
        method: str,
        path: str,
        operation: Any,
        parameters: List[Parameter],
        operation_id: str,
        summary: str
    ) -> Dict[str, Any]:
        """Тестирует один эндпоинт.
        
        Args:
            base_url: Базовый URL API
            method: HTTP метод
            path: Путь эндпоинта
            operation: Операция из спецификации
            parameters: Список параметров
            operation_id: ID операции
            summary: Краткое описание операции
            
        Returns:
            Результат тестирования
        """
        start_time = time.time()
        test_result = {
            'operation_id': operation_id,
            'method': method,
            'path': path,
            'summary': summary,
            'status': 'FAIL',
            'status_code': None,
            'response_time': None,
            'error': None,
            'response_headers': {},
            'response_size': 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Подготовка URL и параметров
            full_url, query_params, path_params, headers, json_body = self._prepare_request(
                base_url, path, parameters, operation
            )
            
            # Выполнение запроса
            response = self.session.request(
                method=method.upper(),
                url=full_url,
                params=query_params,
                headers=headers,
                json=json_body,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Измерение времени ответа
            response_time = time.time() - start_time
            
            # Анализ ответа
            test_result.update({
                'status_code': response.status_code,
                'response_time': round(response_time * 1000, 2),  # в миллисекундах
                'response_headers': dict(response.headers),
                'response_size': len(response.content)
            })
            
            # Определение статуса теста
            if 200 <= response.status_code < 300:
                test_result['status'] = 'PASS'
            elif 400 <= response.status_code < 500:
                # Клиентские ошибки могут быть ожидаемыми
                test_result['status'] = 'WARN'
                test_result['error'] = f"Клиентская ошибка: {response.status_code}"
            else:
                test_result['status'] = 'FAIL'
                test_result['error'] = f"Серверная ошибка: {response.status_code}"
            
            # Попытка парсинга JSON ответа для дополнительной информации
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_json = response.json()
                    if isinstance(response_json, dict) and 'error' in response_json:
                        test_result['error'] = response_json.get('error', 'Неизвестная ошибка')
            except (json.JSONDecodeError, ValueError):
                pass  # Игнорируем ошибки парсинга JSON
            
            logger.debug(f"  -> {test_result['status']} ({test_result['status_code']}) {test_result['response_time']}ms")
            
        except requests.exceptions.Timeout:
            test_result.update({
                'status': 'FAIL',
                'error': f'Таймаут запроса ({self.timeout}s)',
                'response_time': (time.time() - start_time) * 1000
            })
            logger.warning(f"  -> TIMEOUT после {self.timeout}s")
            
        except requests.exceptions.ConnectionError as e:
            test_result.update({
                'status': 'FAIL',
                'error': f'Ошибка подключения: {str(e)}',
                'response_time': (time.time() - start_time) * 1000
            })
            logger.warning(f"  -> CONNECTION ERROR: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            test_result.update({
                'status': 'FAIL',
                'error': f'Ошибка запроса: {str(e)}',
                'response_time': (time.time() - start_time) * 1000
            })
            logger.warning(f"  -> REQUEST ERROR: {str(e)}")
            
        except Exception as e:
            test_result.update({
                'status': 'FAIL',
                'error': f'Неожиданная ошибка: {str(e)}',
                'response_time': (time.time() - start_time) * 1000
            })
            logger.error(f"  -> UNEXPECTED ERROR: {str(e)}")
        
        return test_result
    
    def _prepare_request(
        self,
        base_url: str,
        path: str,
        parameters: List[Parameter],
        operation: Any
    ) -> tuple:
        """Подготавливает параметры запроса.
        
        Args:
            base_url: Базовый URL
            path: Путь эндпоинта
            parameters: Список параметров
            operation: Операция из спецификации
            
        Returns:
            Кортеж (url, query_params, path_params, headers, json_body)
        """
        query_params = {}
        path_params = {}
        headers = {}
        json_body = None
        
        # Обработка параметров
        for param in parameters:
            if param.in_ == 'query':
                # Добавляем query параметры с примерными значениями
                query_params[param.name] = self._get_example_value(param)
            elif param.in_ == 'path':
                # Добавляем path параметры с примерными значениями
                path_params[param.name] = self._get_example_value(param)
            elif param.in_ == 'header':
                # Добавляем заголовки с примерными значениями
                headers[param.name] = str(self._get_example_value(param))
        
        # Замена path параметров в URL
        processed_path = path
        for param_name, param_value in path_params.items():
            processed_path = processed_path.replace(f'{{{param_name}}}', str(param_value))
        
        # Формирование полного URL
        full_url = urljoin(base_url + '/', processed_path.lstrip('/'))
        
        # Обработка request body для POST/PUT/PATCH запросов
        if operation and operation.requestBody:
            json_body = self._generate_request_body(operation.requestBody)
        
        return full_url, query_params, path_params, headers, json_body
    
    def _get_example_value(self, param: Parameter) -> Any:
        """Генерирует примерное значение для параметра.
        
        Args:
            param: Параметр OpenAPI
            
        Returns:
            Примерное значение
        """
        # Если есть example, используем его
        if param.example is not None:
            return param.example
        
        # Если есть схема, анализируем тип
        if param.schema_:
            schema_type = param.schema_.get('type', 'string')
            
            if schema_type == 'integer':
                return 1
            elif schema_type == 'number':
                return 1.0
            elif schema_type == 'boolean':
                return True
            elif schema_type == 'array':
                return []
            elif schema_type == 'object':
                return {}
        
        # По умолчанию возвращаем строковое значение
        if param.name.lower() in ['id', 'userid', 'user_id']:
            return '1'
        elif param.name.lower() in ['name', 'username']:
            return 'test'
        elif param.name.lower() in ['email']:
            return 'test@example.com'
        else:
            return 'test_value'
    
    def _generate_request_body(self, request_body: Any) -> Optional[Dict[str, Any]]:
        """Генерирует тело запроса на основе спецификации.
        
        Args:
            request_body: Спецификация тела запроса
            
        Returns:
            Словарь с телом запроса или None
        """
        try:
            # Ищем application/json content type
            content = request_body.content
            if 'application/json' in content:
                json_schema = content['application/json'].get('schema', {})
                return self._generate_json_from_schema(json_schema)
            
            # Если нет JSON, пытаемся найти другие форматы
            for content_type, content_info in content.items():
                if 'json' in content_type.lower():
                    json_schema = content_info.get('schema', {})
                    return self._generate_json_from_schema(json_schema)
            
        except Exception as e:
            logger.debug(f"Ошибка генерации request body: {str(e)}")
        
        return None
    
    def _generate_json_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует JSON объект из OpenAPI схемы.
        
        Args:
            schema: OpenAPI схема
            
        Returns:
            Сгенерированный JSON объект
        """
        if not isinstance(schema, dict):
            return {}
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            result = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                # Генерируем значения только для обязательных полей
                if prop_name in required:
                    result[prop_name] = self._generate_value_from_schema(prop_schema)
            
            return result
        
        return self._generate_value_from_schema(schema)
    
    def _generate_value_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Генерирует значение из OpenAPI схемы.
        
        Args:
            schema: OpenAPI схема
            
        Returns:
            Сгенерированное значение
        """
        if not isinstance(schema, dict):
            return "test_value"
        
        # Проверяем example
        if 'example' in schema:
            return schema['example']
        
        schema_type = schema.get('type', 'string')
        
        if schema_type == 'string':
            return "test_string"
        elif schema_type == 'integer':
            return 1
        elif schema_type == 'number':
            return 1.0
        elif schema_type == 'boolean':
            return True
        elif schema_type == 'array':
            items = schema.get('items', {})
            return [self._generate_value_from_schema(items)]
        elif schema_type == 'object':
            return self._generate_json_from_schema(schema)
        else:
            return "test_value" 