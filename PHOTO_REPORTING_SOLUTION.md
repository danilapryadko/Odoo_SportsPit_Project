# 📸 Система фото-отчетности для производства SportsPit

## 🎯 Ваши требования:
1. **Фото-отчет о выполнении производственных задач**
2. **Фото рабочего места в начале смены**
3. **Фото рабочего места в конце смены**

## ✅ РЕШЕНИЕ: PWA + Кастомный модуль Odoo

### Архитектура решения:

```
[Мобильное приложение (PWA)] 
        ↓
[Камера телефона]
        ↓
[Odoo 17 API]
        ↓
[Кастомный модуль sportpit_production_photo]
        ↓
[База данных с фото-отчетами]
```

---

## 📦 Шаг 1: Создание модуля Odoo для фото-отчетности

### Структура модуля:
```
sportpit_production_photo/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── production_photo.py
│   └── mrp_production.py
├── views/
│   ├── production_photo_views.xml
│   └── mrp_production_views.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        └── js/
            └── photo_widget.js
```

### __manifest__.py:
```python
{
    'name': 'SportsPit Production Photo Reports',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Фото-отчетность для производства',
    'description': """
        Модуль для фото-отчетности производства:
        - Фото выполненных задач
        - Фото рабочего места в начале/конце смены
        - Контроль качества с фотофиксацией
    """,
    'depends': ['mrp', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/production_photo_views.xml',
        'views/mrp_production_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sportpit_production_photo/static/src/js/photo_widget.js',
        ],
    },
    'installable': True,
    'application': False,
}
```

### models/production_photo.py:
```python
from odoo import models, fields, api
from datetime import datetime
import base64

class ProductionPhoto(models.Model):
    _name = 'production.photo'
    _description = 'Фото-отчет производства'
    _order = 'create_date desc'
    
    name = fields.Char('Описание', required=True)
    photo = fields.Binary('Фото', required=True, attachment=True)
    photo_filename = fields.Char('Имя файла')
    
    # Тип фото
    photo_type = fields.Selection([
        ('task_complete', 'Выполнение задачи'),
        ('workplace_start', 'Рабочее место - начало смены'),
        ('workplace_end', 'Рабочее место - конец смены'),
        ('quality_check', 'Контроль качества'),
        ('issue', 'Проблема/Брак'),
    ], string='Тип фото', required=True)
    
    # Связи
    production_id = fields.Many2one('mrp.production', 'Производственный заказ')
    workorder_id = fields.Many2one('mrp.workorder', 'Рабочее задание')
    employee_id = fields.Many2one('hr.employee', 'Сотрудник', 
                                  default=lambda self: self.env.user.employee_id)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Рабочий центр')
    
    # Метаданные
    timestamp = fields.Datetime('Время фото', default=fields.Datetime.now, required=True)
    gps_location = fields.Char('GPS координаты')
    shift = fields.Selection([
        ('morning', 'Утренняя смена'),
        ('day', 'Дневная смена'),
        ('evening', 'Вечерняя смена'),
        ('night', 'Ночная смена'),
    ], string='Смена')
    
    # Статус
    state = fields.Selection([
        ('draft', 'Черновик'),
        ('confirmed', 'Подтверждено'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ], default='draft', string='Статус')
    
    # Комментарии
    comment = fields.Text('Комментарий')
    supervisor_comment = fields.Text('Комментарий руководителя')
    
    @api.model
    def create_from_mobile(self, vals):
        """API метод для создания фото с мобильного"""
        # Декодируем base64 изображение
        if 'photo_base64' in vals:
            vals['photo'] = vals.pop('photo_base64')
        
        # Автоматически определяем смену
        hour = datetime.now().hour
        if 6 <= hour < 14:
            vals['shift'] = 'morning'
        elif 14 <= hour < 22:
            vals['shift'] = 'day'
        else:
            vals['shift'] = 'night'
            
        # Находим активное рабочее задание сотрудника
        if vals.get('photo_type') == 'task_complete':
            workorder = self.env['mrp.workorder'].search([
                ('state', '=', 'progress'),
                ('workcenter_id', '=', vals.get('workcenter_id'))
            ], limit=1)
            if workorder:
                vals['workorder_id'] = workorder.id
                vals['production_id'] = workorder.production_id.id
        
        return self.create(vals)
    
    def action_approve(self):
        """Одобрить фото-отчет"""
        self.state = 'approved'
        
    def action_reject(self):
        """Отклонить фото-отчет"""
        self.state = 'rejected'


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    photo_ids = fields.One2many('production.photo', 'production_id', 'Фото-отчеты')
    photo_count = fields.Integer('Количество фото', compute='_compute_photo_count')
    
    # Требования по фото
    require_start_photo = fields.Boolean('Требуется фото начала', default=True)
    require_end_photo = fields.Boolean('Требуется фото завершения', default=True)
    has_start_photo = fields.Boolean('Есть фото начала', compute='_compute_photo_status')
    has_end_photo = fields.Boolean('Есть фото завершения', compute='_compute_photo_status')
    
    @api.depends('photo_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photo_ids)
    
    @api.depends('photo_ids')
    def _compute_photo_status(self):
        for record in self:
            record.has_start_photo = any(
                p.photo_type == 'workplace_start' for p in record.photo_ids
            )
            record.has_end_photo = any(
                p.photo_type == 'workplace_end' for p in record.photo_ids
            )
    
    def button_mark_done(self):
        """Переопределяем завершение производства"""
        if self.require_end_photo and not self.has_end_photo:
            raise UserError('Необходимо приложить фото завершения работы!')
        return super().button_mark_done()


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    photo_ids = fields.One2many('production.photo', 'workorder_id', 'Фото-отчеты')
    
    def button_start(self):
        """При начале работы требуем фото"""
        res = super().button_start()
        # Отправляем push-уведомление для фото
        self._send_photo_reminder('workplace_start')
        return res
    
    def button_finish(self):
        """При завершении требуем фото"""
        # Проверяем наличие фото завершения
        if not any(p.photo_type == 'task_complete' for p in self.photo_ids):
            raise UserError('Необходимо приложить фото выполненной работы!')
        res = super().button_finish()
        self._send_photo_reminder('workplace_end')
        return res
    
    def _send_photo_reminder(self, photo_type):
        """Отправка напоминания о необходимости фото"""
        # Здесь будет интеграция с push-уведомлениями
        pass
```

