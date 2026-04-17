# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /app/data

# Create non-root user
RUN useradd -r -u 1000 holmirdas

# Set ownership
RUN chown -R holmirdas:holmirdas /app

# Switch to non-root user
USER holmirdas

# Default command (will be overridden by docker-compose)
CMD ["python", "gts_holmirdas.py"]
