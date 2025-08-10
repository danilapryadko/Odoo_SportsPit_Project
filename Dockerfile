FROM odoo:17.0

USER root

# Копируем конфигурацию
COPY odoo.conf /etc/odoo/odoo.conf
COPY init_db.sh /usr/local/bin/init_db.sh

# Права на выполнение
RUN chmod +x /usr/local/bin/init_db.sh && \
    chown odoo:odoo /etc/odoo/odoo.conf

USER odoo

# Запуск через скрипт
CMD ["/usr/local/bin/init_db.sh"]
