# 🚀 Railway Deploy Fix для Odoo SportsPit

## Проблема
Railway деплой падает из-за:
1. Долгого старта Odoo (инициализация модулей)
2. Таймаута healthcheck
3. Неоптимальной конфигурации

## Решение

### 1. Оптимизированный Dockerfile (`Dockerfile.railway`)
- Минимальный набор пакетов
- Упрощенный startup скрипт
- Отключена инициализация модулей при старте
- Использование переменных окружения Railway

### 2. Ключевые оптимизации:
```bash
# Быстрый старт без обновления модулей
--stop-after-init=False

# Фиксированная база данных
--db-filter="^${PGDATABASE}$"

# Отключен список баз
--no-database-list

# Workers = 0 для Railway
workers = 0
```

### 3. Deployment команды:

#### Вариант 1: Через Railway CLI
```bash
# Логин (если не залогинен)
railway login

# Линк к проекту
railway link -p daa4ac63-d597-4ba7-b10e-1baf84cbacad

# Деплой
railway up --detach
```

#### Вариант 2: Через скрипт
```bash
./scripts/deploy-railway.sh
```

#### Вариант 3: Через GitHub
```bash
# Пуш изменений
git add .
git commit -m "Fix: Optimized Railway deployment configuration"
git push origin main
```

## Переменные окружения для Railway

Убедитесь, что в Railway настроены:
```
PGHOST=postgresql-odoo.railway.internal
PGPORT=5432
PGUSER=odoo
PGPASSWORD=odoo_sportpit_2024
PGDATABASE=odoo_sportpit
PORT=8069
ADMIN_PASSWORD=SportPit2024Master
```

## Мониторинг

### Проверка логов:
```bash
railway logs -f
```

### Проверка статуса:
```bash
railway status
```

## Если все еще падает:

1. **Увеличить память:**
   - В Railway dashboard: Settings → Resources → увеличить RAM до 2GB

2. **Упростить старт еще больше:**
   ```dockerfile
   # В Dockerfile.railway убрать все модули
   exec odoo --config=/etc/odoo/railway.conf
   ```

3. **Использовать прекомпилированный образ:**
   ```bash
   # Локально собрать и запушить в registry
   docker build -f Dockerfile.railway -t odoo-sportpit:optimized .
   docker tag odoo-sportpit:optimized registry.railway.app/odoo-sportpit
   docker push registry.railway.app/odoo-sportpit
   ```

## Альтернатива - Fly.io

Если Railway продолжает падать:
```bash
flyctl deploy --config fly.toml
```

## Контакты для помощи
- Railway Discord: https://discord.gg/railway
- Railway Support: support@railway.app