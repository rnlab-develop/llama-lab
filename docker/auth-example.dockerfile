# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Install the google-auth package
RUN pip install --no-cache-dir google-auth requests

# Your Python script
COPY docker/scripts/script.py ./

# Run your script when the container launches
CMD ["python", "./script.py"]