---

## 📱 Шаг 2: PWA приложение с камерой

### index.html:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SportsPit Производство</title>
    <link rel="manifest" href="manifest.json">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: center;
        }
        .container {
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        .photo-button {
            display: block;
            width: 100%;
            padding: 20px;
            margin: 10px 0;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .photo-button.start {
            background: #27ae60;
        }
        .photo-button.end {
            background: #e74c3c;
        }
        .photo-button.task {
            background: #f39c12;
        }
        .photo-preview {
            margin: 20px 0;
            text-align: center;
        }
        .photo-preview img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .task-list {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
        .task-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .task-item:last-child {
            border-bottom: none;
        }
        .task-status {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
        }
        .task-status.pending {
            background: #fff3cd;
            color: #856404;
        }
        .task-status.completed {
            background: #d4edda;
            color: #155724;
        }
        .camera-icon {
            width: 24px;
            height: 24px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📸 SportsPit Производство</h1>
        <div id="employee-name"></div>
        <div id="current-shift"></div>
    </div>

    <div class="container">
        <!-- Кнопки для фото -->
        <button class="photo-button start" onclick="takePhoto('workplace_start')">
            📷 Фото начала смены
        </button>
        
        <button class="photo-button task" onclick="takePhoto('task_complete')">
            ✅ Фото выполненной задачи
        </button>
        
        <button class="photo-button end" onclick="takePhoto('workplace_end')">
            🏁 Фото конца смены
        </button>

        <!-- Список текущих задач -->
        <div class="task-list">
            <h3>Текущие задачи:</h3>
            <div id="tasks-container"></div>
        </div>

        <!-- Предпросмотр фото -->
        <div id="photo-preview" class="photo-preview" style="display:none;">
            <h3>Последнее фото:</h3>
            <img id="preview-image" src="" alt="Preview">
            <p id="photo-status"></p>
        </div>

        <!-- Статус -->
        <div id="status-message"></div>
    </div>

    <!-- Скрытый input для камеры -->
    <input type="file" id="camera-input" accept="image/*" capture="environment" style="display:none;">

    <script>
        // Конфигурация
        const ODOO_URL = 'https://odoosportspitproject-production.up.railway.app';
        const API_DB = 'odoo_sportpit';
        
        // Данные сотрудника (получаем при входе)
        let employeeData = {
            id: null,
            name: '',
            workcenter_id: null
        };

        // Инициализация
        document.addEventListener('DOMContentLoaded', async () => {
            // Регистрируем Service Worker для офлайн работы
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('sw.js');
            }

            // Получаем данные сотрудника
            await authenticateEmployee();
            
            // Загружаем текущие задачи
            await loadCurrentTasks();
            
            // Определяем текущую смену
            updateShiftInfo();
            
            // Проверяем, были ли сделаны обязательные фото
            checkRequiredPhotos();
        });

        // Функция для съемки фото
        async function takePhoto(photoType) {
            const input = document.getElementById('camera-input');
            
            // Обработчик выбора файла
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;

                // Сжимаем изображение
                const compressedImage = await compressImage(file);
                
                // Получаем GPS координаты
                const location = await getCurrentLocation();
                
                // Отправляем на сервер
                await uploadPhoto({
                    photo_base64: compressedImage,
                    photo_type: photoType,
                    employee_id: employeeData.id,
                    workcenter_id: employeeData.workcenter_id,
                    gps_location: location,
                    timestamp: new Date().toISOString(),
                    name: getPhotoDescription(photoType)
                });
                
                // Показываем превью
                showPhotoPreview(compressedImage);
            };
            
            // Открываем камеру
            input.click();
        }

        // Сжатие изображения
        function compressImage(file) {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        
                        // Максимальный размер 1920px
                        const maxSize = 1920;
                        let width = img.width;
                        let height = img.height;
                        
                        if (width > height && width > maxSize) {
                            height = (maxSize / width) * height;
                            width = maxSize;
                        } else if (height > maxSize) {
                            width = (maxSize / height) * width;
                            height = maxSize;
                        }
                        
                        canvas.width = width;
                        canvas.height = height;
                        ctx.drawImage(img, 0, 0, width, height);
                        
                        // Конвертируем в base64 с качеством 0.8
                        const base64 = canvas.toDataURL('image/jpeg', 0.8);
                        resolve(base64.split(',')[1]);
                    };
                    img.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        }

        // Получение GPS координат
        function getCurrentLocation() {
            return new Promise((resolve) => {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve(`${position.coords.latitude},${position.coords.longitude}`);
                        },
                        () => resolve(null)
                    );
                } else {
                    resolve(null);
                }
            });
        }

        // Отправка фото на сервер
        async function uploadPhoto(data) {
            try {
                const response = await fetch(`${ODOO_URL}/web/dataset/call_kw`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            model: 'production.photo',
                            method: 'create_from_mobile',
                            args: [data],
                            kwargs: {}
                        }
                    })
                });

                const result = await response.json();
                
                if (result.error) {
                    throw new Error(result.error.message);
                }

                showStatus('Фото успешно отправлено!', 'success');
                
                // Обновляем статус выполненных фото
                checkRequiredPhotos();
                
                // Если это фото задачи, обновляем список
                if (data.photo_type === 'task_complete') {
                    await loadCurrentTasks();
                }
                
                return result;
            } catch (error) {
                console.error('Ошибка отправки фото:', error);
                showStatus('Ошибка отправки. Фото сохранено локально.', 'error');
                
                // Сохраняем локально для последующей отправки
                savePhotoLocally(data);
            }
        }

        // Локальное сохранение фото (для офлайн режима)
        function savePhotoLocally(photoData) {
            const photos = JSON.parse(localStorage.getItem('pending_photos') || '[]');
            photos.push({
                ...photoData,
                saved_at: new Date().toISOString()
            });
            localStorage.setItem('pending_photos', JSON.stringify(photos));
        }

        // Синхронизация локальных фото при появлении интернета
        window.addEventListener('online', async () => {
            const photos = JSON.parse(localStorage.getItem('pending_photos') || '[]');
            for (const photo of photos) {
                await uploadPhoto(photo);
            }
            localStorage.removeItem('pending_photos');
        });

        // Загрузка текущих задач
        async function loadCurrentTasks() {
            try {
                const response = await fetch(`${ODOO_URL}/web/dataset/call_kw`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            model: 'mrp.workorder',
                            method: 'search_read',
                            args: [[['state', 'in', ['ready', 'progress']]]],
                            kwargs: {
                                fields: ['name', 'product_id', 'qty_production', 'state'],
                                limit: 10
                            }
                        }
                    })
                });

                const result = await response.json();
                displayTasks(result.result);
            } catch (error) {
                console.error('Ошибка загрузки задач:', error);
            }
        }

        // Отображение задач
        function displayTasks(tasks) {
            const container = document.getElementById('tasks-container');
            container.innerHTML = tasks.map(task => `
                <div class="task-item">
                    <div>
                        <strong>${task.name}</strong><br>
                        <small>Количество: ${task.qty_production}</small>
                    </div>
                    <span class="task-status ${task.state === 'progress' ? 'pending' : 'completed'}">
                        ${task.state === 'progress' ? 'В работе' : 'Готово'}
                    </span>
                </div>
            `).join('');
        }

        // Проверка обязательных фото
        async function checkRequiredPhotos() {
            const today = new Date().toDateString();
            const startPhotoKey = `start_photo_${today}`;
            const endPhotoKey = `end_photo_${today}`;
            
            const hasStartPhoto = localStorage.getItem(startPhotoKey);
            const hasEndPhoto = localStorage.getItem(endPhotoKey);
            
            // Обновляем UI индикаторы
            updatePhotoButtons(hasStartPhoto, hasEndPhoto);
        }

        // Обновление кнопок фото
        function updatePhotoButtons(hasStart, hasEnd) {
            const startBtn = document.querySelector('.photo-button.start');
            const endBtn = document.querySelector('.photo-button.end');
            
            if (hasStart) {
                startBtn.innerHTML = '✅ Фото начала смены (сделано)';
                startBtn.disabled = true;
            }
            
            if (hasEnd) {
                endBtn.innerHTML = '✅ Фото конца смены (сделано)';
                endBtn.disabled = true;
            }
        }

        // Вспомогательные функции
        function getPhotoDescription(type) {
            const descriptions = {
                'workplace_start': 'Рабочее место - начало смены',
                'workplace_end': 'Рабочее место - конец смены',
                'task_complete': 'Выполненная задача',
                'quality_check': 'Контроль качества',
                'issue': 'Обнаруженная проблема'
            };
            return descriptions[type] || 'Фото производства';
        }

        function updateShiftInfo() {
            const hour = new Date().getHours();
            let shift = '';
            
            if (hour >= 6 && hour < 14) {
                shift = 'Утренняя смена (6:00 - 14:00)';
            } else if (hour >= 14 && hour < 22) {
                shift = 'Дневная смена (14:00 - 22:00)';
            } else {
                shift = 'Ночная смена (22:00 - 6:00)';
            }
            
            document.getElementById('current-shift').textContent = shift;
        }

        function showPhotoPreview(base64) {
            const preview = document.getElementById('photo-preview');
            const img = document.getElementById('preview-image');
            img.src = 'data:image/jpeg;base64,' + base64;
            preview.style.display = 'block';
        }

        function showStatus(message, type) {
            const status = document.getElementById('status-message');
            status.className = `status ${type}`;
            status.textContent = message;
            setTimeout(() => {
                status.textContent = '';
                status.className = '';
            }, 5000);
        }

        // Заглушка для аутентификации
        async function authenticateEmployee() {
            // В реальном приложении здесь будет вход через Odoo
            employeeData = {
                id: 1,
                name: 'Иван Иванов',
                workcenter_id: 1
            };
            document.getElementById('employee-name').textContent = employeeData.name;
        }
    </script>
