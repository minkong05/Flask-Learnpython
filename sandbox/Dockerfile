FROM python:3.11-slim

# Create non-root user
RUN useradd -m sandboxuser
USER sandboxuser

WORKDIR /sandbox

COPY runner.py .

# No network tools, no shell
CMD ["python", "runner.py"]