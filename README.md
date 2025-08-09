# Odoo SportsPit Project

Система управления производством спортивного питания на базе Odoo 17.0 Community Edition с интеграцией российских систем маркировки.

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose
- PostgreSQL 15+
- Node.js 16+ (для Railway CLI)
- Git

### Локальная установка

1. **Клонирование репозитория:**
```bash
git clone https://github.com/danilapryadko/Odoo_SportsPit_Project.git
cd Odoo_SportsPit_Project
```

2. **Настройка окружения:**
```bash
cp .env.example .env
# Отредактируйте .env и установите свои пароли
```

3. **Запуск через Docker Compose:**
```bash
docker-compose up -d
```

4. **Инициализация базы данных:**
```bash
chmod +x scripts/*.sh
./scripts/init_db.sh
```

5. **Доступ к системе:**
- URL: http://localhost:8069
- Логин: admin
- Пароль: из файла .env (ADMIN_PASSWORD)

## 🚂 Деплой на Railway

### Подготовка

1. **Создайте аккаунт на Railway.app**
2. **Установите Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

3. **Создайте новый проект в Railway Dashboard**

4. **Настройте переменные окружения в Railway:**
- `ADMIN_PASSWORD` - пароль администратора
- `DATABASE_*` - автоматически создаются при добавлении PostgreSQL

### Деплой

```bash
# Автоматический деплой
./scripts/deploy.sh production

# Или вручную
railway up --service odoo-sportpit
```

## 📦 Структура проекта

```
odoo-sports-nutrition/
├── Dockerfile              # Конфигурация Docker образа
├── docker-compose.yml      # Локальная разработка
├── railway.json           # Конфигурация Railway
├── requirements.txt       # Python зависимости
├── config/
│   └── odoo.conf         # Конфигурация Odoo
├── addons/               # Кастомные модули
│   ├── sports_nutrition_base/     # Базовый модуль
│   ├── mercury_integration/       # Интеграция с Меркурий
│   ├── chestny_znak_integration/  # Интеграция с Честный ЗНАК
│   └── production_automation/     # Автоматизация производства
├── scripts/              # Скрипты автоматизации
│   ├── deploy.sh        # Деплой на Railway
│   ├── init_db.sh       # Инициализация БД
│   ├── backup.sh        # Резервное копирование
│   └── restore.sh       # Восстановление
└── docs/                # Документация
```

## 🔧 Конфигурация

### Основные модули Odoo
- **Manufacturing (MRP)** - управление производством
- **Inventory** - складской учет
- **Purchase** - закупки
- **Sales** - продажи
- **Quality Control** - контроль качества
- **HR & Attendance** - учет персонала
- **Project & Timesheet** - управление задачами

### Кастомные модули
- **sports_nutrition_base** - расширенные поля продуктов (БЖУ, калории)
- **mercury_integration** - интеграция с системой Меркурий
- **chestny_znak_integration** - маркировка Честный ЗНАК
- **production_automation** - автоматизация производственных процессов

## 🛠️ Разработка

### Создание нового модуля
```bash
# Создайте структуру модуля
mkdir -p addons/my_module/{models,views,data,security}
touch addons/my_module/{__init__.py,__manifest__.py}
```

### Тестирование
```bash
# Локальное тестирование
docker-compose up -d
docker-compose logs -f odoo

# Запуск тестов
docker run --rm odoo-sportpit:latest python -m pytest tests/
```

### Резервное копирование
```bash
# Создать бэкап
./scripts/backup.sh

# Восстановить из бэкапа
./scripts/restore.sh backups/odoo_sportpit_YYYYMMDD_HHMMSS.sql.gz
```

## 📊 Мониторинг

### Логи Railway
```bash
railway logs --service odoo-sportpit
```

### Локальные логи
```bash
docker-compose logs -f odoo
```

### Метрики производительности
- CPU: мониторинг через Railway Dashboard
- Memory: ограничение 2GB (настраивается в railway.json)
- Database: PostgreSQL метрики в Railway

## 🔒 Безопасность

- Все пароли хранятся в переменных окружения
- HTTPS обязателен для production (Railway предоставляет автоматически)
- Регулярные бэкапы базы данных
- Ограничение доступа по IP (настраивается в Railway)

## 🐛 Устранение неполадок

### База данных не инициализируется
```bash
# Проверьте подключение к БД
docker-compose exec odoo psql -h db -U odoo -d odoo_sportpit

# Пересоздайте БД
docker-compose down -v
docker-compose up -d
./scripts/init_db.sh
```

### Модули не загружаются
```bash
# Обновите модули
docker-compose exec odoo odoo -c /etc/odoo/odoo.conf -u all

# Проверьте пути к модулям
docker-compose exec odoo ls -la /mnt/extra-addons
```

### Railway деплой не работает
```bash
# Проверьте токен
echo $RAILWAY_TOKEN

# Проверьте статус
railway status

# Проверьте логи
railway logs --tail 100
```

## 📝 Лицензия

LGPL-3.0

## 🤝 Поддержка

- Email: support@sportspit.ru
- Issues: https://github.com/danilapryadko/Odoo_SportsPit_Project/issues

## 🎯 Roadmap

- [x] Базовая конфигурация Odoo
- [x] Docker контейнеризация
- [x] Railway деплой
- [x] CI/CD pipeline
- [ ] Интеграция с Меркурий
- [ ] Интеграция с Честный ЗНАК
- [ ] Мобильное приложение
- [ ] API для партнеров

---

**Версия:** 1.0.0  
**Последнее обновление:** 2025-01-08