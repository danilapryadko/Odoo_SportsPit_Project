# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import base64
import logging

_logger = logging.getLogger(__name__)


class ProductionPhoto(models.Model):
    _name = 'production.photo'
    _description = 'Фото-отчет производства'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Описание', required=True, tracking=True)
    photo = fields.Binary('Фото', required=True, attachment=True)
    photo_filename = fields.Char('Имя файла')
    
    # Тип фото
    photo_type = fields.Selection([
        ('workplace_start', 'Рабочее место - начало смены'),
        ('workplace_end', 'Рабочее место - конец смены'),
        ('task_complete', 'Выполнение задачи'),
        ('quality_check', 'Контроль качества'),
        ('issue', 'Проблема/Брак'),
    ], string='Тип фото', required=True, tracking=True)
    
    # Связи
    production_id = fields.Many2one('mrp.production', 'Производственный заказ', tracking=True)
    workorder_id = fields.Many2one('mrp.workorder', 'Рабочее задание')
    employee_id = fields.Many2one(
        'hr.employee', 
        'Сотрудник',
        default=lambda self: self.env.user.employee_id,
        required=True,
        tracking=True
    )
    workcenter_id = fields.Many2one('mrp.workcenter', 'Рабочий центр')
    
    # Метаданные
    timestamp = fields.Datetime('Время фото', default=fields.Datetime.now, required=True)
    gps_location = fields.Char('GPS координаты')
    gps_latitude = fields.Float('Широта', digits=(10, 6))
    gps_longitude = fields.Float('Долгота', digits=(10, 6))
    
    shift = fields.Selection([
        ('morning', 'Утренняя смена (6:00-14:00)'),
        ('day', 'Дневная смена (14:00-22:00)'),
        ('night', 'Ночная смена (22:00-6:00)'),
    ], string='Смена', compute='_compute_shift', store=True)
    
    # Статус
    state = fields.Selection([
        ('draft', 'Черновик'),
        ('confirmed', 'Подтверждено'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ], default='draft', string='Статус', tracking=True)
    
    # Комментарии
    comment = fields.Text('Комментарий сотрудника')
    supervisor_comment = fields.Text('Комментарий руководителя')
    supervisor_id = fields.Many2one('hr.employee', 'Проверил')
    approval_date = fields.Datetime('Дата проверки')
    
    # Технические поля
    is_offline_sync = fields.Boolean('Синхронизировано офлайн', default=False)
    device_info = fields.Char('Информация об устройстве')
    
    @api.depends('timestamp')
    def _compute_shift(self):
        """Автоматическое определение смены по времени"""
        for record in self:
            if record.timestamp:
                hour = record.timestamp.hour
                if 6 <= hour < 14:
                    record.shift = 'morning'
                elif 14 <= hour < 22:
                    record.shift = 'day'
                else:
                    record.shift = 'night'
    
    @api.model
    def create_from_mobile(self, vals):
        """API метод для создания фото с мобильного устройства"""
        try:
            # Декодируем base64 изображение если нужно
            if 'photo_base64' in vals:
                vals['photo'] = vals.pop('photo_base64')
            
            # Парсим GPS координаты
            if 'gps_location' in vals and vals['gps_location']:
                try:
                    lat, lon = vals['gps_location'].split(',')
                    vals['gps_latitude'] = float(lat)
                    vals['gps_longitude'] = float(lon)
                except:
                    _logger.warning('Не удалось распарсить GPS координаты: %s', vals['gps_location'])
            
            # Находим сотрудника по user_id если не передан employee_id
            if not vals.get('employee_id'):
                employee = self.env.user.employee_id
                if employee:
                    vals['employee_id'] = employee.id
                else:
                    raise ValidationError('Сотрудник не найден для текущего пользователя')
            
            # Находим активное рабочее задание если это фото задачи
            if vals.get('photo_type') == 'task_complete' and vals.get('workcenter_id'):
                workorder = self.env['mrp.workorder'].search([
                    ('state', '=', 'progress'),
                    ('workcenter_id', '=', vals.get('workcenter_id'))
                ], limit=1)
                if workorder:
                    vals['workorder_id'] = workorder.id
                    vals['production_id'] = workorder.production_id.id
            
            # Создаем запись
            photo = self.create(vals)
            
            # Автоматически подтверждаем
            photo.action_confirm()
            
            return {
                'success': True,
                'photo_id': photo.id,
                'message': 'Фото успешно сохранено'
            }
            
        except Exception as e:
            _logger.error('Ошибка при создании фото: %s', str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def action_confirm(self):
        """Подтвердить фото"""
        self.state = 'confirmed'
        
    def action_approve(self):
        """Одобрить фото-отчет"""
        self.write({
            'state': 'approved',
            'supervisor_id': self.env.user.employee_id.id,
            'approval_date': fields.Datetime.now()
        })
        
    def action_reject(self):
        """Отклонить фото-отчет"""
        self.write({
            'state': 'rejected',
            'supervisor_id': self.env.user.employee_id.id,
            'approval_date': fields.Datetime.now()
        })
    
    @api.model
    def check_shift_photos(self, employee_id, date=None):
        """Проверка наличия обязательных фото смены"""
        if not date:
            date = fields.Date.today()
        
        domain = [
            ('employee_id', '=', employee_id),
            ('timestamp', '>=', datetime.combine(date, datetime.min.time())),
            ('timestamp', '<=', datetime.combine(date, datetime.max.time())),
        ]
        
        photos = self.search(domain)
        
        return {
            'has_start_photo': any(p.photo_type == 'workplace_start' for p in photos),
            'has_end_photo': any(p.photo_type == 'workplace_end' for p in photos),
            'task_photos_count': len(photos.filtered(lambda p: p.photo_type == 'task_complete')),
            'total_photos': len(photos)
        }
    
    @api.model
    def get_employee_stats(self, employee_id, date_from=None, date_to=None):
        """Получить статистику фото сотрудника"""
        if not date_from:
            date_from = fields.Date.today() - timedelta(days=30)
        if not date_to:
            date_to = fields.Date.today()
        
        domain = [
            ('employee_id', '=', employee_id),
            ('timestamp', '>=', date_from),
            ('timestamp', '<=', date_to),
        ]
        
        photos = self.search(domain)
        
        return {
            'total': len(photos),
            'approved': len(photos.filtered(lambda p: p.state == 'approved')),
            'rejected': len(photos.filtered(lambda p: p.state == 'rejected')),
            'pending': len(photos.filtered(lambda p: p.state in ['draft', 'confirmed'])),
            'by_type': {
                'workplace_start': len(photos.filtered(lambda p: p.photo_type == 'workplace_start')),
                'workplace_end': len(photos.filtered(lambda p: p.photo_type == 'workplace_end')),
                'task_complete': len(photos.filtered(lambda p: p.photo_type == 'task_complete')),
                'quality_check': len(photos.filtered(lambda p: p.photo_type == 'quality_check')),
                'issue': len(photos.filtered(lambda p: p.photo_type == 'issue')),
            }
        }
