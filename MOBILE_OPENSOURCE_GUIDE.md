# 🆓 Open-Source мобильные приложения для Odoo Community

## 🎯 Ответ на ваш вопрос: ДА, есть БЕСПЛАТНЫЕ open-source приложения!

### ⭐ Лучшие варианты:

## 1. Odoo Mobile Framework (Android) - РЕКОМЕНДУЕМ
**Официальный фреймворк от Odoo**

### Преимущества:
- ✅ Полностью БЕСПЛАТНО
- ✅ Открытый исходный код
- ✅ Официальная поддержка от Odoo
- ✅ Офлайн синхронизация
- ✅ Нативная производительность
- ✅ Можно полностью кастомизировать

### Установка и настройка:

```bash
# Шаг 1: Клонируем репозиторий
git clone https://github.com/Odoo-mobile/framework.git
cd framework

# Шаг 2: Открываем в Android Studio
# File -> Open -> выбираем папку framework

# Шаг 3: Настройка подключения к вашему Odoo
```

#### Файл конфигурации `app/src/main/res/values/server_config.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Ваш Odoo сервер -->
    <string name="host_url">https://odoosportspitproject-production.up.railway.app</string>
    <string name="default_database">odoo_sportpit</string>
    
    <!-- Настройки синхронизации -->
    <bool name="allow_offline">true</bool>
    <integer name="sync_interval">15</integer> <!-- минуты -->
</resources>
```

#### Добавление своих модулей:
```java
// app/src/main/java/com/odoo/addons/YourModule.java
public class ProductionModule extends BaseModel {
    
    // Поля из Odoo
    OColumn name = new OColumn("Name", OVarchar.class);
    OColumn product_id = new OColumn("Product", OSelection.class);
    OColumn quantity = new OColumn("Quantity", OFloat.class);
    OColumn state = new OColumn("State", OSelection.class);
    
    @Override
    public String getModelName() {
        return "mrp.production";
    }
}
```

### Готовые примеры приложений:
- **CRM**: https://github.com/Odoo-mobile/crm
- **Notes**: https://github.com/Odoo-mobile/notes
- **Experience**: https://github.com/Odoo-mobile/experience

---

## 2. W360S Odoo Mobile (React Native) - УНИВЕРСАЛЬНОЕ

### Преимущества:
- ✅ iOS + Android
- ✅ Полностью БЕСПЛАТНО
- ✅ React Native (современный стек)
- ✅ Легко кастомизировать UI
- ✅ Можно использовать свой бренд

### Установка:

```bash
# Предварительные требования
npm install -g react-native-cli

# Клонируем и устанавливаем
git clone https://github.com/W360S/odoo-mobile.git
cd odoo-mobile
npm install

# iOS зависимости (только для Mac)
cd ios && pod install && cd ..
```

### Настройка подключения:

```javascript
// src/config/server.js
export default {
  url: 'https://odoosportspitproject-production.up.railway.app',
  db: 'odoo_sportpit',
  username: 'danila@usafitandjoy.com',
  password: 'admin_sportpit_2024'
}
```

### Запуск:

```bash
# Android
npx react-native run-android

# iOS (только на Mac)
npx react-native run-ios

# Или через Metro bundler
npx react-native start
```

---

## 3. Создание своего приложения с нуля

### Базовый пример подключения к Odoo:

```javascript
// React Native + Odoo XML-RPC
npm install react-native-odoo-xmlrpc

// App.js
import Odoo from 'react-native-odoo-xmlrpc';

const odoo = new Odoo({
  host: 'odoosportspitproject-production.up.railway.app',
  port: 443,
  database: 'odoo_sportpit',
  username: 'danila@usafitandjoy.com',
  password: 'admin_sportpit_2024',
  protocol: 'https'
});

// Подключение
odoo.connect()
  .then(response => {
    console.log('Connected to Odoo');
    // Получаем продукты
    return odoo.search_read('product.product', 
      [['type', '=', 'product']], 
      ['name', 'list_price', 'qty_available']
    );
  })
  .then(products => {
    console.log('Products:', products);
  });
```

---

## 📊 Сравнение open-source решений:

| Критерий | Odoo Mobile Framework | W360S React Native | Свое приложение |
|----------|----------------------|-------------------|-----------------|
| **Цена** | Бесплатно | Бесплатно | Бесплатно |
| **Платформы** | Android | iOS + Android | iOS + Android |
| **Язык** | Java | JavaScript | Любой |
| **Офлайн** | ✅ Есть | ⚠️ Частично | Нужно делать |
| **Документация** | ✅ Отличная | ⚠️ Базовая | Нет |
| **Сложность** | Средняя | Низкая | Высокая |
| **Поддержка** | Официальная | Community | Нет |

---

## 🎯 Что выбрать для SportsPit?

### Рекомендация:
1. **Начните с Odoo Mobile Framework** - он официальный и хорошо документирован
2. **Если нужен iOS** - используйте W360S React Native
3. **Для производства** можно добавить специфичные функции:
   - Сканирование штрих-кодов
   - Фото контроль качества
   - Офлайн учет производства
   - Push-уведомления о критических событиях

### Быстрый старт за 15 минут:

```bash
# 1. Клонируем
git clone https://github.com/Odoo-mobile/framework.git

# 2. Открываем в Android Studio

# 3. Меняем в server_config.xml:
# - host_url на ваш Railway URL
# - database на odoo_sportpit

# 4. Запускаем на эмуляторе или телефоне

# Готово! У вас есть мобильное приложение для Odoo
```

---

## 💡 Дополнительные возможности:

### Добавление сканера штрих-кодов:
```java
// Используем ZXing библиотеку
implementation 'com.journeyapps:zxing-android-embedded:4.3.0'

// Сканирование
IntentIntegrator integrator = new IntentIntegrator(activity);
integrator.setOrientationLocked(false);
integrator.initiateScan();
```

### Push-уведомления:
```java
// Firebase Cloud Messaging
implementation 'com.google.firebase:firebase-messaging:23.0.0'

// Отправка из Odoo
self.env['mail.message'].create({
    'body': 'Критическое событие на производстве!',
    'message_type': 'notification',
    'subtype_id': self.env.ref('mail.mt_comment').id,
    'push_notification': True
})
```

### Офлайн синхронизация:
```java
// Автоматическая синхронизация при появлении интернета
public class SyncService extends Service {
    @Override
    public void onNetworkAvailable() {
        // Синхронизируем локальные изменения
        syncLocalChanges();
        // Получаем обновления с сервера
        fetchServerUpdates();
    }
}
```

---

## 📞 Поддержка и ресурсы:

- **Документация Odoo Mobile**: http://mobile.odoo.co.in/v2/
- **GitHub Issues**: https://github.com/Odoo-mobile/framework/issues
- **Форум Odoo**: https://www.odoo.com/forum/help-1
- **Stack Overflow**: тег `odoo-mobile`

---

## ✅ Итог:

**ДА, у вас есть БЕСПЛАТНЫЕ open-source приложения для Odoo Community!**

- Не нужно платить за лицензии
- Полный контроль над кодом
- Можно кастомизировать под свои нужды
- Можно добавить свой бренд
- Никаких ограничений

Начните с Odoo Mobile Framework уже сегодня - это займет всего 15 минут!