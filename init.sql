-- Создание базы данных для Odoo
CREATE DATABASE odoo_sportpit WITH OWNER odoo ENCODING 'UTF8';

-- Даём все права пользователю odoo
GRANT ALL PRIVILEGES ON DATABASE odoo_sportpit TO odoo;

-- Создаём пользователя если не существует
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user
      WHERE  usename = 'odoo') THEN
      CREATE USER odoo WITH PASSWORD 'odoo_sportpit_2024';
   END IF;
END
$do$;
