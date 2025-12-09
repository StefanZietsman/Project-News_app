# Use an official Python runtime as a parent image.
# python:3.9-slim is a smaller-sized version of the Python 3.9 image.
# 'as builder' names this stage, which is useful in multi-stage builds.
FROM python:3.9-slim as builder

# Set the working directory to /app in the container.
WORKDIR /app

# Copy the requirements file into the container at /app.
# This is done first to leverage Docker's layer caching.
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt.
RUN pip install -r requirements.txt

# Copy the rest of the application's source code into the container at /app.
COPY . .

# Define the command to run your app. This starts the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
