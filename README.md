# WarehouseDatabase
[![Django CI](https://github.com/kehlbach/WarehouseDatabase/actions/workflows/django.yml/badge.svg)](https://github.com/kehlbach/WarehouseDatabase/actions/workflows/django.yml)

![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![Django 4.1.10](https://img.shields.io/badge/django-4.1.10-blue.svg)

This is Django REST API Database service for warehouse accounting.

This project is designed to work with [WarehouseBot](https://github.com/kehlbach/WarehouseBot).

## Running Locally

First clone and setup the virtual environment

```cmd
git clone https://github.com/kehlbach/WarehouseDatabase.git
cd WarehouseDatabase
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

By default this database is set to work with MySQL Server. Database should be created beforehand, Django won't create database.

In directory with manage.py create files .env and db1.cnf.

.env contains:

```
DEBUG=[True or False]
SECRET_KEY=[Django Secret Key]
SQLITE=[True or False]
```

You can set SQLITE to True if you want to use SQLite Database for testing purposes.

db1.cnf contains (for local MySQL Database):

```
[client]
database = [MySQL Database Name]
user = [MySQL User]
password = [MySQL Password]
default-character-set = utf8
host=localhost
port=3306
```

Migrate all models to database:

```
python manage.py migrate
```

Create user:

```
python manage.py createsuperuser
```

These name and password are used for authorization of HTTP requests, and should be specified in Warehouse Bot .env file under DB_LOGIN and DB_PASSWORD.

To run an app:

```
python manage.py runserver
```

To run tests:

```
python manage.py test
```

## Database Schema

![db_schema](https://github.com/user-attachments/assets/160bfc62-1626-4ad9-8c86-6720577abafb)
