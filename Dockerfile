FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Use gunicorn to run Flask on port 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
