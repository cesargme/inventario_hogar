FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
