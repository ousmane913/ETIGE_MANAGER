FROM python:3.11-slim

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend files and build
COPY frontend/package.json frontend/package-lock.json frontend/
COPY frontend/tsconfig.json frontend/ 2>/dev/null || true
COPY frontend/vite.config.ts frontend/ 2>/dev/null || true
COPY frontend/tailwind.config.js frontend/ 2>/dev/null || true
COPY frontend/postcss.config.js frontend/ 2>/dev/null || true
COPY frontend/src frontend/src

WORKDIR /app/frontend
RUN npm install && npm run build

WORKDIR /app

# Copy the rest of the application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
