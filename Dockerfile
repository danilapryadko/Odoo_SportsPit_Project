FROM odoo:17.0

USER root

# Установка русской локали, московского времени и PostgreSQL клиента
RUN apt-get update && apt-get install -y \
    locales \
    tzdata \
    postgresql-client \
    && sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen ru_RU.UTF-8 \
    && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# Установка переменных окружения
ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru_RU:ru  
ENV LC_ALL=ru_RU.UTF-8
ENV TZ=Europe/Moscow

# Создание директории для кастомных модулей
RUN mkdir -p /mnt/extra-addons

# Установка прав
RUN chown -R odoo:odoo /mnt/extra-addons

# Копируем конфигурацию и скрипты
COPY odoo.conf /etc/odoo/
COPY init_db.sh /usr/local/bin/
RUN chown odoo:odoo /etc/odoo/odoo.conf && \
    chmod +x /usr/local/bin/init_db.sh

USER odoo

# Expose порт
EXPOSE 8069

# Команда запуска через скрипт инициализации
CMD ["/usr/local/bin/init_db.sh"]
