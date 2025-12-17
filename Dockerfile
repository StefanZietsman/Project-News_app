# Use an official Python runtime as a parent image.
# python:3.9-slim is a smaller-sized version of the Python 3.9 image.
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN python manage.py migrate

# Copy the rest of your application's source code into the container.
COPY . .

# Expose the port the app runs on.
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
