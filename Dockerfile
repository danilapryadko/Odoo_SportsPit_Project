FROM odoo:17.0

USER root

# Копируем конфигурацию
COPY odoo.conf /etc/odoo/odoo.conf

# Даём права
RUN chown odoo:odoo /etc/odoo/odoo.conf

USER odoo

# Запускаем Odoo БЕЗ обновления модулей
CMD ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "odoo_sportpit", "--without-demo=all", "--load-language=", "--max-cron-threads=0"]
