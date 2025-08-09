# Odoo Sports Nutrition Project

Проект для управления производством спортивного питания на базе Odoo 17.0 Community Edition.

## Развертывание на Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

## Настройка

### Переменные окружения

Необходимо установить следующие переменные в Railway:

#### База данных:
- `DB_HOST` - хост PostgreSQL (например: postgresql-odoo.railway.internal)
- `DB_PORT` - порт PostgreSQL (5432)
- `DB_USER` - пользователь БД (odoo)
- `DB_PASSWORD` - пароль БД
- `DB_NAME` - имя базы данных (odoo_sportpit)

#### Odoo:
- `ADMIN_PASSWORD` - пароль администратора Odoo
- `PORT` - порт для Odoo (Railway автоматически предоставляет)

#### Локализация:
- `TZ` - Europe/Moscow
- `LANG` - ru_RU.UTF-8

## Функционал

- 🏭 Управление производством
- 📦 Складской учет с партионным учетом
- 🔬 Контроль качества
- 👥 Управление персоналом
- 📊 Отчетность
- 🇷🇺 Интеграция с Меркурий (в разработке)
- 🏷️ Интеграция с Честный ЗНАК (в разработке)

## Модули

### Основные модули Odoo:
- Manufacturing (MRP)
- Inventory
- Purchase
- Sales
- Quality Control
- Employees (HR)
- Project

### Кастомные модули (в разработке):
- sports_nutrition_base
- mercury_integration
- chestny_znak_integration

## Первый запуск

После развертывания:
1. Дождитесь инициализации базы данных
2. Перейдите по URL вашего приложения
3. Используйте пароль администратора из переменной ADMIN_PASSWORD
4. Установите необходимые модули
5. Загрузите русскую локализацию

## Поддержка

Для вопросов и предложений создавайте Issues в репозитории.
