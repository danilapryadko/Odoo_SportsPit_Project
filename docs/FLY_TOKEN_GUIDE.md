# Инструкция по работе с токеном Fly.io

## Сохранение токена

### Метод 1: Через конфигурационный файл (рекомендуется)
```bash
# Создать директорию если не существует
mkdir -p ~/.fly

# Сохранить токен в файл конфигурации
echo 'access_token: "YOUR_FLY_TOKEN"' > ~/.fly/config.yml
```

### Метод 2: Через переменную окружения
```bash
export FLY_API_TOKEN="YOUR_FLY_TOKEN"
```

### Метод 3: В команде напрямую
```bash
flyctl status --access-token "YOUR_FLY_TOKEN"
```

## Текущий токен проекта
```
FlyV1 fm2_lJPECAAAAAAACbNKxBCU9nu4mDvzbB+655I0RFkmwrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABK0YB8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDw4TnXcT3mBisS7qnmqFvhFDNinJZHOrwIRIYtX3pC460v2NZe5UbY62eBMsj4xxaaR5uO8byREaeZT+EbETr3nduxuK7p51ZRMqsTkLqqCqlMnAmTrL+PJFBAb2yYv6K8l1caW1/iXDi1IIVJnvfF++IyuKfalH6HRCJzPNMEBy6HHV2KI+ke2KZxLCA2SlAORgc4AjoHeHwWRgqdidWlsZGVyH6J3Zx8BxCBdIP4sClCVPbR8Yei9kOBbMVJo8U+i0I5sAOA1wRjn0g==,fm2_lJPETr3nduxuK7p51ZRMqsTkLqqCqlMnAmTrL+PJFBAb2yYv6K8l1caW1/iXDi1IIVJnvfF++IyuKfalH6HRCJzPNMEBy6HHV2KI+ke2KZxLCA2SlAORgc4AjoHeHwWRgqdidWlsZGVyH6J3Zx8BxCBdIP4sClCVPbR8Yei9kOBbMVJo8U+i0I5sAOA1wRjn0g==
```

## Проверка токена
```bash
# Проверить что токен работает
flyctl auth whoami

# Проверить приложения
flyctl apps list
```

## Основные команды для работы с приложением

### Информация о приложении
```bash
flyctl status --app odoo-sportspit-project
```

### Запуск/остановка приложения
```bash
# Запустить 1 экземпляр
flyctl scale count 1 --app odoo-sportspit-project --yes

# Остановить все экземпляры
flyctl scale count 0 --app odoo-sportspit-project --yes
```

### Логи
```bash
# Просмотр логов
flyctl logs --app odoo-sportspit-project

# Следить за логами в реальном времени
flyctl logs --app odoo-sportspit-project --tail
```

### Деплой
```bash
# Деплой из текущей директории
flyctl deploy --app odoo-sportspit-project

# Деплой с конкретным Dockerfile
flyctl deploy --app odoo-sportspit-project --dockerfile Dockerfile.fly
```

### База данных PostgreSQL
```bash
# Создать новую БД
flyctl postgres create --name odoo-db --region ams

# Подключить БД к приложению
flyctl postgres attach odoo-db --app odoo-sportspit-project

# Список БД
flyctl postgres list
```

### Секреты и переменные окружения
```bash
# Список секретов
flyctl secrets list --app odoo-sportspit-project

# Установить секрет
flyctl secrets set KEY=value --app odoo-sportspit-project

# Удалить секрет
flyctl secrets unset KEY --app odoo-sportspit-project
```

## Troubleshooting

### Если токен не работает
1. Проверить что токен правильно сохранен в `~/.fly/config.yml`
2. Убедиться что в токене есть кавычки: `access_token: "TOKEN"`
3. Попробовать использовать переменную окружения FLY_API_TOKEN

### Если приложение suspended
```bash
flyctl scale count 1 --app odoo-sportspit-project --yes
```

### Проверка состояния машин
```bash
flyctl machine list --app odoo-sportspit-project
flyctl machine start MACHINE_ID --app odoo-sportspit-project
```