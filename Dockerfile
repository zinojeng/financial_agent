# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

# Set default port if not provided
ENV PORT=8501

# Expose the port (will use $PORT from environment)
EXPOSE $PORT

# Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Health check using environment port
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health || exit 1

# Run the application using the startup script
CMD ["./start.sh"]