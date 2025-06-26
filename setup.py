#!/usr/bin/env python3
"""Setup script для APIZap."""

from setuptools import setup, find_packages
from pathlib import Path

# Чтение README.md для long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Чтение requirements.txt
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')

setup(
    name="apizap",
    version="1.0.0",
    description="Автоматический генератор тестов для API на основе OpenAPI спецификаций",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="APIZap Team",
    author_email="info@apizap.dev",
    url="https://github.com/apizap/apizap",
    project_urls={
        "Bug Reports": "https://github.com/apizap/apizap/issues",
        "Source": "https://github.com/apizap/apizap",
        "Documentation": "https://github.com/apizap/apizap#readme"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "apizap=apizap.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="api, testing, openapi, swagger, automation, cli",
    zip_safe=False,
) 