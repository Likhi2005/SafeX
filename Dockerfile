FROM python:3.10-slim

# Set working directory
WORKDIR /app


# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code

COPY . .

# Create models directory
RUN mkdir -p models

# Set environment variables

ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py
ENV SKIP_ML_MODELS=false

# Expose the port the app runs on
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]