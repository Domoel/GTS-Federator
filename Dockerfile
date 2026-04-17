# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the image
COPY gts-federator.py .

# Create data directory
RUN mkdir -p /app/data

# Create non-root user (Standard UID 1000 is good)
RUN useradd -r -u 1000 federator

# Set ownership for the app directory
RUN chown -R federator:federator /app

# Switch to non-root user
USER federator

# Default command - now points to the new filename
CMD ["python", "gts-federator.py"]
