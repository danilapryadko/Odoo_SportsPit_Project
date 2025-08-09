#!/bin/bash

# Скрипт проверки на наличие секретов в коде перед коммитом
# Добавьте в pre-commit hook

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Проверка на наличие секретов в коде...${NC}"

# Паттерны для поиска потенциальных секретов
PATTERNS=(
    "password.*=.*['\"].*['\"]"
    "api[_-]?key.*=.*['\"].*['\"]"
    "secret.*=.*['\"].*['\"]"
    "token.*=.*['\"].*['\"]"
    "PRIVATE KEY"
    "BEGIN RSA"
    "BEGIN DSA"
    "BEGIN EC"
    "BEGIN PGP"
    "aws_access_key_id"
    "aws_secret_access_key"
    "client_secret"
    "api_token"
)

FOUND_SECRETS=0
FILES_TO_CHECK=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|json|yml|yaml|env|conf|cfg|ini|sh)$' || true)

if [ -z "$FILES_TO_CHECK" ]; then
    echo -e "${GREEN}✅ Нет файлов для проверки${NC}"
    exit 0
fi

for pattern in "${PATTERNS[@]}"; do
    for file in $FILES_TO_CHECK; do
        if [ -f "$file" ]; then
            # Исключаем файлы-примеры
            if [[ "$file" == *".example"* ]] || [[ "$file" == *"example."* ]]; then
                continue
            fi
            
            # Ищем паттерн в файле
            if grep -Ei "$pattern" "$file" > /dev/null 2>&1; then
                echo -e "${RED}❌ Потенциальный секрет найден в $file:${NC}"
                grep -Ein "$pattern" "$file" | head -3
                FOUND_SECRETS=$((FOUND_SECRETS + 1))
            fi
        fi
    done
done

# Проверка на наличие файлов, которые не должны быть в репозитории
FORBIDDEN_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "secrets.yml"
    "secrets.yaml"
    "credentials.json"
    "*.pem"
    "*.key"
    "*.p12"
)

for pattern in "${FORBIDDEN_FILES[@]}"; do
    if git diff --cached --name-only | grep -E "$pattern" > /dev/null 2>&1; then
        echo -e "${RED}❌ Запрещенный файл в коммите: $pattern${NC}"
        FOUND_SECRETS=$((FOUND_SECRETS + 1))
    fi
done

if [ $FOUND_SECRETS -gt 0 ]; then
    echo -e "${RED}❌ Найдено потенциальных секретов: $FOUND_SECRETS${NC}"
    echo -e "${YELLOW}Рекомендации:${NC}"
    echo "  1. Используйте переменные окружения вместо хардкода"
    echo "  2. Добавьте файлы с секретами в .gitignore"
    echo "  3. Используйте .env.example для примеров"
    echo "  4. Для Railway/GitHub используйте их системы секретов"
    echo ""
    echo -e "${YELLOW}Если это false positive, используйте:${NC}"
    echo "  git commit --no-verify"
    exit 1
else
    echo -e "${GREEN}✅ Секреты не найдены${NC}"
fi