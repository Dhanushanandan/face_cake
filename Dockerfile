FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Use gunicorn to serve the Flask app on port 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
