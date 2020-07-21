FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY src /code/
RUN apk add mariadb-dev gcc libc-dev
RUN pip install -r requirements.txt
RUN apk del libc-dev gcc

EXPOSE 8000

ENTRYPOINT [ "gunicorn" ]
CMD [ "meertime.wsgi:application" ]
