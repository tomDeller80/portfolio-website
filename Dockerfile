# Use a lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (build-essential needed for some C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip==26.2 \
    && pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Run with Gunicorn or direct python entry point
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
