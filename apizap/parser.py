"""Модуль для парсинга OpenAPI спецификаций."""

import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from loguru import logger
from pydantic import BaseModel, Field, ValidationError


class Contact(BaseModel):
    """Контактная информация API."""
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


class License(BaseModel):
    """Лицензия API."""
    name: str
    url: Optional[str] = None


class Info(BaseModel):
    """Информация об API."""
    title: str
    description: Optional[str] = None
    version: str
    contact: Optional[Contact] = None
    license: Optional[License] = None


class Server(BaseModel):
    """Сервер API."""
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class Parameter(BaseModel):
    """Параметр операции."""
    name: str
    in_: str = Field(alias='in')
    description: Optional[str] = None
    required: Optional[bool] = False
    schema_: Optional[Dict[str, Any]] = Field(default=None, alias='schema')
    example: Optional[Any] = None


class RequestBody(BaseModel):
    """Тело запроса."""
    description: Optional[str] = None
    content: Dict[str, Any]
    required: Optional[bool] = False


class Response(BaseModel):
    """Ответ операции."""
    description: str
    content: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None


class Operation(BaseModel):
    """HTTP операция."""
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    requestBody: Optional[RequestBody] = None
    responses: Dict[str, Response]
    security: Optional[List[Dict[str, List[str]]]] = None


class PathItem(BaseModel):
    """Элемент пути API."""
    get: Optional[Operation] = None
    post: Optional[Operation] = None
    put: Optional[Operation] = None
    delete: Optional[Operation] = None
    patch: Optional[Operation] = None
    head: Optional[Operation] = None
    options: Optional[Operation] = None
    parameters: Optional[List[Parameter]] = None


class OpenAPISpec(BaseModel):
    """Главная модель OpenAPI спецификации."""
    openapi: Optional[str] = None  # Для OpenAPI 3.0+
    swagger: Optional[str] = None  # Для Swagger 2.0
    info: Info
    servers: Optional[List[Server]] = None
    host: Optional[str] = None  # Для Swagger 2.0
    basePath: Optional[str] = None  # Для Swagger 2.0
    schemes: Optional[List[str]] = None  # Для Swagger 2.0
    paths: Dict[str, PathItem]
    components: Optional[Dict[str, Any]] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    tags: Optional[List[Dict[str, Any]]] = None


