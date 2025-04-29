# Build stage
FROM python:3.9-slim as builder

# Instalar dependências de compilação
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.9-slim

# Instalar Nginx e Chrome
RUN apt-get update && apt-get install -y \
    nginx \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m appuser

# Configurar diretório de trabalho
WORKDIR /app

# Copiar ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar arquivos do projeto
COPY . .

# Copiar configurações
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/scripts/start.sh /start.sh
RUN chmod +x /start.sh

# Criar diretórios necessários e ajustar permissões
RUN mkdir -p /app/webapp/data /app/webapp/static /var/log/nginx /var/lib/nginx /var/run && \
    chown -R appuser:appuser /app /var/log/nginx /var/lib/nginx /var/run

# Mudar para usuário não-root
USER appuser

# Configurar variáveis de ambiente
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 80

# Comando de inicialização
CMD ["/start.sh"] 