from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Nutrition Facts
    is_sports_nutrition = fields.Boolean(
        string='Спортивное питание',
        default=False
    )
    
    calories = fields.Float(
        string='Калории (ккал/100г)',
        digits=(10, 2),
        help='Калорийность на 100 грамм продукта'
    )
    
    protein = fields.Float(
        string='Белки (г/100г)',
        digits=(10, 2),
        help='Содержание белка на 100 грамм'
    )
    
    carbohydrates = fields.Float(
        string='Углеводы (г/100г)',
        digits=(10, 2),
        help='Содержание углеводов на 100 грамм'
    )
    
    fats = fields.Float(
        string='Жиры (г/100г)',
        digits=(10, 2),
        help='Содержание жиров на 100 грамм'
    )
    
    fiber = fields.Float(
        string='Клетчатка (г/100г)',
        digits=(10, 2),
        help='Содержание клетчатки на 100 грамм'
    )
    
    sugar = fields.Float(
        string='Сахар (г/100г)',
        digits=(10, 2),
        help='Содержание сахара на 100 грамм'
    )
    
    sodium = fields.Float(
        string='Натрий (мг/100г)',
        digits=(10, 2),
        help='Содержание натрия на 100 грамм'
    )
    
    # Sports Nutrition Specific
    sports_category_id = fields.Many2one(
        'sports.nutrition.category',
        string='Категория спортпита'
    )
    
    serving_size = fields.Float(
        string='Размер порции (г)',
        default=30.0,
        help='Рекомендуемый размер одной порции'
    )
    
    servings_per_container = fields.Float(
        string='Порций в упаковке',
        compute='_compute_servings_per_container',
        store=True
    )
    
    # Ingredients and Allergens
    ingredients = fields.Text(
        string='Состав',
        help='Полный список ингредиентов'
    )
    
    allergens = fields.Text(
        string='Аллергены',
        help='Информация об аллергенах'
    )
    
    # Quality and Certification
    batch_tracking = fields.Boolean(
        string='Партионный учет',
        default=True,
        help='Требуется отслеживание по партиям'
    )
    
    shelf_life_days = fields.Integer(
        string='Срок годности (дней)',
        default=365,
        help='Срок годности продукта в днях'
    )
    
    storage_conditions = fields.Text(
        string='Условия хранения',
        default='Хранить в сухом прохладном месте'
    )
    
    # Certifications
    has_mercury_cert = fields.Boolean(
        string='Сертификат Меркурий',
        default=False
    )
    
    has_chestny_znak = fields.Boolean(
        string='Маркировка Честный ЗНАК',
        default=False
    )
    
    certificate_ids = fields.One2many(
        'product.certificate',
        'product_tmpl_id',
        string='Сертификаты'
    )
    
    @api.depends('weight', 'serving_size')
    def _compute_servings_per_container(self):
        for product in self:
            if product.weight and product.serving_size:
                # Convert weight from kg to g
                weight_in_grams = product.weight * 1000
                product.servings_per_container = weight_in_grams / product.serving_size
            else:
                product.servings_per_container = 0
    
    @api.constrains('protein', 'carbohydrates', 'fats')
    def _check_macros_total(self):
        for product in self:
            if product.is_sports_nutrition:
                total = product.protein + product.carbohydrates + product.fats
                if total > 100:
                    raise ValidationError(
                        'Сумма БЖУ не может превышать 100г на 100г продукта!'
                    )
    
    @api.onchange('protein', 'carbohydrates', 'fats')
    def _onchange_calculate_calories(self):
        if self.is_sports_nutrition:
            # Калории = Белки*4 + Углеводы*4 + Жиры*9
            self.calories = (
                self.protein * 4 + 
                self.carbohydrates * 4 + 
                self.fats * 9
            )
    
    def calculate_nutrition_per_serving(self):
        """Расчет пищевой ценности на порцию"""
        self.ensure_one()
        if not self.serving_size:
            return {}
        
        ratio = self.serving_size / 100.0
        return {
            'calories': self.calories * ratio,
            'protein': self.protein * ratio,
            'carbohydrates': self.carbohydrates * ratio,
            'fats': self.fats * ratio,
            'fiber': self.fiber * ratio,
            'sugar': self.sugar * ratio,
            'sodium': self.sodium * ratio,
        }


class SportsNutritionCategory(models.Model):
    _name = 'sports.nutrition.category'
    _description = 'Категория спортивного питания'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Название',
        required=True
    )
    
    code = fields.Char(
        string='Код',
        required=True
    )
    
    parent_id = fields.Many2one(
        'sports.nutrition.category',
        string='Родительская категория'
    )
    
    child_ids = fields.One2many(
        'sports.nutrition.category',
        'parent_id',
        string='Подкатегории'
    )
    
    sequence = fields.Integer(
        string='Последовательность',
        default=10
    )
    
    description = fields.Text(
        string='Описание'
    )
    
    active = fields.Boolean(
        default=True
    )


class ProductCertificate(models.Model):
    _name = 'product.certificate'
    _description = 'Сертификат продукта'
    
    name = fields.Char(
        string='Номер сертификата',
        required=True
    )
    
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Продукт',
        required=True
    )
    
    certificate_type = fields.Selection([
        ('quality', 'Сертификат качества'),
        ('conformity', 'Сертификат соответствия'),
        ('mercury', 'Меркурий'),
        ('chestny_znak', 'Честный ЗНАК'),
        ('other', 'Другое')
    ], string='Тип сертификата', required=True)
    
    issue_date = fields.Date(
        string='Дата выдачи',
        required=True
    )
    
    expiry_date = fields.Date(
        string='Дата окончания',
        required=True
    )
    
    issuer = fields.Char(
        string='Кем выдан'
    )
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Файлы сертификата'
    )