class OpenAPIParser:
    """Парсер OpenAPI спецификаций."""
    
    def __init__(self, timeout: int = 30):
        """Инициализация парсера.
        
        Args:
            timeout: Таймаут для HTTP запросов в секундах
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'APIZap/1.0.0 (OpenAPI Parser)',
            'Accept': 'application/json, application/yaml, text/yaml, */*'
        })
    
    def parse(self, url_or_path: str) -> Optional[OpenAPISpec]:
        """Парсит OpenAPI спецификацию из URL или файла.
        
        Args:
            url_or_path: URL спецификации или путь к локальному файлу
            
        Returns:
            Распарсенная OpenAPI спецификация или None при ошибке
        """
        try:
            # Определяем, это URL или локальный файл
            if self._is_url(url_or_path):
                spec_data = self._load_from_url(url_or_path)
            else:
                spec_data = self._load_from_file(url_or_path)
            
            if not spec_data:
                return None
            
            # Валидация и парсинг с помощью Pydantic
            logger.debug("Валидация OpenAPI спецификации...")
            spec = OpenAPISpec(**spec_data)
            
            logger.info(f"Успешно распарсена спецификация: {spec.info.title} v{spec.info.version}")
            return spec
            
        except ValidationError as e:
            logger.error("Ошибка валидации OpenAPI спецификации:")
            for error in e.errors():
                logger.error(f"  - {error['loc']}: {error['msg']}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при парсинге спецификации: {str(e)}")
            return None
    
    def _is_url(self, path: str) -> bool:
        """Проверяет, является ли строка URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _load_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Загружает спецификацию по URL.
        
        Args:
            url: URL спецификации
            
        Returns:
            Словарь с данными спецификации или None при ошибке
        """
        try:
            logger.debug(f"Загрузка спецификации с URL: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Попытка определить формат по Content-Type или URL
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type or url.endswith('.json'):
                return response.json()
            elif 'yaml' in content_type or url.endswith(('.yaml', '.yml')):
                try:
                    import yaml
                    return yaml.safe_load(response.text)
                except ImportError:
                    logger.warning("PyYAML не установлен, пытаемся парсить как JSON...")
                    return response.json()
            else:
                # Пытаемся сначала JSON, потом YAML
                try:
                    return response.json()
                except json.JSONDecodeError:
                    try:
                        import yaml
                        return yaml.safe_load(response.text)
                    except ImportError:
                        logger.error("Не удалось определить формат спецификации и PyYAML не установлен")
                        return None
            
        except requests.exceptions.Timeout:
            logger.error(f"Таймаут при загрузке спецификации: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Ошибка подключения к: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка {e.response.status_code} при загрузке: {url}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Невалидный JSON в спецификации: {url}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке спецификации: {str(e)}")
            return None
    
    def _load_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Загружает спецификацию из локального файла.
        
        Args:
            file_path: Путь к файлу спецификации
            
        Returns:
            Словарь с данными спецификации или None при ошибке
        """
        try:
            logger.debug(f"Загрузка спецификации из файла: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Определяем формат по расширению файла
            if file_path.endswith('.json'):
                return json.loads(content)
            elif file_path.endswith(('.yaml', '.yml')):
                try:
                    import yaml
                    return yaml.safe_load(content)
                except ImportError:
                    logger.error("PyYAML не установлен для парсинга YAML файлов")
                    return None
            else:
                # Пытаемся автоматически определить формат
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    try:
                        import yaml
                        return yaml.safe_load(content)
                    except ImportError:
                        logger.error("Не удалось определить формат файла и PyYAML не установлен")
                        return None
            
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return None
        except PermissionError:
            logger.error(f"Нет прав доступа к файлу: {file_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Невалидный JSON в файле: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")
            return None
    
    def get_base_url(self, spec: OpenAPISpec) -> str:
        """Получает базовый URL для API.
        
        Args:
            spec: OpenAPI спецификация
            
        Returns:
            Базовый URL API
        """
        # OpenAPI 3.0+ с серверами
        if spec.servers and len(spec.servers) > 0:
            return spec.servers[0].url.rstrip('/')
        
        # Swagger 2.0 с host и basePath
        if spec.host:
            scheme = 'https' if spec.schemes and 'https' in spec.schemes else 'http'
            base_path = spec.basePath.rstrip('/') if spec.basePath else ''
            return f"{scheme}://{spec.host}{base_path}"
        
        # Fallback для старых версий
        return "http://localhost"
    
    def get_all_operations(self, spec: OpenAPISpec) -> List[Dict[str, Any]]:
        """Извлекает все операции из спецификации.
        
        Args:
            spec: OpenAPI спецификация
            
        Returns:
            Список всех операций с метаданными
        """
        operations = []
        
        for path, path_item in spec.paths.items():
            # Получаем параметры уровня пути
            path_parameters = path_item.parameters or []
            
            # Проверяем все HTTP методы
            for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                operation = getattr(path_item, method, None)
                if operation:
                    # Объединяем параметры пути и операции
                    all_parameters = path_parameters.copy()
                    if operation.parameters:
                        all_parameters.extend(operation.parameters)
                    
                    operations.append({
                        'method': method.upper(),
                        'path': path,
                        'operation': operation,
                        'parameters': all_parameters,
                        'operation_id': operation.operationId or f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
                        'summary': operation.summary or f"{method.upper()} {path}",
                        'tags': operation.tags or ['default']
                    })
        
        logger.info(f"Найдено операций: {len(operations)}")
        return operations 