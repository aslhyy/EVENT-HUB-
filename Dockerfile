FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias del sistema para MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar los requirements
COPY requirements/base.txt requirements/base.txt
COPY requirements/prod.txt requirements/prod.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copiar todo el proyecto
COPY . .

# No ejecutar collectstatic aquí (Railway no tiene envs disponibles en build)
# Se hace en CMD

EXPOSE 8000

CMD \
    echo "▶ Applying migrations..." && \
    python manage.py migrate && \
    echo "▶ Collecting static files..." && \
    python manage.py collectstatic --noinput --clear && \
    echo "▶ Starting Gunicorn..." && \
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:${PORT:-8000} \
        --workers 4 \
        --timeout 120
