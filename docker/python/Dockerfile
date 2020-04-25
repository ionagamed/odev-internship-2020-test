FROM python:3.7

RUN pip3 install uwsgi

WORKDIR /app
RUN pip3 install poetry

RUN poetry config virtualenvs.create false
COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install

COPY . .

CMD python3 manage.py migrate && \
    uwsgi --ini /app/docker/python/uwsgi.ini
