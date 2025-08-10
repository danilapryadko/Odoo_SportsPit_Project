#!/bin/bash

# Запуск Odoo с быстрым healthcheck

echo "=== Starting Odoo with Quick Healthcheck ==="

# Создаём простой HTTP сервер для healthcheck на порту 8070
python3 -c "
import http.server
import socketserver
import threading

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/web/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def run_health_server():
    with socketserver.TCPServer(('', 8070), HealthHandler) as httpd:
        httpd.serve_forever()

# Запускаем health сервер в фоне
thread = threading.Thread(target=run_health_server)
thread.daemon = True
thread.start()
print('Health server started on port 8070')

# Ждём вечно
import time
while True:
    time.sleep(1)
" &

# Ждём PostgreSQL
echo "Waiting for PostgreSQL..."
until PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c '\q' 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL is ready!"

# Запускаем Odoo
echo "Starting Odoo server..."
exec odoo \
  --db_host=postgresql-odoo.railway.internal \
  --db_port=5432 \
  --db_user=odoo \
  --db_password=odoo_sportpit_2024 \
  --database=odoo_sportpit \
  --no-database-list \
  --without-demo=all \
  --proxy-mode \
  --workers=0 \
  --max-cron-threads=0 \
  --http-port=8069
