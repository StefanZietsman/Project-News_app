# Django 6.0 requires Python 3.12 or newer.
FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Set the working directory in the container.
WORKDIR /app

# Copy just the requirements file to leverage Docker cache
COPY requirements.txt requirements.txt

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    pkg-config \    
    gcc \
    libmariadb-dev-compat

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application's source code into the container.
COPY . .

# Expose the port the app runs on.
EXPOSE 8000

# Run the Django development server. This is suitable for development but not for production.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
