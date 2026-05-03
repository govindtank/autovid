# AutoVid Dockerfile
# Build multi-stage container for production deployment

FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/app/ ./frontend/app/

FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd autovid -u 1000 -g 1000
USER autovid

# Copy installed packages from builder
COPY --from=builder /root/.local /home/autovid/.local
COPY --from=builder /usr/local/lib/python3.11/site-packages /home/autovid/.local/lib/python3.11/site-packages

# Copy application code
COPY --chown=autovid:autovid backend/ ./backend/
COPY --chown=autovid:autovid frontend/app/ ./frontend/app/
COPY --chown=autovid:autovid config/ ./config/

# Set up virtual environment
RUN python -m venv /app/venv && \
    PATH="/app/venv/bin:$PATH"

# Create output directory
RUN mkdir -p /output && chmod 777 /output

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENAI_API_KEY=your_openai_api_key_here \
    PEXELS_API_KEY=your_pexels_api_key_here \
    NODE_ENV=production

# Switch back to root for final command
USER root

# Run API server (frontend is separate Next.js deployment)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
