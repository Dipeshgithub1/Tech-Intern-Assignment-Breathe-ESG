FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt* ./ 2>/dev/null || echo "No requirements.txt"

RUN pip install django djangorestframework django-cors-headers gunicorn whitenoise 2>/dev/null || pip install django djangorestframework django-cors-headers gunicorn whitenoise

COPY backend/ .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]