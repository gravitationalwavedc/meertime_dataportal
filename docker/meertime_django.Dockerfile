FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN apk --no-cache add mariadb-dev gcc libc-dev
RUN apk del libc-dev gcc

WORKDIR /code
COPY src /code/
RUN pip --no-cache-dir install -r requirements.txt

EXPOSE 8000

CMD [ "gunicorn", "-b 0.0.0.0:8000", "meertime.wsgi:application", ]