</body>
</html>
```

### Service Worker (sw.js):
```javascript
const CACHE_NAME = 'sportpit-v1';
const urlsToCache = [
    '/',
    '/manifest.json',
    '/offline.html'
];

// Установка Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

// Обработка запросов
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Возвращаем кэшированный ответ или делаем запрос
                return response || fetch(event.request);
            })
            .catch(() => {
                // Если офлайн, показываем офлайн страницу
                return caches.match('/offline.html');
            })
    );
});

// Фоновая синхронизация
self.addEventListener('sync', event => {
    if (event.tag === 'sync-photos') {
        event.waitUntil(syncPendingPhotos());
    }
});

async function syncPendingPhotos() {
    // Отправляем все несинхронизированные фото
    const photos = await getPendingPhotos();
    for (const photo of photos) {
        await uploadPhoto(photo);
    }
}
```

---

## 🚀 Шаг 3: Быстрое развертывание

### 1. Установка модуля в Odoo:
```bash
# Копируем модуль в addons
cp -r sportpit_production_photo /odoo/custom/addons/

# Обновляем список модулей
python odoo-bin -c /etc/odoo/odoo.conf -u sportpit_production_photo

# Или через интерфейс:
# Приложения → Обновить список → Найти "SportsPit Production Photo" → Установить
```

### 2. Настройка PWA:
```bash
# В папке Odoo создаем статические файлы
cd /odoo/custom/addons/sportpit_production_photo/static/
mkdir pwa
cd pwa

