# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose ports for both FastAPI and Streamlit (though only one will be used per container)
EXPOSE 8000
EXPOSE 8501

# Create a shell script to determine which app to run
RUN echo '#!/bin/bash\n\
if [ "$APP_TYPE" = "streamlit" ]; then\n\
    echo "Starting Streamlit frontend..."\n\
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
else\n\
    echo "Starting FastAPI backend..."\n\
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000\n\
fi' > /app/run.sh && chmod +x /app/run.sh

# Default command
CMD ["/app/run.sh"]
