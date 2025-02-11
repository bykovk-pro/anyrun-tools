#!/usr/bin/env bash

# Выход при любой ошибке
set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Функция для вывода заголовка
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Проверка наличия tox
if ! command -v tox &> /dev/null; then
    echo -e "${RED}Error: tox is not installed${NC}"
    echo "Install it with: pip install tox"
    exit 1
fi

# Проверка версии Python
print_header "Checking Python versions"

check_python_version() {
    version=$1
    if command -v python$version &> /dev/null; then
        echo -e "${GREEN}✓ Python $version found${NC}"
        return 0
    else
        echo -e "${RED}✗ Python $version not found${NC}"
        return 1
    fi
}

missing_versions=()
for version in "3.8" "3.9" "3.10" "3.11" "3.12"; do
    if ! check_python_version $version; then
        missing_versions+=($version)
    fi
done

if [ ${#missing_versions[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}Warning: Some Python versions are missing:${NC}"
    for version in "${missing_versions[@]}"; do
        echo "- Python $version"
    done
    echo -e "\nConsider installing them with pyenv:"
    for version in "${missing_versions[@]}"; do
        echo "pyenv install $version"
    done
    echo -e "\nContinue with available versions? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Очистка предыдущих результатов
print_header "Cleaning previous results"
rm -rf .coverage coverage.xml .tox htmlcov .pytest_cache .mypy_cache

# Запуск тестов
print_header "Running tests"
tox run-parallel

# Проверка покрытия кода
if [ -f "coverage.xml" ]; then
    print_header "Code coverage"
    coverage report
fi

print_header "All tests completed successfully!"
