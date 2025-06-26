#!/usr/bin/env python3
"""Тесты для модуля парсера OpenAPI."""

import json
import pytest
from unittest.mock import Mock, patch

from apizap.parser import OpenAPIParser, OpenAPISpec


class TestOpenAPIParser:
    """Тесты для класса OpenAPIParser."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.parser = OpenAPIParser()
    
    def test_init(self):
        """Тест инициализации парсера."""
        parser = OpenAPIParser(timeout=60)
        assert parser.timeout == 60
        assert parser.session is not None
    
    def test_is_url_valid(self):
        """Тест проверки валидных URL."""
        assert self.parser._is_url("https://example.com/api.json") is True
        assert self.parser._is_url("http://localhost:8000/openapi.json") is True
        assert self.parser._is_url("https://api.example.com/v1/swagger.json") is True
    
    def test_is_url_invalid(self):
        """Тест проверки невалидных URL."""
        assert self.parser._is_url("not_a_url") is False
        assert self.parser._is_url("/local/file.json") is False
        assert self.parser._is_url("file.json") is False
    
    def test_parse_valid_spec(self):
        """Тест парсинга валидной спецификации."""
        # Минимальная валидная OpenAPI спецификация
        spec_data = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }
        
        # Мокаем загрузку данных
        with patch.object(self.parser, '_load_from_url', return_value=spec_data):
            spec = self.parser.parse("https://example.com/api.json")
            
            assert spec is not None
            assert isinstance(spec, OpenAPISpec)
            assert spec.info.title == "Test API"
            assert spec.info.version == "1.0.0"
            assert "/users" in spec.paths
    
    def test_parse_invalid_spec(self):
        """Тест парсинга невалидной спецификации."""
        # Невалидная спецификация (отсутствует info)
        invalid_spec = {
            "openapi": "3.0.0",
            "paths": {}
        }
        
        with patch.object(self.parser, '_load_from_url', return_value=invalid_spec):
            spec = self.parser.parse("https://example.com/invalid.json")
            assert spec is None
    
    def test_get_base_url_with_servers(self):
        """Тест получения базового URL из серверов."""
        spec = Mock()
        spec.servers = [
            Mock(url="https://api.example.com/v1"),
            Mock(url="https://api-staging.example.com/v1")
        ]
        
        base_url = self.parser.get_base_url(spec)
        assert base_url == "https://api.example.com/v1"
    
    def test_get_base_url_fallback(self):
        """Тест fallback для базового URL."""
        spec = Mock()
        spec.servers = None
        
        base_url = self.parser.get_base_url(spec)
        assert base_url == "http://localhost"
    
    def test_get_all_operations(self):
        """Тест извлечения всех операций."""
        # Создаем мок спецификации
        spec = Mock()
        
        # Мок операции GET
        get_operation = Mock()
        get_operation.operationId = "getUsers"
        get_operation.summary = "Get all users"
        get_operation.tags = ["users"]
        get_operation.parameters = None
        
        # Мок операции POST
        post_operation = Mock()
        post_operation.operationId = "createUser"
        post_operation.summary = "Create user"
        post_operation.tags = ["users"]
        post_operation.parameters = None
        
        # Мок path item
        path_item = Mock()
        path_item.get = get_operation
        path_item.post = post_operation
        path_item.put = None
        path_item.delete = None
        path_item.patch = None
        path_item.head = None
        path_item.options = None
        path_item.parameters = None
        
        spec.paths = {"/users": path_item}
        
        operations = self.parser.get_all_operations(spec)
        
        assert len(operations) == 2
        assert operations[0]['method'] == 'GET'
        assert operations[0]['path'] == '/users'
        assert operations[0]['operation_id'] == 'getUsers'
        assert operations[1]['method'] == 'POST'
        assert operations[1]['path'] == '/users'
        assert operations[1]['operation_id'] == 'createUser'


if __name__ == "__main__":
    pytest.main([__file__]) 