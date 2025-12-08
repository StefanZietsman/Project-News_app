# Project News

A news application built with Django and Django REST Framework. This project provides a backend service for managing and delivering news articles through a RESTful API. The homepage lists published articles and newsletter titles from Publishers and Independent Journalists which an unregistered or registered Reader can view. The article/newsletter is viewed by selecting its title link. Navigation links at the bottom provide user options, and depending on their role, users will only see allowed options. Users with roles of Reader, Journalist, and Editor can be registered. Permissions have been preset for these roles. Users can reset a forgotten password to receive an email to reset it.

A Reader user can set subscriptions to receive new articles and/or newsletters by email from Publishers and/or Independent Journalists as soon as they are published. A Reader user can retrieve their subscribed articles and/or newsletters via an API endpoint on another device.

A Journalist user can create, update, delete, and view articles and/or newsletters of only related Publisher. Once an article and/or newsletter is created under a publisher, the publisher's editor, related to same Publisher, needs to approve it before the item is published. A journalist can independently publish an article/newsletter without a publisher or editor approval, and it will be marked as published by an independent journalist. In the Journalist user's homepage view, the published and "pending editor approval" marked titles are visible.

An Editor user can only update, delete, and view publisher-created articles and/or newsletters of only related Publisher. An Editor can view items that are published and items pending approval of only related Publisher. An Editor needs to select an article title to view the item and use the bottom user options to manage and approve the article and/or newsletter. Once the Editor approves and updates the item, it is published.

Once an article and/or newsletter is published, it is uploaded to X.com account.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [Running with Docker](#running-with-docker)
- [X.com API Configuration](#xcom-api-configuration)
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

- Python 3.8+
- `pip` and `virtualenv` (or any other virtual environment tool)
- MariaDB

## Setup and Installation

Follow these steps to get your development environment set up.

1.  **Copy:**
    1.  Copy the source files to your virtual environment.

2.  **Install dependencies:**
    1.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    2.  Install MariaDB from `https://mariadb.org/`.
    3.  Add the `news_app_db` database folder to your MariaDB data path (e.g., `C:\Program Files\MariaDB 12.0\data`).   

## Running with Docker

Alternatively, you can run the application using Docker and Docker Compose for a more isolated and consistent environment.

1.  **Build and run the containers:**
    Make sure you have Docker installed, then run the following command from the project root:
    ```bash
    docker-compose up --build
    ```

2.  The application will be available at `http://127.0.0.1:8000`.




## Running the Application

Start the development server with the following command:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`.
- The admin panel is at `http://127.0.0.1:8000/admin/`.

Django admin panel user:
Username: `admin`
Password: `password`

Created users for testing:
Journalist: Planetnews
Username: `john`
Password: `Password1#`

Editor: Planetnews
Username: `tom`
Password: `Password1#`

Reader with subscriptions:
Username: `sue`
Password: `Password1#`

Reader without subscriptions:
Username: `betty`
Password:`Password1#`

Journalist: Newsgalore
Username: `gill`
Password: `Password1#`

Editor: Newsgalore
Username: `dave`
Password: `Password1#`

## X.com API Configuration

To enable posting articles to X.com, you need to obtain API credentials from the X Developer Portal.

1.  **Apply for a Developer Account**: Go to the X Developer Platform and apply for a developer account.
2.  **Create a Project and App**:
    - Once your account is approved, create a new Project.
    - Inside your project, create a new App.
    - During app setup, ensure you enable **"Read and Write"** permissions.
3.  **Generate Keys and Tokens**:
    - Navigate to your App's "Keys and tokens" tab.
    - Generate the **API Key** and **API Key Secret**. These correspond to `CONSUMER_KEY` and `CONSUMER_SECRET` in
     news_app\finctions\tweet.py.
4.  **Configure Environment Variables**:
    - The application is configured to read these keys from environment variables.
    - If running locally, you can set them in your shell or use a `.env` file.


## API Endpoints

The API endpoint for Reader role to receive subscribed articles and/or newsletters:
- `GET http://127.0.0.1:8000/api/reader_view/`
