{
    'name': 'Sports Nutrition Base',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Базовый модуль для производства спортивного питания',
    'description': """
        Модуль для управления производством спортивного питания:
        - Расширенные поля продуктов (БЖУ, калории)
        - Категории спортпита
        - Калькулятор пищевой ценности
        - Шаблоны этикеток
    """,
    'author': 'SportsPit Company',
    'website': 'https://sportspit.ru',
    'depends': [
        'base',
        'product',
        'mrp',
        'stock',
        'quality_control',
        'uom',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/sports_nutrition_security.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/nutrition_calculator_views.xml',
        'views/menu_views.xml',
        'data/product_categories.xml',
        'data/uom_data.xml',
        'reports/product_label_report.xml',
    ],
    'demo': [
        'demo/demo_products.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}