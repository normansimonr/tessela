# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=True
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . $APP_HOME

# Make the entrypoint script executable
RUN chmod +x run.sh

# Expose the port Streamlit will run on (Cloud Run provides PORT env var)
# Streamlit will bind to $PORT, FastAPI will bind to 8001 internally
EXPOSE 8080

# Run the entrypoint script
CMD ["./run.sh"]
