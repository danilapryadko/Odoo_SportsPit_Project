# -*- coding: utf-8 -*-
{
    'name': 'SportsPit Production Photo Reports',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Фото-отчетность для производства спортивного питания',
    'description': """
        Модуль фото-отчетности для производства SportsPit
        ===================================================
        
        Функции:
        --------
        * Обязательное фото рабочего места в начале смены
        * Фото выполненных производственных задач
        * Обязательное фото рабочего места в конце смены
        * GPS координаты и временные метки
        * Офлайн режим с синхронизацией
        * Контроль и одобрение фото руководителем
        
        Интеграция:
        -----------
        * Привязка к производственным заказам (mrp.production)
        * Привязка к рабочим заданиям (mrp.workorder)
        * Интеграция с учетом рабочего времени (hr.attendance)
    """,
    'author': 'SportsPit',
    'website': 'https://sportpit.ru',
    'depends': [
        'base',
        'mrp',
        'hr',
        'hr_attendance',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/production_photo_security.xml',
        'views/production_photo_views.xml',
        'views/mrp_production_views.xml',
        'views/production_photo_menu.xml',
        'data/photo_types_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sportpit_production_photo/static/src/js/photo_widget.js',
            'sportpit_production_photo/static/src/css/photo_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