# Копируем файлы index.html, manifest.json, sw.js

# Настраиваем nginx для обслуживания PWA
location /production-app {
    alias /odoo/custom/addons/sportpit_production_photo/static/pwa;
    try_files $uri $uri/ /index.html;
}
```

### 3. Добавление на телефон:
1. Откройте Chrome на Android
2. Перейдите на https://yourserver.com/production-app
3. Нажмите "Добавить на главный экран"
4. Готово!

---

## 📊 Отчеты и аналитика

### Дашборд для руководителя:
```xml
<!-- views/production_photo_dashboard.xml -->
<record id="production_photo_dashboard" model="ir.ui.view">
    <field name="name">Фото-отчеты производства</field>
    <field name="model">production.photo</field>
    <field name="arch" type="xml">
        <kanban>
            <field name="photo"/>
            <field name="name"/>
            <field name="employee_id"/>
            <field name="timestamp"/>
            <field name="photo_type"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_global_click">
                        <div class="o_kanban_image">
                            <img t-att-src="kanban_image('production.photo', 'photo', record.id.raw_value)"/>
                        </div>
                        <div class="oe_kanban_details">
                            <strong><field name="name"/></strong>
                            <div>
                                <field name="employee_id"/>
                                <field name="timestamp" widget="datetime"/>
                            </div>
                            <div>
                                <span t-if="record.state.raw_value == 'approved'" 
                                      class="badge badge-success">Одобрено</span>
                                <span t-elif="record.state.raw_value == 'rejected'" 
                                      class="badge badge-danger">Отклонено</span>
                                <span t-else="" class="badge badge-warning">На проверке</span>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

