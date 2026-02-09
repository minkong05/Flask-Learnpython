FROM python:3.10-slim

# Create non-root user
RUN useradd -m sandbox

# Disable dangerous Linux capabilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /sandbox
USER sandbox

# Copy ONLY sandbox code
COPY sandbox_app.py .
COPY requirements.txt .

# Install minimal deps only
RUN pip install --no-cache-dir -r requirements.txt

# Run sandbox API
CMD ["python", "sandbox_app.py"]