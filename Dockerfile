FROM odoo:17.0

USER root

# Копируем конфигурацию
COPY odoo.conf /etc/odoo/odoo.conf

# Даём права
RUN chown odoo:odoo /etc/odoo/odoo.conf

USER odoo

# Переменные окружения для ускорения запуска
ENV ODOO_RC=/etc/odoo/odoo.conf
ENV DB_HOST=postgresql-odoo.railway.internal
ENV DB_PORT=5432
ENV DB_USER=odoo
ENV DB_PASSWORD=odoo_sportpit_2024

# Запускаем Odoo
CMD ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "odoo_sportpit", "--db-filter=^odoo_sportpit$", "--no-database-list"]