## ✅ Преимущества решения:

1. **Простота использования**
   - Интуитивный интерфейс
   - Работает на любом телефоне
   - Не требует установки (PWA)

2. **Контроль производства**
   - Обязательные фото начала/конца смены
   - Фотофиксация выполненных задач
   - GPS метки и временные штампы

3. **Офлайн работа**
   - Фото сохраняются локально
   - Автоматическая синхронизация при появлении интернета

4. **Интеграция с Odoo**
   - Привязка к производственным заказам
   - Связь с рабочими заданиями
   - Отчеты для руководства

---

## 💰 Стоимость внедрения:

### Вариант 1: Сделать самим (1-2 недели)
- Разработка модуля: 40 часов
- Настройка PWA: 20 часов
- Тестирование: 20 часов
- **Итого: ~80 часов работы**

### Вариант 2: Заказать разработку
- Модуль Odoo: $2,000-3,000
- PWA приложение: $1,000-2,000
- Интеграция и настройка: $500-1,000
- **Итого: $3,500-6,000**

### Вариант 3: Готовое решение
- WebKul или аналоги: $500-1,500
- Настройка под ваши нужды: $500-1,000
- **Итого: $1,000-2,500**

---

## 🎯 Рекомендация:

Начните с PWA + простого модуля для фото. Это можно сделать за неделю и начать использовать сразу. Потом постепенно добавляйте функции:
- Push-уведомления о необходимости фото
- Распознавание QR-кодов на рабочих местах
- Автоматическая проверка качества фото через AI
- Интеграция с системой KPI сотрудников