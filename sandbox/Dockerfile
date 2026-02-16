FROM python:3.11-slim

# Create non-root user
RUN useradd -m sandboxuser
USER sandboxuser

WORKDIR /sandbox

COPY runner.py .

CMD ["python", "runner.py"]