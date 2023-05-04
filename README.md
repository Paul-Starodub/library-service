# library-service
Project API service for managing and borrowing books in library.
***
# Features
- JWT authentication
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/ and /api/doc/redoc/
- Managing books and borrowing in service
- Creating user at /api/users/
- Login user at /api/users/token/
- Creating books at /api/library/books/
- Detail books info at /api/library/books/{pk}/
- Creating borrowings at /api/library/borrowings/
- Borrowings detail at api/library/borrowings/{pk}/
- Return borrowing book at api/library/borrowings/{pk}/return/
- Creating payment at /api/library/payments/
- Detail payment info at /api/library/payments/{pk}/
- Notification by Telegram Bot
- Celery task to overdue borrowing by Redis broker
- Using Flower to track the celery tasks by /0.0.0.0:5555/
- Run PR in docker
***
# Installing using GitHub
```
git clone https://github.com/Paul-Starodub/library-service
cd library-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
---
# .env file
Open file .env.sample and change environment variables to yours. Also rename file extension to .env
***
# Run on local server
- Install PostgreSQL, create DB and User
- Connect DB
- Run:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
- You can download test texture:
```
python manage.py dumpdata --indent 4 > library.json
```
***
# Run with Docker
Docker should be already installed
```
docker-compose up --build
```
***
# Create/Authenticate User
- Path to create user: api/users
- Path to login user: api/users/token
- Authorize Bearer
- docker exec -it library-service-web-1 bash 
- python manage.py createsuperuser
## Getting access
You can use following:
- superuser:
  - Email: admin@gmail.com
  - Password: 1qazcde3
- user:
  - Email: postgres@gmail.com
  - Password: 1qazcde3
## Note: Make sure to send Token in api urls in Headers as follows
```
key: Authorize
value: Bearer <token>
```
***
# Testing with docker
- docker exec -it library-service-web-1 bash
- python manage.py test
***
# Stop server
```
docker-compose down
```