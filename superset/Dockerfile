FROM apache/superset:5.0.0

USER root
RUN python -m ensurepip --upgrade || true && \
    python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir psycopg2-binary==2.9.9

RUN mkdir -p /app/superset/static/assets/images/branding && \
    mkdir -p /app/.venv/lib/python3.10/site-packages/flask_appbuilder/templates/appbuilder/general/security/

COPY ./branding/ /app/superset/static/assets/images/branding/

COPY ./overrides/login_db.html/login_db.html /app/.venv/lib/python3.10/site-packages/flask_appbuilder/templates/appbuilder/general/security/login_db.html
COPY ./overrides/login_oauth.html/login_oauth.html /app/.venv/lib/python3.10/site-packages/flask_appbuilder/templates/appbuilder/general/security/login_oauth.html

RUN chown -R superset:superset /app/superset/static/assets/images/branding && \
    chown superset:superset /app/.venv/lib/python3.10/site-packages/flask_appbuilder/templates/appbuilder/general/security/login_db.html && \
    chown superset:superset /app/.venv/lib/python3.10/site-packages/flask_appbuilder/templates/appbuilder/general/security/login_oauth.html

# Entrypoint script
RUN cat > /entrypoint.sh << 'EOF'
#!/bin/bash
set -e

PORT=${PORT:-10000}

echo "=== Inicializando Superset ==="
superset db upgrade

echo "Creando usuario administrador..."
superset fab create-admin \
    --username ${ADMIN_USER:-admin} \
    --password ${SUPERSET_ADMIN_PASSWORD:-admin} \
    --firstname ${ADMIN_FIRST:-Admin} \
    --lastname ${ADMIN_LAST:-User} \
    --email ${ADMIN_EMAIL:-admin@example.com} || true

echo "Inicializando Superset..."
superset init || true

echo "=== Iniciando servidor ==="
superset run -p ${PORT} --with-threads --reload --debugger --host 0.0.0.0
EOF

RUN chmod +x /entrypoint.sh

USER superset

EXPOSE 10000

ENTRYPOINT ["/entrypoint.sh"]