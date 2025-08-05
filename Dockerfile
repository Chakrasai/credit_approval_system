# Use Python 3.13.3 image
FROM python:3.13-slim

# Ensure all system packages are updated to address vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*



# Upgrade pip and setuptools to latest versions
RUN pip install --upgrade pip setuptools

# Upgrade system packages to address vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=credit.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media and static directories
RUN mkdir -p /app/credit/media /app/credit/staticfiles

# Set permissions
RUN chmod +x /app/docker-entrypoint.sh || echo "No entrypoint script found, will create one"

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "credit/manage.py", "runserver", "0.0.0.0:8000"]
