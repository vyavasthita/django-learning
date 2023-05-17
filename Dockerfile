FROM python:3.10.6-slim-buster
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y default-libmysqlclient-dev

EXPOSE 5000
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install django-mysql
RUN pip install mysqlclient

RUN apt-get autoremove -y gcc

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/

RUN chmod +x /app/docker-entrypoint.sh

# RUN [ "pip", "install", "-r", "requirements.txt" ]

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]

# CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
