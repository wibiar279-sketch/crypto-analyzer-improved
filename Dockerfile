# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install gunicorn for production
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . /app/

# Make start script executable
RUN chmod +x start.sh

# Expose port (Railway will set PORT env variable)
EXPOSE ${PORT:-5000}

# Start the application
CMD ["./start.sh"]
