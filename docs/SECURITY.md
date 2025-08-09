# 🔒 Руководство по безопасности

## Управление секретами

### ❌ НИКОГДА не делайте это:

```python
# ПЛОХО - никогда не хардкодьте секреты!
DATABASE_PASSWORD = "my_super_secret_password"
API_KEY = "sk-1234567890abcdef"
ADMIN_PASSWORD = "admin123"
```

### ✅ ВСЕГДА делайте так:

```python
# ХОРОШО - используйте переменные окружения
import os

DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
API_KEY = os.environ.get('API_KEY')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
```

## Где хранить секреты

### 1. Локальная разработка
- Используйте файл `.env` (добавлен в .gitignore)
- Копируйте `.env.example` и заполняйте реальными данными
- НИКОГДА не коммитьте `.env` файл!

### 2. Railway Production
- Используйте Railway Variables в Dashboard
- Settings → Variables → Add Variable
- Railway автоматически инжектит их как переменные окружения

### 3. GitHub Actions
- Settings → Secrets and variables → Actions
- New repository secret
- Используйте в workflow: `${{ secrets.YOUR_SECRET }}`

## Проверка на секреты

### Автоматическая проверка перед коммитом:

```bash
# Установите pre-commit hook
cp scripts/check-secrets.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Ручная проверка:

```bash
# Запустите скрипт проверки
./scripts/check-secrets.sh

# Используйте gitleaks (если установлен)
gitleaks detect --config=.gitleaks.toml
```

## Ротация секретов

### Рекомендуемая периодичность:
- **Пароли:** каждые 90 дней
- **API ключи:** каждые 6 месяцев
- **Сертификаты:** перед истечением срока

### Процесс ротации:

1. **Создайте новый секрет**
2. **Обновите в Railway/GitHub**
3. **Деплой с новым секретом**
4. **Проверьте работоспособность**
5. **Отзовите старый секрет**

## Интеграции с внешними системами

### Меркурий
```bash
# Храните в Railway Variables:
MERCURY_API_KEY=xxx
MERCURY_API_SECRET=xxx
MERCURY_CERT_PATH=/certs/mercury.pem
```

### Честный ЗНАК
```bash
# Храните в Railway Variables:
CHESTNY_ZNAK_API_KEY=xxx
CHESTNY_ZNAK_TOKEN=xxx
CHESTNY_ZNAK_OMS_ID=xxx
```

## Шифрование данных

### В базе данных
- Используйте PostgreSQL встроенное шифрование
- Включите SSL для соединений
- Шифруйте бэкапы

### В файловой системе
```bash
# Шифрование бэкапа
gpg --encrypt --recipient your-email@example.com backup.sql

# Расшифровка
gpg --decrypt backup.sql.gpg > backup.sql
```

## Аудит безопасности

### Регулярные проверки:
- [ ] Все секреты в переменных окружения
- [ ] .gitignore содержит все чувствительные файлы
- [ ] Нет хардкода паролей в коде
- [ ] SSL/HTTPS включен в production
- [ ] Бэкапы зашифрованы
- [ ] Логи не содержат секретов
- [ ] 2FA включена для админов

### Инструменты проверки:

```bash
# Сканирование на уязвимости Python пакетов
pip install safety
safety check

# Проверка Docker образа
docker scan odoo-sportpit:latest

# Аудит зависимостей
pip-audit
```

## Инцидент с утечкой

### Если секрет попал в Git:

1. **НЕМЕДЛЕННО смените скомпрометированный секрет**
2. **Удалите из истории Git:**
```bash
# Используйте BFG Repo-Cleaner
brew install bfg  # для macOS
bfg --delete-files .env
git push --force
```
3. **Проверьте все форки репозитория**
4. **Уведомите команду**
5. **Проведите аудит использования**

## Контакты безопасности

- Email безопасности: security@sportspit.ru
- Срочные инциденты: +7 (XXX) XXX-XX-XX

## Чек-лист перед деплоем

- [ ] Все секреты в переменных окружения
- [ ] .env файл НЕ в репозитории
- [ ] Проверка прошла check-secrets.sh
- [ ] HTTPS включен
- [ ] Пароли соответствуют политике (минимум 12 символов)
- [ ] API ключи с ограниченными правами
- [ ] Логирование не содержит секретов
- [ ] Бэкапы настроены и шифруются

---

**Последнее обновление:** 2025-01-08  
**Версия:** 1.0.0