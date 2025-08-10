FROM odoo:17.0

USER root

# Установим postgresql-client для работы с БД
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Копируем файлы
COPY odoo.conf /etc/odoo/odoo.conf
COPY fast_start.sh /usr/local/bin/fast_start.sh

# Даём права
RUN chmod +x /usr/local/bin/fast_start.sh && \
    chown odoo:odoo /etc/odoo/odoo.conf

USER odoo

# Запускаем через fast_start.sh
CMD ["/usr/local/bin/fast_start.sh"]
