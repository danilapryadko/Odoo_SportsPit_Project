FROM odoo:17.0

USER root

# Установка русской локали и московского времени
RUN apt-get update && apt-get install -y \
    locales \
    tzdata \
    python3-pip \
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

# Копируем конфигурацию
COPY odoo.conf /etc/odoo/
RUN chown odoo:odoo /etc/odoo/odoo.conf

USER odoo

# Expose порт
EXPOSE 8069

# Команда запуска
CMD ["odoo"]
