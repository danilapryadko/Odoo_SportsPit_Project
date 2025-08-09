# 🚀 Доступы и настройки Odoo SportsPit Project

## 📌 URL доступа к системе
**Production URL:** https://odoosportspitproject-production.up.railway.app

## 🔐 Доступы

### Master Password (для создания/управления БД):
```
SportPit2024Master (наш новый)

Старые (не работают):
- dbny-777k-4ggc  (сгенерирован системой)
- admin_sportpit_2024 (первоначальный)
```

### База данных:
```
Имя БД: odoo_sportpit
Хост: postgresql-odoo.railway.internal
Порт: 5432
Пользователь: odoo
Пароль: odoo_sportpit_2024
```

### Администратор Odoo:
```
Email: danila@usafitandjoy.com
Password: admin_sportpit_2024!
Phone: +79779106671
```

## 🛠️ Railway настройки

### Проект:
- **Название:** athletic-emotion
- **Project ID:** daa4ac63-d597-4ba7-b10e-1baf84cbacad
- **Environment:** production (d312f78e-aea8-46ab-a1a6-0b20b9e94e74)

### Сервисы:
1. **Odoo_SportsPit_Project**
   - Service ID: b6ea85a1-246c-460a-9642-e204f70a2bec
   - Домен: odoosportspitproject-production.up.railway.app
   - Порт: 8069

2. **PostgreSQL-Odoo**
   - Service ID: 7eaa90e4-d6e2-46d1-8b04-306d73f85d24
   - Internal host: postgresql-odoo.railway.internal

### Railway API Token:
```
e2a89410-8aeb-419c-8020-741fba8f9bf9
```

## 📁 GitHub репозиторий
**URL:** https://github.com/danilapryadko/Odoo_SportsPit_Project.git

## 🌍 Локализация
- **Язык:** Русский (ru_RU.UTF-8)
- **Часовой пояс:** Europe/Moscow (UTC+3)
- **Валюта:** RUB (Российский рубль)

## 📦 Переменные окружения в Railway

```bash
# База данных
DB_HOST=postgresql-odoo.railway.internal
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=odoo_sportpit_2024
DB_NAME=odoo_sportpit

# Odoo
ADMIN_PASSWORD=admin_sportpit_2024
PORT=8069

# Локализация
TZ=Europe/Moscow
LANG=ru_RU.UTF-8
```

## 🚀 Быстрые команды

### Перезапуск сервиса через Claude:
```
Попроси: "Перезапусти Odoo сервис в Railway"
```

### Проверка логов через Claude:
```
Попроси: "Покажи логи Odoo из Railway"
```

### Обновление через git:
```bash
cd /Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project
git add .
git commit -m "Описание изменений"
git push origin main
```

## 📝 Чек-лист первоначальной настройки

### При первом входе:
- [ ] Создать базу данных (если не создана автоматически)
- [ ] Установить email администратора
- [ ] Установить пароль администратора
- [ ] Выбрать страну: Россия
- [ ] Выбрать язык: Русский

### Установка модулей:
- [ ] Manufacturing (MRP) - Производство
- [ ] Inventory - Склад
- [ ] Purchase - Закупки
- [ ] Sales - Продажи
- [ ] Quality Control - Контроль качества
- [ ] Employees - Сотрудники
- [ ] Attendances - Учет времени
- [ ] Project - Проекты и задачи
- [ ] Accounting - Бухгалтерия

### Настройка компании:
- [ ] Название: [Ваша компания]
- [ ] Адрес: [Адрес в России]
- [ ] ИНН/КПП: [Ваши реквизиты]
- [ ] Валюта: RUB
- [ ] Часовой пояс: Europe/Moscow

### Настройка производства:
- [ ] Создать склады (сырье, готовая продукция)
- [ ] Настроить категории продуктов (протеины, BCAA, гейнеры)
- [ ] Создать единицы измерения
- [ ] Настроить рабочие центры
- [ ] Создать маршруты производства

## 🔧 Решение частых проблем

### Если не открывается сайт:
1. Проверьте статус в Railway
2. Попросите Claude проверить логи
3. Перезапустите сервис

### Если забыли пароль:
1. Используйте master password для сброса
2. Или пересоздайте БД (потеря данных!)

### Если нужно обновить модули:
1. Войдите в режим разработчика (Settings → Activate developer mode)
2. Apps → Update Apps List
3. Установите нужные модули

---
*Документ обновлен: 09.08.2025*
*Сохраните этот файл для быстрого доступа к настройкам!*
