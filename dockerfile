FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Forzar que la salida de Python sea unbuffered
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements
COPY requirements/base.txt requirements/base.txt
COPY requirements/prod.txt requirements/prod.txt

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copiar todo el proyecto
COPY . .

# Colectar archivos estáticos
RUN python manage.py collectstatic --noinput --clear || echo "Collectstatic optional"

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD python manage.py migrate && \
    gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120