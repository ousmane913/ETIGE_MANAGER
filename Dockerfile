FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend files and build
COPY frontend/package.json frontend/package-lock.json frontend/
COPY frontend/src frontend/src
COPY frontend/vite.config.ts frontend/
COPY frontend/tailwind.config.js frontend/
COPY frontend/postcss.config.js frontend/

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
