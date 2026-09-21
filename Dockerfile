# ============================================================
# LabMS — production container
# ============================================================
FROM python:3.14-slim

# System deps: Pillow, ReportLab, and gcc for any C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
        libpng-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --shell /bin/bash labms
WORKDIR /app

# Install Python deps first (Docker cache friendliness)
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt -r requirements-prod.txt

# Copy the app
COPY . .

# Permissions
RUN chown -R labms:labms /app \
 && chmod +x /app/entrypoint.sh

USER labms

# Runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=wsgi:app \
    PORT=8000 \
    GUNICORN_WORKERS=4

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
