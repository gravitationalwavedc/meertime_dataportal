FROM python:3.8 as build
ENV PYTHONUNBUFFERED 0
ENV VIRTUAL_ENV /opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR ${VIRTUAL_ENV}
RUN apt-get update && apt-get install -y python-wheel
COPY src/requirements.txt requirements.txt
RUN pip install -r requirements.txt

FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV /opt/venv
COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}
RUN apt-get update && apt-get install -y libmariadb-dev
RUN mkdir /code

WORKDIR /code
COPY src /code/
RUN rm -rf /code/frontend

EXPOSE 8000

ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
CMD [ "gunicorn", "-b 0.0.0.0:8000", "meertime.wsgi:application", ]
