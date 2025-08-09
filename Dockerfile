FROM odoo:17.0

USER root

# Установка русской локали и московского времени
RUN apt-get update && apt-get install -y \
    locales \
    tzdata \
    python3-pip \
    python3-dev \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    && sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen ru_RU.UTF-8 \
    && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка переменных окружения для русской локали
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8
ENV TZ Europe/Moscow

# Копирование requirements и установка Python зависимостей
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Создание директорий для модулей и данных
RUN mkdir -p /mnt/extra-addons \
    && mkdir -p /var/lib/odoo \
    && mkdir -p /etc/odoo

# Копирование кастомных модулей
COPY ./addons /mnt/extra-addons

# Копирование конфигурации
COPY ./config/odoo.conf /etc/odoo/odoo.conf

# Установка прав доступа
RUN chown -R odoo:odoo /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo \
    && chown -R odoo:odoo /etc/odoo

USER odoo

# Установка рабочей директории
WORKDIR /var/lib/odoo

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default command
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]