# 🏋️ Odoo SportsPit - Система управления производством спортивного питания

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)
![Odoo Version](https://img.shields.io/badge/Odoo-17.0-purple)
![Python Version](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)

## 📌 О проекте

Комплексная ERP-система для управления производством спортивного питания на базе Odoo 17.0 Community Edition с интеграцией российских систем маркировки и прослеживаемости.

### 🎯 Ключевые возможности

- **🏭 Производство** - полный цикл от сырья до готовой продукции
- **📦 Складской учет** - многоуровневые склады с зонами хранения
- **🔬 Контроль качества** - лабораторный контроль на всех этапах
- **📊 Аналитика** - детальные отчеты и дашборды
- **🇷🇺 Российская локализация** - интеграция с Меркурий и Честный ЗНАК
- **⚡ Автоматизация** - скрипты для быстрого развертывания

## 🚀 Быстрый старт

### Автоматическая настройка (рекомендуется)

1. Клонировать репозиторий:
```bash
git clone https://github.com/danilapryadko/Odoo_SportsPit_Project.git
cd Odoo_SportsPit_Project
```

2. Запустить скрипты автоматизации:
```bash
# Проверка статуса
python3 scripts/monitor_status.py

# Создание базы данных
python3 scripts/init_odoo_database.py

# Установка модулей
python3 scripts/install_odoo_modules.py
```

### Ручная настройка

1. Развернуть на Railway через кнопку Deploy
2. Настроить переменные окружения (см. ниже)
3. Дождаться успешного деплоя
4. Войти в Odoo и настроить модули

## 📁 Структура проекта

```
Odoo_SportsPit_Project/
├── Dockerfile              # Docker образ с Odoo 17
├── docker-compose.yml      # Docker Compose конфигурация
├── odoo.conf              # Конфигурация Odoo
├── railway.json           # Railway конфигурация
├── requirements.txt       # Python зависимости
├── scripts/              # Скрипты автоматизации
│   ├── init_odoo_database.py     # Инициализация БД
│   ├── install_odoo_modules.py   # Установка модулей
│   ├── monitor_status.py         # Мониторинг статуса
│   └── README.md                  # Документация скриптов
├── addons/               # Кастомные модули
│   ├── sports_nutrition_base/
│   ├── mercury_integration/
│   ├── chestny_znak_integration/
│   └── production_automation/
├── config/               # Конфигурационные файлы
├── docs/                 # Документация
├── PROJECT_STATUS.md     # Статус проекта
├── CREDENTIALS.md        # Учетные данные
├── SETUP_GUIDE.md        # Руководство по установке
└── README.md             # Этот файл
```

## ⚙️ Конфигурация

### Переменные окружения для Railway

#### База данных PostgreSQL:
```env
DB_HOST=postgresql-odoo.railway.internal
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=odoo_sportpit_2024
DB_NAME=odoo_sportpit
```

#### Odoo настройки:
```env
ADMIN_PASSWORD=SportPit2024Master
ADMIN_PASSWD=SportPit2024Master
USER=odoo
PASSWORD=odoo_sportpit_2024
DATABASE=odoo_sportpit
HOST=0.0.0.0
PORT=8069
```

#### Локализация:
```env
TZ=Europe/Moscow
LANG=ru_RU.UTF-8
```

## 📦 Модули системы

### Установленные модули Odoo:
- ✅ **Manufacturing (MRP)** - управление производством
- ✅ **Inventory** - складской учет
- ✅ **Purchase** - закупки
- ✅ **Sales** - продажи
- ✅ **Quality Control** - контроль качества
- ✅ **Accounting** - бухгалтерия
- ✅ **HR** - управление персоналом
- ✅ **Project** - управление проектами
- ✅ **Product Expiry** - сроки годности

### Разрабатываемые модули:
- 🔄 **sports_nutrition_base** - расширение для спортпита
- 🔄 **mercury_integration** - интеграция с Меркурий
- 🔄 **chestny_znak_integration** - интеграция с Честный ЗНАК
- 🔄 **production_automation** - автоматизация производства

## 🔐 Доступ к системе

После развертывания система доступна по адресу:
```
https://odoosportspitproject-production.up.railway.app
```

**Учетные данные:**
- Email: `danila@usafitandjoy.com`
- Пароль: `admin_sportpit_2024`
- База данных: `odoo_sportpit`

## 📊 Статус проекта

Текущий прогресс: **30%**

- Инфраструктура: █████████░ 90%
- Базовая настройка: ███░░░░░░░ 30%
- Автоматизация: ████░░░░░░ 40%
- Кастомные модули: ░░░░░░░░░░ 0%
- Интеграции: ░░░░░░░░░░ 0%

Подробный статус см. в [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 🛠️ Разработка

### Требования:
- Python 3.11+
- PostgreSQL 15+
- Docker (опционально)
- Git

### Установка зависимостей:
```bash
pip install -r requirements.txt
```

### Запуск локально:
```bash
docker-compose up -d
```

### Тестирование:
```bash
python3 scripts/monitor_status.py --watch
```

## 📚 Документация

- [Руководство по установке](SETUP_GUIDE.md)
- [Статус проекта](PROJECT_STATUS.md)
- [Документация скриптов](scripts/README.md)
- [Официальная документация Odoo](https://www.odoo.com/documentation/17.0/)

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект лицензирован под LGPL-3 лицензией - см. файл [LICENSE](LICENSE) для деталей.

## 💬 Поддержка

- **GitHub Issues:** [Создать issue](https://github.com/danilapryadko/Odoo_SportsPit_Project/issues)
- **Email:** danila@usafitandjoy.com
- **Railway Dashboard:** [Railway](https://railway.app)

## 🙏 Благодарности

- Команде Odoo за отличную ERP платформу
- Railway за простой хостинг
- Claude AI за помощь в разработке
- Сообществу открытого ПО

---

*Последнее обновление: 09.08.2025*
*Версия: 1.0.0*
