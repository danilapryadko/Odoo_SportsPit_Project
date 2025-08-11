FROM odoo:17.0

USER root

# Install PostgreSQL client for database operations
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy Odoo configuration
COPY odoo.conf /etc/odoo/odoo.conf

# Create startup script for Railway
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Starting Odoo on Railway ==="\n\
echo "Database host: ${PGHOST:-localhost}"\n\
echo "Database port: ${PGPORT:-5432}"\n\
echo "Database user: ${PGUSER:-odoo}"\n\
echo "Database name: ${PGDATABASE:-odoo_sportpit}"\n\
\n\
# Wait for PostgreSQL to be ready\n\
if [ -n "$PGHOST" ]; then\n\
    echo "Waiting for PostgreSQL to be ready..."\n\
    for i in $(seq 1 30); do\n\
        if PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "SELECT 1" >/dev/null 2>&1; then\n\
            echo "PostgreSQL is ready!"\n\
            break\n\
        fi\n\
        echo "Waiting for PostgreSQL... ($i/30)"\n\
        sleep 2\n\
    done\n\
fi\n\
\n\
# Create database if it doesn'"'"'t exist\n\
if [ -n "$PGHOST" ]; then\n\
    echo "Ensuring database exists..."\n\
    PGPASSWORD=$PGPASSWORD createdb -h $PGHOST -p $PGPORT -U $PGUSER $PGDATABASE 2>/dev/null || echo "Database already exists"\n\
fi\n\
\n\
# Update odoo.conf with Railway environment variables\n\
if [ -n "$PGHOST" ]; then\n\
    sed -i "s/^db_host = .*/db_host = $PGHOST/" /etc/odoo/odoo.conf\n\
    sed -i "s/^db_port = .*/db_port = $PGPORT/" /etc/odoo/odoo.conf\n\
    sed -i "s/^db_user = .*/db_user = $PGUSER/" /etc/odoo/odoo.conf\n\
    sed -i "s/^db_password = .*/db_password = $PGPASSWORD/" /etc/odoo/odoo.conf\n\
    sed -i "s/^db_name = .*/db_name = $PGDATABASE/" /etc/odoo/odoo.conf\n\
fi\n\
\n\
# Start Odoo\n\
echo "Starting Odoo server..."\n\
exec odoo -c /etc/odoo/odoo.conf --db-filter=$PGDATABASE' > /entrypoint.sh && \
chmod +x /entrypoint.sh

# Set proper permissions
RUN chown -R odoo:odoo /etc/odoo

USER odoo

# Expose Odoo port
EXPOSE 8069

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Start Odoo
ENTRYPOINT ["/entrypoint.sh"]