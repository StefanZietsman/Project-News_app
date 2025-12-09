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
- [Running with Docker](#running-with-docker)
- [Creating a Superuser](#creating-a-superuser)
- [X.com API Configuration](#xcom-api-configuration)
- [Test Users](#test-users)
- [API Endpoints](#api-endpoints)

## Features

- **RESTful API**: A complete API for CRUD (Create, Read, Update, Delete) operations on news articles and newsletters.
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
- **Docker & Docker Compose**: For the containerized setup.

## Local Development Setup

Follow these steps to run the application on your local machine.

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd project_news
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Configure Environment Variables**
    - Create a file named `.env` in the project root. This file will store your configuration and secrets.
    - Copy the contents from the `.env` example in the **Running with Docker** section into your new file.
    - **Important**: For local setup, update the database credentials in `.env` to match the user and database you create in the next step.

4.  **Set Up the MariaDB Database**
    - Start your local MariaDB server.
    - Log in to MariaDB as a root user and create the database and a dedicated user for the application.
    ```sql
    CREATE DATABASE news_app_db;
    CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'a_strong_password';
    GRANT ALL PRIVILEGES ON news_app_db.* TO 'news_user'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
    ```

5.  **Install Dependencies and Run Migrations**
    ```bash
    # Install Python packages
    pip install -r requirements.txt

    # Apply database migrations
    python manage.py migrate
    ```

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

---

## Running with Docker

You can run the entire application stack (Django and MariaDB) using Docker and Docker Compose for a more isolated and consistent environment.

1.  **Prerequisites for Docker:**
    - Make sure you have Docker and Docker Compose installed on your system.

2.  **Environment Configuration:**
    - Create a file named `.env` in the root of the project (`C:\Users\stefa\Documents\HyperionDev\project_news\.env`).
    - This file will hold your environment variables. Your `docker-compose.yml` is likely configured to use it. Add the following content, replacing placeholder values with your actual secrets.
    ```
    # Django Settings
    # Generate a new secret key for production. You can use an online generator.
    SECRET_KEY='django-insecure-your-development-secret-key'
    DEBUG=1

    # Database Credentials (for Docker)
    # The HOST should be 'db' (the service name in docker-compose.yml)
    DB_HOST=db
    MYSQL_DATABASE=news_app_db
    MYSQL_USER=news_user
    MYSQL_PASSWORD=a_strong_password
    MYSQL_ROOT_PASSWORD=a_very_strong_root_password

    # X.com API Credentials (see X.com API Configuration section)
    CONSUMER_KEY=your_x_com_api_key
    CONSUMER_SECRET=your_x_com_api_key_secret
    ACCESS_TOKEN=your_x_com_access_token
    ACCESS_TOKEN_SECRET=your_x_com_access_token_secret
    ```

3.  **Build and Run the Containers:**
    - Open a terminal in the project root and run the following command. This will build the images and start the Django and database containers in the background.
    ```bash
    docker-compose up --build -d
    ```

4.  **Run Database Migrations:**
    - After the containers have started, run the database migrations to set up the schema.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Access the Application:**
    - The application will now be available at `http://127.0.0.1:8000`.

6.  **Stopping the Containers:**
    - To stop the running containers, use:
    ```bash
    docker-compose down
    ```

## Creating a Superuser

To access the Django admin panel at `/admin/`, you need to create a superuser.

*   **For Local Development:**
    ```bash
    python manage.py createsuperuser
    ```

*   **For Docker:**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

Follow the prompts to set a username, email, and password.

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

## Test Users

The following users have been created for testing purposes. You can create them by running migrations if they are included in a data migration file, or create them manually.

**Journalist: Planetnews**
- Username: `john`
- Password: `Password1#`

**Editor: Planetnews**
- Username: `tom`
- Password: `Password1#`

**Reader with subscriptions:**
- Username: `sue`
- Password: `Password1#`

**Reader without subscriptions:**
- Username: `betty`
- Password:`Password1#`

**Journalist: Newsgalore**
- Username: `gill`
- Password: `Password1#`

**Editor: Newsgalore**
- Username: `dave`
- Password: `Password1#`

## API Endpoints

The API endpoint for a Reader to receive their subscribed articles and/or newsletters:
- `GET http://127.0.0.1:8000/api/reader_view/`
