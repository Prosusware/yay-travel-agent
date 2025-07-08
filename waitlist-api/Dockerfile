# Start Generation Here
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY app.py .

# Expose the port that the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]