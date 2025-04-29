#!/bin/bash
set -e

# Criar diretórios necessários
mkdir -p /app/data
mkdir -p /app/static

# Ajustar permissões
chown -R appuser:appuser /app/data
chown -R appuser:appuser /app/static
chown -R appuser:appuser /var/log/nginx
chown -R appuser:appuser /var/lib/nginx
chown -R appuser:appuser /var/run

# Iniciar Nginx
echo "Iniciando Nginx..."
nginx

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile /var/log/gunicorn-access.log \
    --error-logfile /var/log/gunicorn-error.log \
    --log-level info \
    app:app 