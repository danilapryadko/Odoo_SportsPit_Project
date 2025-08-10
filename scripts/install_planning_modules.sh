#!/bin/bash
# Скрипт для установки бесплатных модулей планирования OCA

echo "================================"
echo "УСТАНОВКА МОДУЛЕЙ ПЛАНИРОВАНИЯ"
echo "================================"

cd /Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project

# Создаем папку для OCA модулей
mkdir -p addons/oca_modules
cd addons/oca_modules

echo "📦 Загрузка модулей планирования OCA..."

# Модуль для планирования MRP
git clone --depth 1 --branch 17.0 https://github.com/OCA/manufacture.git manufacture_oca

# Модуль для расширенного календаря
git clone --depth 1 --branch 17.0 https://github.com/OCA/project.git project_oca

# Модуль для Gantt диаграмм
git clone --depth 1 --branch 17.0 https://github.com/OCA/web.git web_oca

echo "✅ Модули загружены!"

# Обновляем файл с путями к модулям
cd ../..
cat >> odoo.conf << EOF

# OCA Modules
addons_path = /mnt/extra-addons,/mnt/extra-addons/oca_modules/manufacture_oca,/mnt/extra-addons/oca_modules/project_oca,/mnt/extra-addons/oca_modules/web_oca
EOF

echo "📝 Конфигурация обновлена"
echo ""
echo "================================"
echo "СЛЕДУЮЩИЕ ШАГИ:"
echo "================================"
echo "1. Закоммитьте изменения в Git"
echo "2. Запушьте в Railway"
echo "3. После деплоя обновите список модулей в Odoo"
echo "4. Установите новые модули через Приложения"
