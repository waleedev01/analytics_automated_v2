# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/requirements/
COPY requirements/dev.txt /app/requirements/
RUN pip install --upgrade pip
RUN python -m pip install --upgrade "pip<24.1"
RUN pip install -r requirements/dev.txt

# Copy the project files
COPY . /app/

# Create necessary files and directories
RUN echo '{}' > analytics_automated_project/settings/base_secrets.json
RUN echo '{"USER": "test_user", "PASSWORD": "test_pass", "SECRET_KEY": "ANDKSNKJDNSJKFNJKDFJKBFDJKFDBJKDBFJKFBJKFDBJKFBDJKBFJKDBFJKDFBJKFD"}' > analytics_automated_project/settings/dev_secrets.json
RUN mkdir -p logs && touch logs/debug.log

# Expose port 8000 for Django
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
