# 🎯 ИНСТРУКЦИЯ: Проверка и вход в Odoo

## 1️⃣ Проверьте, создана ли база данных

Откройте в браузере:
```
https://odoosportspitproject-production.up.railway.app/web/database/selector
```

Если видите список баз данных и там есть **odoo_sportpit** - база создана! ✅

## 2️⃣ Если база НЕ создана

1. Перейдите на: https://odoosportspitproject-production.up.railway.app/web/database/manager
2. Нажмите **"Create Database"**
3. Заполните форму:
   - Master Password: `SportPit2024Master`
   - Database Name: `odoo_sportpit`
   - Email: `danila@usafitandjoy.com`
   - Password: `admin_sportpit_2024`
   - Confirm Password: `admin_sportpit_2024`
   - Language: **Russian / Русский**
   - Country: **Russia**
   - ❌ Снимите галочку "Load demonstration data"
4. Нажмите **"Create Database"**
5. Подождите 1-2 минуты

## 3️⃣ Если база создана - войдите в систему

1. Перейдите на: https://odoosportspitproject-production.up.railway.app/web/login
2. Введите:
   - Email: `danila@usafitandjoy.com`
   - Password: `admin_sportpit_2024`
3. Нажмите **"Log in"**

## 4️⃣ После успешного входа

Запустите скрипты для настройки:

```bash
# Установка модулей
python3 scripts/install_odoo_modules.py

# Создание продуктов и рецептур
python3 scripts/create_products_and_bom.py
```

## ❓ Проблемы?

Если не можете войти:
1. Проверьте правильность пароля
2. Убедитесь, что выбрана база данных `odoo_sportpit`
3. Попробуйте очистить cookies браузера для этого сайта

---

**Текущий статус:** Проверьте результат выполнения `simple_check.py` в терминале
