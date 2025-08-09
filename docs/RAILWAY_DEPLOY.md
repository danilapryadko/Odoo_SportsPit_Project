# 🚂 Railway Deployment Guide

## Railway API Token Configuration

Ваш Railway API токен сохранен и настроен:
```
Token: e2a89410-8aeb-419c-8020-741fba8f9bf9
```

## Способы деплоя

### Способ 1: Через Railway Dashboard (Рекомендуется)

1. **Откройте Railway Dashboard:**
   https://railway.app/dashboard

2. **Создайте новый проект:**
   - New Project → Deploy from GitHub repo
   - Выберите репозиторий: `Odoo_SportsPit_Project`

3. **Добавьте PostgreSQL:**
   - New Service → Database → PostgreSQL

4. **Установите переменные окружения:**
   ```env
   ADMIN_PASSWORD=SportsPit2025Admin!
   PORT=8069
   WORKERS=2
   LANG=ru_RU.UTF-8
   TZ=Europe/Moscow
   ```

### Способ 2: Через Railway CLI

1. **Авторизуйтесь с токеном:**
   ```bash
   export RAILWAY_TOKEN=e2a89410-8aeb-419c-8020-741fba8f9bf9
   railway login --browserless
   ```

2. **Инициализируйте проект:**
   ```bash
   railway init -n odoo-sportpit
   ```

3. **Деплой:**
   ```bash
   railway up
   ```

### Способ 3: Через GitHub Actions

Токен уже добавлен в проект. Для активации:

1. **Добавьте секрет в GitHub:**
   - Settings → Secrets → Actions
   - Name: `RAILWAY_TOKEN`
   - Value: `e2a89410-8aeb-419c-8020-741fba8f9bf9`

2. **Push в main ветку запустит автоматический деплой**

## Конфигурация сохранена в файлах:

- `.env.railway` - токен для локального использования (в .gitignore)
- `config/railway-mcp.json` - конфигурация Railway MCP
- `scripts/railway-deploy.sh` - скрипт деплоя через API
- `scripts/railway-quick-deploy.sh` - быстрый деплой через CLI

## Проверка токена

Для проверки работоспособности токена:

```bash
curl -H "Authorization: Bearer e2a89410-8aeb-419c-8020-741fba8f9bf9" \
     -H "Content-Type: application/json" \
     -d '{"query":"query { me { email } }"}' \
     https://backboard.railway.app/graphql/v2
```

## Важные замечания

1. **Токен сохранен локально** в `.env.railway` (не коммитится в Git)
2. **Для production** используйте Railway Dashboard для большей безопасности
3. **PostgreSQL** будет автоматически подключен Railway

## После деплоя

1. **Проверьте логи:**
   ```bash
   railway logs --tail 100
   ```

2. **Получите URL приложения:**
   ```bash
   railway domain
   ```

3. **Инициализируйте Odoo:**
   - Откройте URL в браузере
   - Используйте пароль администратора из переменных окружения

## Поддержка

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Railway Status: https://status.railway.app

---

**Token установлен:** ✅  
**Проект готов к деплою:** ✅  
**Последнее обновление:** 2025-01-08