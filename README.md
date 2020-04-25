# Currency exchange rate statistics

This service provides statistics on currency exchange rates, duh.

API docs are at `/docs/redoc` (http://localhost:8000/docs/redoc/ if you are
running on localhost).

## Installing and running

### `docker-compose`

```
$ docker-compose up
```

### Local

This project uses (poetry)[https://github.com/python-poetry/poetry] to manage
dependencies.  It also manages virtualenvs automatically and is generally
superior to `pip` (even though it uses it as a backend :) ).

Requires a postgres11+ instance and a redis server.

```
$ poetry install
$ poetry run python3 manage.py runserver 0.0.0.0:8000
```
