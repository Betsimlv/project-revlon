# Dockerfile
FROM apache/superset:5.0.0

# Install pip (ensurepip) and then the DB driver(s)
USER root
RUN python -m ensurepip --upgrade || true && \
    python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir psycopg2-binary==2.9.9
# If you want gevent worker later, also add:
#    python -m pip install --no-cache-dir gevent==23.9.1
USER superset

