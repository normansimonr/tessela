# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY src/ ./src
COPY scripts/ ./scripts
COPY prompts/ ./prompts

# The main command to run when the container starts
# It assumes that the 'data' and 'output' directories will be mounted as volumes
# and the GOOGLE_API_KEY will be passed as an environment variable.
CMD ["python", "scripts/run_normalization.py"]
