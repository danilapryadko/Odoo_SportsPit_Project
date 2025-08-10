# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    photo_ids = fields.One2many('production.photo', 'production_id', 'Фото-отчеты')
    photo_count = fields.Integer('Количество фото', compute='_compute_photo_count')
    
    # Требования по фото
    require_start_photo = fields.Boolean('Требуется фото начала', default=True)
    require_end_photo = fields.Boolean('Требуется фото завершения', default=True)
    require_quality_photo = fields.Boolean('Требуется фото контроля качества', default=True)
    
    has_start_photo = fields.Boolean('Есть фото начала', compute='_compute_photo_status')
    has_end_photo = fields.Boolean('Есть фото завершения', compute='_compute_photo_status')
    has_quality_photo = fields.Boolean('Есть фото контроля качества', compute='_compute_photo_status')
    
    @api.depends('photo_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photo_ids)
    
    @api.depends('photo_ids', 'photo_ids.photo_type', 'photo_ids.state')
    def _compute_photo_status(self):
        for record in self:
            approved_photos = record.photo_ids.filtered(lambda p: p.state in ['confirmed', 'approved'])
            record.has_start_photo = any(
                p.photo_type == 'workplace_start' for p in approved_photos
            )
            record.has_end_photo = any(
                p.photo_type == 'workplace_end' for p in approved_photos
            )
            record.has_quality_photo = any(
                p.photo_type == 'quality_check' for p in approved_photos
            )
    
    def button_mark_done(self):
        """Переопределяем завершение производства с проверкой фото"""
        for record in self:
            missing_photos = []
            
            if record.require_start_photo and not record.has_start_photo:
                missing_photos.append('фото начала работы')
            
            if record.require_end_photo and not record.has_end_photo:
                missing_photos.append('фото завершения работы')
            
            if record.require_quality_photo and not record.has_quality_photo:
                missing_photos.append('фото контроля качества')
            
            if missing_photos:
                raise UserError(_(
                    'Невозможно завершить производственный заказ.\n'
                    'Необходимо приложить: %s'
                ) % ', '.join(missing_photos))
        
        return super().button_mark_done()
    
    def action_view_photos(self):
        """Просмотр фото-отчетов"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Фото-отчеты',
            'view_mode': 'kanban,tree,form',
            'res_model': 'production.photo',
            'domain': [('production_id', '=', self.id)],
            'context': {
                'default_production_id': self.id,
            }
        }


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    photo_ids = fields.One2many('production.photo', 'workorder_id', 'Фото-отчеты')
    photo_count = fields.Integer('Количество фото', compute='_compute_photo_count')
    
    @api.depends('photo_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photo_ids)
    
    def button_start(self):
        """При начале работы отправляем напоминание о фото"""
        res = super().button_start()
        
        # Здесь можно добавить отправку push-уведомления
        self._send_photo_notification('start')
        
        return res
    
    def button_finish(self):
        """При завершении проверяем наличие фото"""
        for record in self:
            if not any(p.photo_type == 'task_complete' for p in record.photo_ids):
                # Предупреждение, но не блокируем
                pass
        
        res = super().button_finish()
        self._send_photo_notification('finish')
        
        return res
    
    def _send_photo_notification(self, notification_type):
        """Отправка уведомления о необходимости фото"""
        # Заготовка для будущей интеграции с push-уведомлениями
        _logger.info('Напоминание о фото: %s для %s', notification_type, self.name)
