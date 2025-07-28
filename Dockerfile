# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY main.py parser_utils.py requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Run the script automatically when container starts
CMD ["python", "main.py"]
