# Руководство по деплою Odoo SportsPit

## 📋 Предварительные требования

### Railway.app
1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Подтвердите email
3. Выберите тариф Pro ($20/месяц) для production

### GitHub
1. Форкните репозиторий или создайте новый
2. Загрузите код проекта
3. Настройте GitHub Actions secrets

## 🚀 Пошаговая инструкция деплоя

### Шаг 1: Подготовка репозитория

```bash
# Клонируйте репозиторий
git clone https://github.com/danilapryadko/Odoo_SportsPit_Project.git
cd Odoo_SportsPit_Project

# Инициализируйте git (если новый проект)
git init
git add .
git commit -m "Initial commit: Odoo SportsPit configuration"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Шаг 2: Настройка Railway

#### 2.1 Создание проекта
1. Войдите в [Railway Dashboard](https://railway.app/dashboard)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Авторизуйте Railway для доступа к GitHub
5. Выберите ваш репозиторий

#### 2.2 Добавление PostgreSQL
1. В проекте нажмите "New Service"
2. Выберите "Database" → "PostgreSQL"
3. Railway автоматически создаст переменные:
   - `DATABASE_HOST`
   - `DATABASE_PORT`
   - `DATABASE_USER`
   - `DATABASE_PASSWORD`
   - `DATABASE_NAME`

#### 2.3 Настройка переменных окружения
В настройках сервиса Odoo добавьте:

```env
# Обязательные
ADMIN_PASSWORD=ваш_безопасный_пароль_123!
PORT=8069
WORKERS=2
LANG=ru_RU.UTF-8
TZ=Europe/Moscow

# Ограничения памяти
LIMIT_MEMORY_HARD=2684354560
LIMIT_MEMORY_SOFT=2147483648

# Опциональные (для email)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_SSL=True
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Шаг 3: Деплой

#### 3.1 Через Railway CLI

```bash
# Установка CLI
npm install -g @railway/cli

# Авторизация
railway login

# Привязка к проекту
railway link

# Деплой
railway up
```

#### 3.2 Через GitHub Actions

1. Получите Railway token:
```bash
railway tokens create
```

2. Добавьте в GitHub Secrets:
   - Перейдите в Settings → Secrets → Actions
   - Добавьте `RAILWAY_TOKEN`

3. Push в main ветку запустит автоматический деплой

### Шаг 4: Инициализация Odoo

#### 4.1 Первый запуск
После успешного деплоя:

1. Получите URL приложения:
```bash
railway domain
# Или в Dashboard → Settings → Domains
```

2. Откройте URL в браузере
3. Odoo автоматически создаст базу данных

#### 4.2 Настройка русской локализации

1. Войдите как администратор
2. Перейдите в Settings → Translations → Languages
3. Активируйте "Russian / Русский"
4. Settings → Translations → Load Translation
   - Language: Russian
   - Загрузить
5. Settings → Users & Companies → Users
   - Выберите admin
   - Preferences → Language: Русский

#### 4.3 Установка модулей

1. Apps → Update Apps List
2. Установите базовые модули:
   - Manufacturing
   - Inventory
   - Purchase
   - Sales
   - Quality Control
   - Employees
   - Attendances
   - Project
   - Timesheets

3. Установите кастомные модули:
   - Sports Nutrition Base
   - Mercury Integration (когда готов)
   - Chestny Znak Integration (когда готов)
   - Production Automation (когда готов)

### Шаг 5: Настройка производства

#### 5.1 Создание компании
1. Settings → Companies → Create
   - Название: ООО "СпортПит"
   - Страна: Россия
   - Валюта: RUB
   - Часовой пояс: Europe/Moscow

#### 5.2 Настройка складов
1. Inventory → Configuration → Warehouses
2. Создайте склады:
   - Склад сырья
   - Склад готовой продукции
   - Карантинная зона

#### 5.3 Настройка производственных участков
1. Manufacturing → Configuration → Work Centers
2. Создайте участки:
   - Взвешивание
   - Смешивание
   - Лаборатория
   - Фасовка
   - Маркировка
   - Упаковка

## 🔧 Обслуживание

### Мониторинг
```bash
# Просмотр логов
railway logs --tail 100

# Статус сервисов
railway status

# Метрики
railway metrics
```

### Резервное копирование

#### Автоматическое (Railway)
1. Dashboard → PostgreSQL → Settings
2. Включите "Daily Backups"

#### Ручное
```bash
# Подключение к БД
railway run psql

# Создание дампа
pg_dump odoo_sportpit > backup_$(date +%Y%m%d).sql
```

### Обновление

```bash
# Обновление кода
git pull origin main
git push

# Railway автоматически передеплоит

# Обновление модулей Odoo
railway run odoo -u all
```

## 🚨 Устранение проблем

### Проблема: "Database connection failed"
**Решение:**
1. Проверьте переменные окружения в Railway
2. Убедитесь, что PostgreSQL запущен
3. Проверьте сетевые настройки

### Проблема: "Module not found"
**Решение:**
```bash
# Проверьте пути к модулям
railway run ls -la /mnt/extra-addons

# Обновите список модулей
railway run odoo -u base --stop-after-init
```

### Проблема: "Out of memory"
**Решение:**
1. Увеличьте лимиты в переменных окружения
2. Уменьшите количество workers
3. Обновите тарифный план Railway

### Проблема: "Slow performance"
**Решение:**
1. Включите кеширование в odoo.conf
2. Оптимизируйте PostgreSQL:
```sql
-- Анализ таблиц
ANALYZE;

-- Очистка
VACUUM FULL;
```

## 📊 Мониторинг производительности

### Метрики для отслеживания
- CPU использование < 80%
- RAM использование < 2GB
- Время ответа < 2 сек
- Доступность > 99.9%

### Инструменты мониторинга
- Railway Metrics (встроенный)
- Grafana (опционально)
- Sentry (для ошибок)

## 🔒 Безопасность

### Чек-лист безопасности
- [ ] Сильный пароль администратора
- [ ] HTTPS включен (Railway автоматически)
- [ ] Регулярные бэкапы настроены
- [ ] Доступ ограничен по IP (если нужно)
- [ ] 2FA для администраторов
- [ ] Логирование включено
- [ ] Мониторинг безопасности

### Рекомендации
1. Меняйте пароли каждые 90 дней
2. Используйте разные пароли для dev/staging/production
3. Не храните секреты в коде
4. Регулярно обновляйте зависимости

## 📝 Контрольный список деплоя

- [ ] Репозиторий создан и код загружен
- [ ] Railway проект создан
- [ ] PostgreSQL добавлен
- [ ] Переменные окружения настроены
- [ ] Деплой успешно выполнен
- [ ] Домен настроен
- [ ] Odoo инициализирован
- [ ] Русский язык установлен
- [ ] Модули установлены
- [ ] Компания создана
- [ ] Склады настроены
- [ ] Производственные участки созданы
- [ ] Резервное копирование настроено
- [ ] Мониторинг включен
- [ ] Документация обновлена

---

**Последнее обновление:** 2025-01-08  
**Версия документа:** 1.0.0