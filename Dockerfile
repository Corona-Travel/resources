FROM python:3.9-slim

ARG APP="app"

ENV SRC_PATH="./src/$APP"
ENV APP_PATH="./$APP"
ENV ASGI_APP="$APP.app:app"
ENV ASGI_APP_ENV=$ASGI_APP

EXPOSE 1234

WORKDIR /corona_travel

RUN apt update && apt install -y git && apt clean

RUN pip install poetry
ENV PATH /root/.local/bin:$PATH

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry config --local virtualenvs.create false
RUN poetry install

# RUN pip install fastapi uvicorn git+https://github.com/Corona-Travel/reusable_mongodb_connection.git@main

COPY $SRC_PATH $APP_PATH

CMD uvicorn --host 0.0.0.0 --port 1234 --log-level debug $ASGI_APP_ENV
