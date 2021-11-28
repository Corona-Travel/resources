FROM python:3.9-slim

EXPOSE 1234

WORKDIR /corona_travel

RUN apt update && apt install -y git && apt clean

RUN pip install poetry
ENV PATH /root/.local/bin:$PATH

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry config --local virtualenvs.create false
RUN poetry install

ARG SRC_PATH="./src/app"
ARG APP_PATH="./app"
ARG ASGI_APP="app:app"

ENV ASGI_APP_ENV=$ASGI_APP

# RUN pip install fastapi uvicorn git+https://github.com/Corona-Travel/reusable_mongodb_connection.git@main

COPY $SRC_PATH $APP_PATH

CMD uvicorn --host 0.0.0.0 --port 1234 --log-level debug $ASGI_APP_ENV
