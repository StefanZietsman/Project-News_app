# Project News

A news application built with Django and Django REST Framework. This project provides a backend service for managing and delivering news articles through a RESTful API. The homepage lists published articles and newsletter titles from Publishers and Independent Journalists which an unregistered or registered Reader can view. The article/newsletter is viewed by selecting its title link. Navigation links at the bottom provide user options, and depending on their role, users will only see allowed options. Users with roles of Reader, Journalist, and Editor can be registered. Permissions have been preset for these roles. Users can reset a forgotten password to receive an email to reset it.

A Reader user can set subscriptions to receive new articles and/or newsletters by email from Publishers and/or Independent Journalists as soon as they are published. A Reader user can retrieve their subscribed articles and/or newsletters via an API endpoint on another device.

A Journalist user can create, update, delete, and view articles and/or newsletters `of only related Publisher`. Once an article and/or newsletter is created under a publisher, the publisher's editor, `related to same Publisher`, needs to approve it before the item is published. A journalist can independently publish an article/newsletter without a publisher or editor approval, and it will be marked as published by an independent journalist. In the Journalist user's homepage view, the published and "pending editor approval" marked titles are visible.

An Editor user can only update, delete, and view publisher-created articles and/or newsletters `of only related Publisher`. An Editor can view items that are published and items pending approval `of only related Publisher`. An Editor needs to select an article title to view the item and use the bottom user options to manage and approve the article and/or newsletter. Once the Editor approves and updates the item, it is published.

Once an article and/or newsletter is published, it is uploaded to X.com account.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [X.com API Configuration](#xcom-api-configuration)
- [App setup for Docker Desktop](#app-setup-for-docker-desktop)
- [API Endpoints](#api-endpoints)

## Features

- **RESTful API**: Retrieve subscribed articles and newsletters via api for readers.
- **Custom User Model**: Extends Django's default user model to include roles and other application-specific fields.
- **Admin Interface**: Django Admin is configured for easy management of app data.
- **Role-Based Permissions**: Custom permissions for Reader, Journalist, and Editor roles.
- **Email & Social Media Integration**: Automatic emails for subscriptions and posting to X.com upon publication.

## Technology Stack

- **Backend**: Python, Django
- **API**: Django REST Framework
- **Database**: MariaDB (or MySQL)

## Prerequisites

- **Python 3.9+**
- **Git**
- **MariaDB Server**: A locally installed instance of MariaDB.
- **Docker**: For the containerized setup. [Docker Desktop](https://www.docker.com/products/docker-desktop/) is recommended.

## Local Development Setup
Follow these steps to run the application on your local machine using Visual Studio Code.

1.  **Clone the Repository**
```bash
    git clone https://github.com/StefanZietsman/Project-News_app
    cd project_news
```

2.  **Create and Activate a Virtual Environment**
```bash
    python -m venv .venv
    \.venv\Scripts\activate
```

3.  **Set Up the MariaDB Database**
- Start your local MariaDB server.
- Log in to MariaDB as a root user and create the database and a dedicated user for the application.
```bash 
    CREATE DATABASE project_news_db;
    CREATE USER 'admin'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON project_news_db.* TO 'admin'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
```

4.  **Install Dependencies and Run Migrations.**
In terminal run these commands:
- Install requirements.
```bash
    pip install -r requirements.txt
```
- Collect static files
```bash
    python manage.py collectstatic
```
Type 'yes' to overwrite existing files

- Apply database migrations
```bash
    python manage.py migrate
```
- Create a Superuser
```bash
    python manage.py createsuperuser
```
Follow and complete required inputs


5.  **Run the Development Server**
- In terminal run command:
```bash
    python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000` using your web browser.

## X.com API Configuration

To enable posting articles to X.com, you need to obtain API credentials from the X Developer Portal.

1.  **Apply for a Developer Account**: Go to the X Developer Platform and apply for a developer account.
2.  **Create a Project and App**:
    - Once your account is approved, create a new Project.
    - Inside your project, create a new App.
    - During app setup, ensure you enable **"Read and Write"** permissions.
3.  **Generate Keys and Tokens**:
    - Navigate to your App's "Keys and tokens" tab.
    - Generate the **API Key** and **API Key Secret**. These correspond to `CONSUMER_KEY` and `CONSUMER_SECRET`.
4.  **Configure Environment Variables**:
    - Add the generated keys and tokens to your `.env` file as shown in the configuration sections above. The application is configured to read these keys from this file.

## App setup for Docker Desktop
- Make sure Docker Desktop is running. In Visual Studio Code terminal run docker commands:

1. **Build the image:**
```bash
    docker build -t project-news .
```

2. **Run MariaDB image in a container:**
```bash
    docker run -d
    --name mariadb-db
    --network news-network
    -v mariadb_data:/var/lib/mysql
    -e MARIADB_ROOT_PASSWORD=a_very_secret_password
    -e MARIADB_DATABASE=project_news_db
    -e MARIADB_USER=admin
    -e MARIADB_PASSWORD=password
    mariadb:latest
```

3. **Run project-news app image in another container:**
```bash
    docker run -d
    -p 8000:8000
    --name project-news_app
    --network news-network
    -e DB_HOST=mariadb-db
    project-news:latest
```

4. **In Docker Desktop, container project-news, tab Exec, run the following commands:**
- Collect static files
```bash
    python manage.py collectstatic
```
Type 'yes' to overwrite existing files

- Apply database migrations
```bash
    python manage.py migrate
```
- Create a Superuser
```bash
    python manage.py createsuperuser
```
Follow and complete required inputs

App should be running and can be found at `http://127.0.0.1:8000` using your web browser.
To get to Django administration page, go to `http://127.0.0.1:8000/admin`.

## API Endpoints

The API endpoint for a Reader to receive their subscribed articles and/or newsletters:
`GET http://127.0.0.1:8000/api/reader_view/`
Unit tests to test the third-party RESTful API done in news_app\tests_api.py file.
